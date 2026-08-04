#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y docker postgresql16

systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# IMDSv2 - determine this instance's own public IP so the app's
# FRONTEND_BASE_URL/BACKEND_BASE_URL are correct without knowing the IP in advance
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)

mkdir -p /opt/autoassist/backend
cd /opt/autoassist

# Pull the deploy config (docker-compose.prod.yml + seed.sql) from S3 - just
# the config, not the app source, since images now come pre-built from ECR.
aws s3 cp s3://${deploy_bucket}/deploy/docker-compose.prod.yml . --region ${aws_region}
aws s3 cp s3://${deploy_bucket}/deploy/seed.sql . --region ${aws_region}

# Authenticate to ECR using the instance role (no static keys) and pull.
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_registry}

cat > backend/.env <<ENVEOF
DATABASE_URL=postgresql://postgres:${db_password}@${rds_endpoint}/autoassist
JWT_SECRET_KEY=${jwt_secret_key}
SES_SENDER_EMAIL=${ses_sender_email}
AWS_REGION=${aws_region}
S3_BUCKET_NAME=${s3_bucket_name}
FRONTEND_BASE_URL=http://$PUBLIC_IP
BACKEND_BASE_URL=http://$PUBLIC_IP
ENVEOF

# Compose's own variable substitution file (distinct from backend/.env above,
# which is the Python app's config) - docker compose auto-loads a .env
# alongside the compose file for variable substitution inside it.
cat > .env <<COMPOSEENVEOF
ECR_BACKEND_IMAGE=${ecr_backend_image}
ECR_FRONTEND_IMAGE=${ecr_frontend_image}
COMPOSEENVEOF

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
