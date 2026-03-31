resource "aws_lambda_function" "backend" {

  function_name = "task-manager"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.repo.repository_url}:latest"

  role    = aws_iam_role.lambda_role.arn
  timeout = 30

  depends_on = [
    aws_iam_role_policy_attachment.lambda_vpc_access
  ]

  vpc_config {
    subnet_ids         = data.aws_subnets.default.ids
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  environment {
    variables = {
      JWT_SECRET      = var.jwt_secret
      PASS_SECRET_KEY = var.pass_secret_key
      USERS_TABLE     = var.users_table
      TASKS_TABLE     = var.tasks_table
      AUDIT_LOGS_TABLE= var.audit_logs_table
      ENVIRONMENT     = var.environment
    }
  }
}