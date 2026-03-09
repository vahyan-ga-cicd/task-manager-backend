resource "aws_apigatewayv2_api" "api" {

  name          = "task-manager-api"
  protocol_type = "HTTP"
}


resource "aws_apigatewayv2_integration" "lambda" {

  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.backend.invoke_arn
  payload_format_version = "2.0"
}


resource "aws_apigatewayv2_route" "route" {

  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}