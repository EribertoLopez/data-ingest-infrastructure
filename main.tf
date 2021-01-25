terraform {
  backend "s3" {
    bucket = "strateos-data-ingest-infrastructure"
    key    = "data-science"
    region = "us-west-2"
  }
}

provider "aws" {
  region              = var.region
  allowed_account_ids = ["722041473403"]
}

//
resource "aws_s3_bucket" "data_ingest_lambda_bucket" {
  bucket = "${var.customer}-${local.workspace}-lambda-bucket"
  //  acl    = "private"

  versioning {
    enabled = true
  }
}

// The S3 bucket for initial data source ingest.
resource "aws_s3_bucket" "ingest_bucket" {
  bucket = "${var.customer}-${local.workspace}-ingest-bucket"
  //  acl    = "private"

  versioning {
    enabled = true
  }
}

// Allow lambdas to get objects from the ingest_bucket.
resource "aws_s3_bucket_policy" "allow_lambda_get_objects" {
  bucket = aws_s3_bucket.ingest_bucket.id
  policy = data.aws_iam_policy_document.allow_lambda_get_objects.json
}

// The primary SQS Queue triggered by new data ingest.
resource "aws_sqs_queue" "new_ingest_queue" {
  name = "${var.customer}-${local.workspace}-s3-new-data-ingest-queue"

  //  policy = data.aws_iam_policy_document.sqs_s3_notification_policy.json
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:*:*:${var.customer}-${local.workspace}-s3-new-data-ingest-queue",
      "Condition": {
        "ArnEquals": { "aws:SourceArn": "${aws_s3_bucket.ingest_bucket.arn}" }
      }
    }
  ]
}
POLICY

}

// Trigger an SQS enqueue when S3 bucket ObjectCreated
resource "aws_s3_bucket_notification" "new_ingest_notification" {
  bucket = aws_s3_bucket.ingest_bucket.id

  queue {
    events    = ["s3:ObjectCreated:*"]
    queue_arn = aws_sqs_queue.new_ingest_queue.arn
  }
}

// API Gateway

resource "aws_apigatewayv2_api" "data_ingest_gateway" {
  name          = "${var.customer}-${local.workspace}-data-ingest-gateway"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_route" "data_type" {
  api_id    = aws_apigatewayv2_api.data_ingest_gateway.id
  route_key = "POST /data_type"
}

resource "aws_apigatewayv2_stage" "ingest-stage" {
  api_id = aws_apigatewayv2_api.data_ingest_gateway.id
  name   = "${var.customer}-${local.workspace}-ingest-stage"
}

resource "aws_apigatewayv2_integration" "gateway-get-data-type-integration" {
  api_id           = aws_apigatewayv2_api.data_ingest_gateway.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  description               = "Lambda get-data-type"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.get-data-type-lambda.arn
  passthrough_behavior      = "WHEN_NO_MATCH"
}

// Lambda to get data type



resource "aws_lambda_function" "get-data-type-lambda" {
  s3_bucket         = aws_s3_bucket.data_ingest_lambda_bucket.bucket
  s3_key            = "get_data_upload_type.zip"
  function_name     = "get_data_upload_lambda"
  role              = aws_iam_role.iam_for_lambda.arn
  handler           = "get_data_upload_type.handler"
  runtime           = "python3.8"
  s3_object_version = data.aws_s3_bucket_object.pherastar_lambda_zip.version_id
}

data "aws_s3_bucket_object" "pherastar_lambda_zip" {
  bucket = aws_s3_bucket.data_ingest_lambda_bucket.bucket
  key    = "get_data_upload_type.zip"
}
// Kinesis stream? Or SQS

// Lambda get_data_type

// Enqueue process_txt_data

// Lambda write to s3 transformed json blob

// Lambda write to postgres DB



// Local variables (main.tf).
locals {
  workspace = terraform.workspace
}