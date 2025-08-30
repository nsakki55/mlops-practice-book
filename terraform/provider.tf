terraform {
  required_version = ">= 1.9, < 2.0"
  backend "s3" {
    bucket = "<your-tfstate-bucket-name>" # 作成したS3バケット名を設定する
    key    = "terraform.tfstate"
    region = "ap-northeast-1"

  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
  default_tags {
    tags = {
      Name = "mlops-practice"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
  aws_region     = data.aws_region.current.name
}
