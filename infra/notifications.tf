data "archive_file" "lambda_reminders" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_reminders"
  output_path = "${path.module}/lambda_reminders.zip"
}

resource "aws_iam_role" "lambda_reminders" {
  name = "autoassist-lambda-reminders-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_reminders_basic" {
  role       = aws_iam_role.lambda_reminders.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_reminders" {
  name = "autoassist-lambda-reminders-policy"
  role = aws_iam_role.lambda_reminders.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ses:SendEmail", "ses:SendRawEmail"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["ssm:GetParameter"]
        Resource = "arn:aws:ssm:${var.aws_region}:224603709350:parameter${var.backend_url_param}"
      }
    ]
  })
}

resource "aws_lambda_function" "reminders" {
  function_name = "autoassist-reminders"
  role          = aws_iam_role.lambda_reminders.arn
  handler       = "handler.handler"
  runtime       = "python3.13"
  timeout       = 30

  filename         = data.archive_file.lambda_reminders.output_path
  source_code_hash = data.archive_file.lambda_reminders.output_base64sha256

  environment {
    variables = {
      BACKEND_URL_PARAM = var.backend_url_param
      INTERNAL_API_KEY  = var.internal_api_key
      SES_SENDER_EMAIL  = var.ses_sender_email
      # AWS_REGION is a reserved Lambda env var name, auto-populated by the
      # runtime - setting it explicitly here would error on apply. handler.py
      # reads it as a plain os.environ lookup and it's already correct.
    }
  }
}

# --- Daily schedule ----------------------------------------------------------

resource "aws_cloudwatch_event_rule" "reminders_daily" {
  name                = "autoassist-reminders-daily"
  description         = "Trigger the maintenance reminders Lambda once a day"
  schedule_expression = "cron(0 13 * * ? *)" # 8am US Eastern (UTC-5); adjust if needed
}

resource "aws_cloudwatch_event_target" "reminders_daily" {
  rule = aws_cloudwatch_event_rule.reminders_daily.name
  arn  = aws_lambda_function.reminders.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reminders.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.reminders_daily.arn
}
