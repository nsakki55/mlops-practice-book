resource "aws_s3_bucket" "model" {
  bucket_prefix = "mlops-model-"

  tags = {
    Name = "mlops-model-bucket"
  }
}

resource "aws_s3_bucket" "data" {
  bucket_prefix = "mlops-data-"

  tags = {
    Name = "mlops-data-bucket"
  }
}

resource "aws_s3_bucket" "feature_store" {
  bucket_prefix = "mlops-feature-store-"

  tags = {
    Name = "mlops-feature-store-bucket"
  }
}

resource "aws_s3_bucket" "athena" {
  bucket_prefix = "mlops-athena-"

  tags = {
    Name = "mlops-athena-bucket"
  }
}

resource "aws_s3_bucket" "predict_api" {
  bucket_prefix = "mlops-predict-api-"

  tags = {
    Name = "mlops-predict-api-bucket"
  }
}

resource "aws_s3_bucket" "athena_output" {
  bucket_prefix = "mlops-athena-output-"

  tags = {
    Name = "mlops-athena-output-bucket"
  }
}
