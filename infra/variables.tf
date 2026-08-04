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
  default     = "99.72.205.93/32"
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
  description = "EC2 instance type. t3.small rather than t3.micro (the guide's suggestion) — deliberate: docker compose up --build runs a full Vite/npm build on the instance itself (Phase 8's pre-built-image pipeline doesn't exist yet), and t3.micro's 1GB RAM is genuinely tight for that."
  type        = string
  default     = "t3.small"
}
