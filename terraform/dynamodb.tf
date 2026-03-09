resource "aws_dynamodb_table" "users" {

  name         = "Users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }
}


resource "aws_dynamodb_table" "tasks" {

  name         = "Tasks"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "user_id"
  range_key = "task_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "task_id"
    type = "S"
  }
}