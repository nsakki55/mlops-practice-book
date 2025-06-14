resource "aws_dynamodb_table" "impression_feature" {
  name           = "mlops-impression-feature"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  stream_enabled = false

  attribute {
    name = "user_id"
    type = "N"
  }

  ttl {
    attribute_name = "expired_at"
    enabled        = true
  }

  tags = {
    Name = "mlops-impression-feature-table"
  }
}

resource "aws_dynamodb_table" "model_registry" {
  name           = "mlops-model-registry"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "model"
  range_key      = "version"
  stream_enabled = false

  attribute {
    name = "model"
    type = "S"
  }

  attribute {
    name = "version"
    type = "S"
  }

  tags = {
    Name = "mlops-model-registry-table"
  }
}
