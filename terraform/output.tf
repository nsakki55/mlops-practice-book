output "alb_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.mlops.dns_name
}

output "data_s3_bucket" {
  description = "s3 bucket name for data"
  value       = aws_s3_bucket.data.bucket
}

output "model_s3_bucket" {
  description = "s3 bucket name for model"
  value       = aws_s3_bucket.model.bucket
}

output "feature_s3_bucket" {
  description = "s3 bucket name for feature store"
  value       = aws_s3_bucket.feature_store.bucket
}

output "athena_database" {
  description = "database name in athena"
  value       = aws_glue_catalog_database.mlops.name
}

output "feature_dynamodb_table" {
  description = "dynamodb table name for online feature store"
  value       = aws_dynamodb_table.impression_feature.name
}

output "model_registry_dynamodb_table" {
  description = "dynamodb table name for model registry"
  value       = aws_dynamodb_table.model_registry.name
}

output "public_subnet_1a" {
  description = "resource id for public subnet 1a"
  value       = aws_subnet.public[0].id
}

output "train_security_group" {
  description = "security group for train pipeline"
  value       = aws_security_group.train.id
}
