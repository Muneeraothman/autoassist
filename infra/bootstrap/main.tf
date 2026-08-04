# Persistent infrastructure — created once, NOT part of the destroy-between-
# sessions compute cycle in the main infra/ project. Two kinds of things
# live here, both for the same reason: they need to survive a
# `terraform destroy` of the compute resources.
#
# 1. The S3 bucket + DynamoDB lock table the main infra/ project uses as its
#    remote state backend. This module itself uses local state (the classic
#    chicken-and-egg problem — you can't store Terraform's state in a bucket
#    that doesn't exist yet).
# 2. As of Phase 8: the ECR repositories CI pushes images to, and the GitHub
#    Actions OIDC trust relationship. If these lived in the destroyable
#    infra/ project, every `terraform destroy` would wipe the built images
#    and the CI/CD auth setup along with the EC2/RDS teardown — exactly the
#    kind of thing that should persist across sessions even though compute
#    doesn't.
#
# Run this once (or when adding new persistent resources like this);
# infra/ is what you actually work in day to day.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "autoassist-terraform-state-224603709350"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "autoassist-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

# --- ECR (Phase 8) ------------------------------------------------------

resource "aws_ecr_repository" "backend" {
  name                 = "autoassist-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "frontend" {
  name                 = "autoassist-frontend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images after 7 days"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 7
      }
      action = { type = "expire" }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "frontend" {
  repository = aws_ecr_repository.frontend.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expire untagged images after 7 days"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 7
      }
      action = { type = "expire" }
    }]
  })
}

# --- GitHub Actions OIDC federation (Phase 8) -----------------------------
# GitHub Actions authenticates by assuming this role via a short-lived OIDC
# token — no static AWS access keys stored in GitHub Secrets at all. Same
# "avoid static credentials where a role will do" pattern as the EC2
# instance role.

data "tls_certificate" "github_actions" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  # AWS needs the ROOT CA's thumbprint, not the leaf (server) cert -
  # certificates[0] is the leaf; the last entry in the chain is the root.
  # Got this wrong on the first pass (used [0]) and hit
  # "Not authorized to perform sts:AssumeRoleWithWebIdentity" in CD as a
  # result - the trust policy's `sub` condition was correct, the OIDC
  # provider's thumbprint just didn't match anything real.
  thumbprint_list = [data.tls_certificate.github_actions.certificates[length(data.tls_certificate.github_actions.certificates) - 1].sha1_fingerprint]
}

resource "aws_iam_role" "github_actions_deploy" {
  name = "autoassist-github-actions-deploy"

  # Restricted to the main branch specifically — PR builds from branches or
  # forks never get AWS credentials, only a merge to main can assume this.
  #
  # The `sub` claim's actual format was a real surprise: GitHub embeds the
  # owner's and repo's immutable numeric IDs alongside their names -
  # "repo:Muneeraothman@307808101/autoassist@1308257599:ref:refs/heads/main"
  # - not the simpler "repo:owner/repo:ref:refs/heads/branch" format most
  # OIDC setup guides show (that was apparently an older format). Found this
  # by adding a temporary debug step to cd.yml that decoded the actual JWT
  # rather than guessing further after the thumbprint fix alone didn't
  # resolve "Not authorized to perform sts:AssumeRoleWithWebIdentity".
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Federated = aws_iam_openid_connect_provider.github_actions.arn }
        Action    = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:Muneeraothman@*/autoassist@*:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "github_actions_ecr" {
  name = "autoassist-github-actions-ecr-policy"
  role = aws_iam_role.github_actions_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchGetImage",
        ]
        Resource = [
          aws_ecr_repository.backend.arn,
          aws_ecr_repository.frontend.arn,
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "github_actions_ssm" {
  name = "autoassist-github-actions-ssm-policy"
  role = aws_iam_role.github_actions_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["ssm:SendCommand"]
        # Scoped by tag, not instance ID — the instance ID changes every
        # destroy/apply cycle, but the Name tag stays constant.
        Resource = "arn:aws:ec2:us-east-1:${data.aws_caller_identity.current.account_id}:instance/*"
        Condition = {
          StringEquals = {
            "ssm:resourceTag/Name" = "autoassist-app"
          }
        }
      },
      {
        Effect   = "Allow"
        Action   = ["ssm:SendCommand"]
        Resource = "arn:aws:ssm:us-east-1::document/AWS-RunShellScript"
      },
      {
        Effect   = "Allow"
        Action   = ["ssm:GetCommandInvocation", "ssm:ListCommandInvocations"]
        Resource = "*"
      }
    ]
  })
}

output "state_bucket_name" {
  value = aws_s3_bucket.terraform_state.id
}

output "lock_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}

output "ecr_backend_repository_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_repository_url" {
  value = aws_ecr_repository.frontend.repository_url
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions_deploy.arn
}
