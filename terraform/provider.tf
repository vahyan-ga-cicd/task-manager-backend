provider "aws" {
  region = "ap-south-1"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket = "task-manager-state"
    key    = "backend/terraform.tfstate"
    region = "ap-south-1"
  }
}