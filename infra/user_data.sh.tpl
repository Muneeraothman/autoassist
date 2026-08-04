#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y docker git tar

systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# docker compose build (as of recent Compose versions) requires buildx
# 0.17.0+, and Amazon Linux 2023's docker package doesn't ship it. Hit and
# fixed live during first deploy - without this, "docker compose build"
# fails outright with "compose build requires buildx 0.17.0 or later".
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep tag_name | cut -d'"' -f4)
curl -SL "https://github.com/docker/buildx/releases/latest/download/buildx-$BUILDX_VERSION.linux-amd64" \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx

# IMDSv2 - determine this instance's own public IP so the app's
# FRONTEND_BASE_URL/BACKEND_BASE_URL are correct without knowing the IP in advance
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)

mkdir -p /opt/autoassist
cd /opt/autoassist
aws s3 cp s3://${deploy_bucket}/deploy/autoassist-deploy.tar.gz . --region ${aws_region}
tar -xzf autoassist-deploy.tar.gz
rm autoassist-deploy.tar.gz

cat > backend/.env <<ENVEOF
DATABASE_URL=postgresql://postgres:${db_password}@${rds_endpoint}/autoassist
JWT_SECRET_KEY=${jwt_secret_key}
SES_SENDER_EMAIL=${ses_sender_email}
AWS_REGION=${aws_region}
S3_BUCKET_NAME=${s3_bucket_name}
FRONTEND_BASE_URL=http://$PUBLIC_IP
BACKEND_BASE_URL=http://$PUBLIC_IP
ENVEOF

docker compose -f docker-compose.prod.yml up --build -d
