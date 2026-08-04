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
