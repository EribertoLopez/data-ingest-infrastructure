data "aws_iam_policy_document" "sns_s3_notification_policy" {
  statement {
    effect = "Allow"

    actions = []

    resources = [aws_sns_topic.new_ingest_topic.arn]

    principals {
      identifiers = ["sns.amazonaws.com"]
      type        = "Service"
    }

    condition {
      test = "ArnLike"
      values = [aws_sns_topic.new_ingest_topic.arn]
      variable = "aws:SourceArn"
    }
  }
}