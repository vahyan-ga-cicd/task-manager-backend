resource "aws_iam_role" "lambda_role" {

  name = "task_manager_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "lambda.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {

  role = aws_iam_role.lambda_role.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {
        Effect = "Allow"

        Action = [
          "logs:*"
        ]

        Resource = "*"
      },

      {
        Effect = "Allow"

        Action = [
          "dynamodb:*"
        ]

        Resource = "*"
      }

    ]
  })
}