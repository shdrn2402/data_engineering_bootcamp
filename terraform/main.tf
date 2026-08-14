terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "eu-central-1"
}

# Create an S3 bucket for the data landing zone
resource "aws_s3_bucket" "data_landing_zone" {
  bucket        = "data-eng-bootcamp-api-football-landing-dev"
  force_destroy = true
}

# Create a public access block for the S3 bucket
resource "aws_s3_bucket_public_access_block" "data_landing_zone_access_block" {
  bucket = aws_s3_bucket.data_landing_zone.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
