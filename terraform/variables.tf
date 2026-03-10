variable "jwt_secret" {
  type = string
}

variable "redis_port" {
  type = string
}

variable "users_table" {
  type = string
}

variable "tasks_table" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "environment" {
  type    = string
  default = "production"
}