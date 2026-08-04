output "rds_endpoint" {
  description = "RDS connection endpoint (host:port) — not publicly reachable, only from within the VPC"
  value       = aws_db_instance.main.endpoint
}

output "app_public_ip" {
  description = "Public IP of the deployed app. Frontend at http://<this>, backend API at http://<this>:8000"
  value       = aws_instance.app.public_ip
}
