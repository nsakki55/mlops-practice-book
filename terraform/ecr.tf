resource "aws_ecr_repository" "mlops" {
  name                 = "mlops-practice"
  image_tag_mutability = "MUTABLE"

  tags = {
    Name = "mlops-ecr-repository"
  }
}

resource "aws_ecr_lifecycle_policy" "mlops" {
  repository = aws_ecr_repository.mlops.name

  policy = jsonencode(
    {
      "rules" : [
        {
          "rulePriority" : 1,
          "description" : "Delete any image older than 3 days",
          "selection" : {
            "tagStatus" : "any"
            "countType" : "sinceImagePushed",
            "countUnit" : "days",
            "countNumber" : 3
          },
          "action" : {
            "type" : "expire"
          }
        }
      ]
    }
  )
}

resource "aws_ecr_repository" "fluentbit" {
  name                 = "fluentbit"
  image_tag_mutability = "MUTABLE"

  tags = {
    Name = "mlops-fluentbit-ecr-repository"
  }
}

resource "aws_ecr_lifecycle_policy" "fluentbit" {
  repository = aws_ecr_repository.fluentbit.name
  policy = jsonencode(
    {
      "rules" : [
        {
          "rulePriority" : 1,
          "description" : "Delete any image older than 3 days",
          "selection" : {
            "tagStatus" : "any"
            "countType" : "sinceImagePushed",
            "countUnit" : "days",
            "countNumber" : 3
          },
          "action" : {
            "type" : "expire"
          }
        }
      ]
    }
  )

}

resource "null_resource" "fluentbit" {
  # Trigger when any file in the fluentbit directory changes
  triggers = {
    fluentbit_hash = sha256(join("", [
      for f in fileset("fluentbit", "**/*") :
      filesha256("fluentbit/${f}")
    ]))
  }

  # Authenticate to ECR
  provisioner "local-exec" {
    command = "aws ecr get-login-password --region ${local.aws_region} | docker login --username AWS --password-stdin ${local.aws_account_id}.dkr.ecr.ap-northeast-1.amazonaws.com"
  }

  # Build the image for Fluent Bit
  provisioner "local-exec" {
    command = "docker build --platform linux/x86_64 -f fluentbit/Dockerfile -t predict-api-fluentbit ."
  }

  # Tag the image
  provisioner "local-exec" {
    command = "docker tag predict-api-fluentbit:latest ${aws_ecr_repository.fluentbit.repository_url}:latest"
  }

  # Push the image to ECR
  provisioner "local-exec" {
    command = "docker push ${aws_ecr_repository.fluentbit.repository_url}:latest"
  }

  depends_on = [
    aws_ecr_repository.fluentbit,
    aws_ecr_lifecycle_policy.fluentbit
  ]
}
