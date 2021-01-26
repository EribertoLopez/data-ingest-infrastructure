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

// Attach logging policy to lambdas.
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "lambda_from_api" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_from_api.arn
}

// S3 bucket to hold all data-ingest lambda .zip files.
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

// Permission for s3 to execute forwarding lambda.
resource "aws_lambda_permission" "allow_bucket" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.forward_s3_create_data_object.arn
  principal = "s3.amazonaws.com"
  source_arn = aws_s3_bucket.ingest_bucket.arn
}

// The forwarding lambda triggered by new data ingest.
data "aws_s3_bucket_object" "forward_create_object_lambda" {
  bucket = aws_s3_bucket.data_ingest_lambda_bucket.bucket
  key    = "forward_s3_data_object.zip"
}

resource "aws_lambda_function" "forward_s3_create_data_object" {
  s3_bucket         = aws_s3_bucket.data_ingest_lambda_bucket.bucket
  s3_key            = "forward_s3_data_object.zip"
  function_name     = "forward_s3_data_object_lambda"
  role              = aws_iam_role.iam_for_lambda.arn
  handler           = "forward_s3_data_object.handler"
  runtime           = "python3.8"
  s3_object_version = data.aws_s3_bucket_object.forward_create_object_lambda.version_id
}

// Execute the forwarding lambda on S3 CreateObject

resource "aws_s3_bucket_notification" "forward_s3_create_data_object" {
  bucket = aws_s3_bucket.ingest_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.forward_s3_create_data_object.arn
    events = ["s3:ObjectCreated:*"]
  }
}

// API Gateway
resource "aws_apigatewayv2_api" "data_ingest_gateway" {
  name          = "${var.customer}-${local.workspace}-data-ingest-gateway"
  protocol_type = "HTTP"
}

// Gateway stage
resource "aws_apigatewayv2_stage" "dev" {
  api_id = aws_apigatewayv2_api.data_ingest_gateway.id
  name = "strateos-data-ingest-dev-ingest-stage"
}

// Gateway logs
resource "aws_cloudwatch_log_group" "gateway_logs" {
  name = "${var.customer}-${local.workspace}-gateway-logs"

  tags = {
    Environment = local.workspace
    Application = var.appname
  }
}

// Endpoint for get_data_type
resource "aws_apigatewayv2_route" "test_route" {
  api_id    = aws_apigatewayv2_api.data_ingest_gateway.id
  route_key = "GET /test-route"
  target    = "integrations/${aws_apigatewayv2_integration.gateway-get-data-type-integration.id}"
}

resource "aws_apigatewayv2_route" "data_type" {
  api_id    = aws_apigatewayv2_api.data_ingest_gateway.id
  route_key = "POST /data-upload-type"
  target    = "integrations/${aws_apigatewayv2_integration.gateway-get-data-type-integration.id}"
}

resource "aws_apigatewayv2_integration" "gateway-get-data-type-integration" {
  api_id           = aws_apigatewayv2_api.data_ingest_gateway.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "Lambda get-data-type"
  integration_method   = "POST"
  integration_uri      = aws_lambda_function.get-data-type-lambda.arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

// Lambda to get data type
data "aws_s3_bucket_object" "get_data_type_lambda" {
  bucket = aws_s3_bucket.data_ingest_lambda_bucket.bucket
  key    = "get_data_upload_type.zip"
}

resource "aws_lambda_function" "get-data-type-lambda" {
  s3_bucket         = aws_s3_bucket.data_ingest_lambda_bucket.bucket
  s3_key            = "get_data_upload_type.zip"
  function_name     = "get_data_upload_type_lambda"
  role              = aws_iam_role.iam_for_lambda.arn
  handler           = "get_data_upload_type.handler"
  runtime           = "python3.8"
  s3_object_version = data.aws_s3_bucket_object.get_data_type_lambda.version_id
}

// Enqueue process_txt_data

// Lambda write to s3 transformed json blob

// Lambda write to postgres DB



// Local variables (main.tf).
locals {
  workspace = terraform.workspace
}