resource "aws_glue_catalog_database" "mlops" {
  name         = "mlops_db"
  location_uri = "s3a://${aws_s3_bucket.data.bucket}/train/"
}

resource "aws_glue_crawler" "mlops" {
  database_name = aws_glue_catalog_database.mlops.name
  name          = "mlops_train_data_crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data.bucket}/train"
  }
}

resource "aws_glue_crawler" "mlops_predict_log" {
  database_name = aws_glue_catalog_database.mlops.name
  name          = "mlops_predict_log_crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${aws_s3_bucket.predict_api.bucket}/predict_log"
  }
}

resource "aws_glue_crawler" "mlops_train_log" {
  database_name = aws_glue_catalog_database.mlops.name
  name          = "mlops_train_log_crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${aws_s3_bucket.model.bucket}/train_log"
  }
}

resource "aws_glue_crawler" "mlops_feature_store" {
  database_name = aws_glue_catalog_database.mlops.name
  name          = "mlops_feature_store_crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${aws_s3_bucket.feature_store.bucket}/impression_feature"
  }
}
