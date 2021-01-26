data "aws_iam_policy_document" "lambda-assume-role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole"
    ]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }

  statement {
    effect = "Allow"

    actions = [
      "execute-api:Invoke"
    ]

    resources = []
  }
}

data "aws_iam_policy_document" "allow_lambda_get_objects" {
  statement {
    sid    = ""
    effect = "Allow"

    actions = [
      //      "s3:GetObject",
      "s3:*"
    ]

    resources = [
      "arn:aws:s3:::${var.customer}-${local.workspace}-ingest-bucket/*"
    ]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type = "Service"
    }
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_lambda_assume"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "iam_lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_from_api" {
  policy = data.aws_iam_policy_document.lambda_from_api.json
}

data "aws_iam_policy_document" "lambda_from_api" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      aws_lambda_function.get-data-type-lambda.arn
    ]

    condition {
      test = "ArnLike"
      values = ["arn:aws:execute-api:us-west-2:722041473403:vad0ls6yx4/*/*/get_data_upload_type_lambda"]
      variable = "aws:SourceArn"
    }
  }
}