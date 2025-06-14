resource "aws_cloudwatch_log_group" "predict_api_kinesis" {
  name              = "/aws/kinesis/predict-api"
  retention_in_days = 365
}

resource "aws_cloudwatch_log_stream" "predict_api_kinesis" {
  name           = "mlops-predict-api-kinesis-log-stream"
  log_group_name = aws_cloudwatch_log_group.predict_api_kinesis.name
}


resource "aws_kinesis_firehose_delivery_stream" "firelens" {
  name        = "mlops-predict-api-kinesis-firehose"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn           = aws_iam_role.kinesis.arn
    bucket_arn         = aws_s3_bucket.predict_api.arn
    buffering_size     = 64
    buffering_interval = 10
    prefix             = "predict_log/"

    cloudwatch_logging_options {
      enabled         = "true"
      log_group_name  = aws_cloudwatch_log_group.predict_api_kinesis.name
      log_stream_name = aws_cloudwatch_log_stream.predict_api_kinesis.name
    }
  }
}

