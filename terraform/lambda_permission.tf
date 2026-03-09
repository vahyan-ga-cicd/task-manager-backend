resource "aws_lambda_permission" "apigateway" {

  statement_id  = "AllowAPIGatewayInvoke"

  action = "lambda:InvokeFunction"

  function_name = aws_lambda_function.backend.function_name

  principal = "apigateway.amazonaws.com"
}