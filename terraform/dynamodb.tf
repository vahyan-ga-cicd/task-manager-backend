resource "aws_dynamodb_table" "task_users" {

  name         = "Task_Users"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  global_secondary_index {
    name            = "email-index"
    hash_key        = "email"
    projection_type = "ALL"
  }

  tags = {
    Project = "TaskManager"
  }
  lifecycle {
    prevent_destroy = false
    ignore_changes = all
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
  lifecycle {
    prevent_destroy = false
    ignore_changes = all

  }
  tags = {
    Project = "TaskManager"
  }
}