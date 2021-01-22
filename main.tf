terraform {
  backend "s3" {
    bucket = "strateos-data-ingest-infrastructure"
    key    = "data-science"
    region = var.region
  }
}

provider "aws" {
  region              = var.region
  allowed_account_ids = [""]
}

// The S3 bucket for initial data source ingest.
resource "aws_s3_bucket" "ingest_bucket" {
  bucket = "${var.customer}-${var.workspace}-ingest-bucket"
  acl    = "private"

  versioning {
    enabled = true
  }
}

// The primary SNS Topic triggered by new data ingest.
resource "aws_sns_topic" "new_ingest_topic" {
  name = "${var.customer}-${var.workspace}-s3-new-data-ingest-topic"

  policy = data.aws_iam_policy_document.sns_s3_notification_policy.json
}

