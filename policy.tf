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