variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "billing_alert_email" {
  description = "Email address to receive billing alarm notifications"
  type        = string
  default     = "muneera0615@gmail.com"
}

variable "my_ip_cidr" {
  description = "Muneera's public IP (as a /32 CIDR), for scoping SSH access. Update this if working from a different network — check with `curl https://checkip.amazonaws.com`."
  type        = string
  default     = "129.110.242.97/32"
}

variable "db_password" {
  description = "Master password for the RDS Postgres instance. Passed via TF_VAR_db_password at apply time — never given a default, never committed to a tfvars file."
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT signing secret for the deployed backend (separate from the local-dev one). Passed via TF_VAR_jwt_secret_key at apply time."
  type        = string
  sensitive   = true
}

variable "ses_sender_email" {
  description = "Verified SES sender identity"
  type        = string
  default     = "muneera0615@gmail.com"
}

variable "s3_receipts_bucket" {
  description = "S3 bucket for receipt uploads and the deployment artifact"
  type        = string
  default     = "autoassist-receipts-224603709350"
}

variable "instance_type" {
  description = "EC2 instance type. As of Phase 8, the instance pulls pre-built images from ECR rather than building locally, so t3.micro would work again — left at t3.small for now since it's already the proven-working size and the cost difference is small."
  type        = string
  default     = "t3.small"
}

variable "ecr_backend_repository_url" {
  description = "ECR repository URL for the backend image (created in infra/bootstrap)"
  type        = string
  default     = "224603709350.dkr.ecr.us-east-1.amazonaws.com/autoassist-backend"
}

variable "ecr_frontend_repository_url" {
  description = "ECR repository URL for the frontend image (created in infra/bootstrap)"
  type        = string
  default     = "224603709350.dkr.ecr.us-east-1.amazonaws.com/autoassist-frontend"
}
