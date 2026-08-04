terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- Billing alarm ---------------------------------------------------------
# Applied first, before any resource that actually spends money (EC2, RDS).
# AWS/Billing metrics are only published in us-east-1, which is why this
# works here without any special provider aliasing — the whole project runs
# in us-east-1 anyway.
#
# Prerequisite that Terraform can't set on its own: "Receive Billing Alerts"
# must be enabled in the account's Billing preferences console, or no
# EstimatedCharges datapoints ever get published and this alarm just sits in
# INSUFFICIENT_DATA forever.

resource "aws_sns_topic" "billing_alerts" {
  name = "autoassist-billing-alerts"
}

resource "aws_sns_topic_subscription" "billing_alerts_email" {
  topic_arn = aws_sns_topic.billing_alerts.arn
  protocol  = "email"
  endpoint  = var.billing_alert_email
}

resource "aws_cloudwatch_metric_alarm" "billing_10" {
  alarm_name          = "autoassist-billing-over-10-usd"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600 # billing metrics update a few times a day, not continuously
  statistic           = "Maximum"
  threshold           = 10
  alarm_description   = "Estimated AWS charges have exceeded $10"

  dimensions = {
    Currency = "USD"
  }

  alarm_actions = [aws_sns_topic.billing_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "billing_50" {
  alarm_name          = "autoassist-billing-over-50-usd"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = 50
  alarm_description   = "Estimated AWS charges have exceeded $50"

  dimensions = {
    Currency = "USD"
  }

  alarm_actions = [aws_sns_topic.billing_alerts.arn]
}
