resource "aws_athena_workgroup" "mlops" {
  name = "mlops"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_output.bucket}/output/"
    }
  }
}
