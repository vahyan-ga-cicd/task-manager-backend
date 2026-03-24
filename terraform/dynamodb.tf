resource "aws_dynamodb_table" "task_users" {

  name         = "Task_Users"
  billing_mode = "PAY_PER_REQUEST"

  # Table Primary Key (Partition Key)
  # NOTE: Using hash_key because key_schema block was rejected by the provider version.
  hash_key = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  # GSI for searching by email
  global_secondary_index {
    name            = "email-index"
    key_schema {
      attribute_name = "email"
      key_type       = "HASH"
    }
    projection_type = "ALL"
  }

  tags = {
    Project = "TaskManager"
  }

  # Prevent accidental deletion (VERY IMPORTANT)
  lifecycle {
    prevent_destroy = true
  }
}



resource "aws_dynamodb_table" "tasks" {

  name         = "Tasks"
  billing_mode = "PAY_PER_REQUEST"

  # Composite Primary Key
  # NOTE: Using hash_key/range_key due to provider rejection of key_schema block.
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

  tags = {
    Project = "TaskManager"
  }

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
}