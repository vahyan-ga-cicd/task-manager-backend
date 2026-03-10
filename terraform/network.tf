# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Get all subnets in default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security group for Lambda
resource "aws_security_group" "lambda_sg" {
  name        = "lambda-sg"
  description = "Allow Lambda outbound"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security group for Redis
resource "aws_security_group" "redis_sg" {
  name   = "redis-sg"
  vpc_id = data.aws_vpc.default.id
}

# Allow Lambda to access Redis
resource "aws_security_group_rule" "redis_lambda" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  security_group_id        = aws_security_group.redis_sg.id
  source_security_group_id = aws_security_group.lambda_sg.id
}

resource "aws_vpc_endpoint" "dynamodb" {

  vpc_id            = data.aws_vpc.default.id
  service_name      = "com.amazonaws.ap-south-1.dynamodb"
  vpc_endpoint_type = "Gateway"

  route_table_ids = data.aws_route_tables.default.ids
}

data "aws_route_tables" "default" {
  vpc_id = data.aws_vpc.default.id
}