terraform {
  backend "s3" {
    bucket         = "autoassist-terraform-state-224603709350"
    key            = "autoassist/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "autoassist-terraform-locks"
    encrypt        = true
  }
}
