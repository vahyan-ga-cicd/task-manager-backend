provider "aws" {
  region = "ap-south-1"
}

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "task-manager-state"
    key    = "backend/terraform.tfstate"
    region = "ap-south-1"
  }
}