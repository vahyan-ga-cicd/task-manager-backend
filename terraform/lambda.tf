resource "aws_lambda_function" "backend" {

  function_name = "task-manager"

  package_type = "Image"

  image_uri = "${aws_ecr_repository.repo.repository_url}:latest"

  role = aws_iam_role.lambda_role.arn

  timeout = 30

  lifecycle {
    ignore_changes = [image_uri]
  }

    vpc_config {
    subnet_ids = [
      aws_subnet.private1.id,
      aws_subnet.private2.id
    ]

    security_group_ids = [
      aws_security_group.lambda_sg.id
    ]
  }

  environment {
    variables = {
      JWT_SECRET  = var.jwt_secret
      REDIS_HOST  = var.redis_host
      REDIS_PORT  = var.redis_port
      USERS_TABLE = var.users_table
      TASKS_TABLE = var.tasks_table
    }
  }
}