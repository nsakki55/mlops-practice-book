# ECS Task Execution Role
data "aws_iam_policy_document" "ecs_task_execution" {
  statement {
    effect = "Allow"
    actions = [
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateSecurityGroup",
      "ec2:CreateTags",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:DeleteSecurityGroup",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_task_execution" {
  name   = "mlops-ecs-task-exection-policy"
  policy = data.aws_iam_policy_document.ecs_task_execution.json

  tags = {
    Name = "mlops-ecs-task-execution-policy"
  }
}

data "aws_iam_policy_document" "ecs_task_execution_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name               = "mlops-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume_role.json

  tags = {
    Name = "mlops-ecs-task-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_task_execution.arn
}


# ECS Task Role
data "aws_iam_policy_document" "ecs_task" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:CreateLogGroup",
      "logs:DescribeLogGroups",
      "logs:GetLogEvents",
      "logs:DescribeLogStreams",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:ListMultipartUploadParts",
      "s3:AbortMultipartUpload",
      "s3:CreateBucket",
      "s3:PutObject",
      "s3:PutBucketPublicAccessBlock"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "athena:*",
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "glue:CreateDatabase",
      "glue:DeleteDatabase",
      "glue:GetCatalog",
      "glue:GetCatalogs",
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:UpdateDatabase",
      "glue:CreateTable",
      "glue:DeleteTable",
      "glue:BatchDeleteTable",
      "glue:UpdateTable",
      "glue:GetTable",
      "glue:GetTables",
      "glue:BatchCreatePartition",
      "glue:CreatePartition",
      "glue:DeletePartition",
      "glue:BatchDeletePartition",
      "glue:UpdatePartition",
      "glue:GetPartition",
      "glue:GetPartitions",
      "glue:BatchGetPartition",
      "glue:StartColumnStatisticsTaskRun",
      "glue:GetColumnStatisticsTaskRun",
      "glue:GetColumnStatisticsTaskRuns",
      "glue:GetCatalogImportStatus"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:Query"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "firehose:PutRecord",
      "firehose:PutRecordBatch",
    ]
    resources = [
      "*"
    ]
  }
}



resource "aws_iam_policy" "ecs_task" {
  name   = "mlops-ecs-task-policy"
  policy = data.aws_iam_policy_document.ecs_task.json

  tags = {
    Name = "mlops-ecs-task-policy"
  }
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com", "ssm.amazonaws.com", "ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task" {
  name               = "mlops-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = {
    Name = "mlops-ecs-task-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.ecs_task.arn
}

# Step Functions Role
data "aws_iam_policy_document" "step_functions" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogDelivery",
      "logs:GetLogDelivery",
      "logs:UpdateLogDelivery",
      "logs:DeleteLogDelivery",
      "logs:ListLogDeliveries",
      "logs:PutResourcePolicy",
      "logs:DescribeResourcePolicies",
      "logs:DescribeLogGroups",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecs:RunTask",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "glue:StartCrawler",
      "glue:GetCrawler"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingRules",
      "xray:GetSamplingTargets",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "events:PutTargets",
      "events:PutRule",
      "events:DescribeRule",
    ]
    resources = [
      "arn:aws:events:${local.aws_region}:${local.aws_account_id}:rule/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecs:UpdateService"
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "step_functions" {
  name   = "mlops-step-functions-policy"
  policy = data.aws_iam_policy_document.step_functions.json

  tags = {
    Name = "mlops-step-functions-policy"
  }
}


data "aws_iam_policy_document" "step_functions_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "step_functions" {
  name               = "mlops-step-functions-role"
  assume_role_policy = data.aws_iam_policy_document.step_functions_assume_role.json

  tags = {
    Name = "mlops-step-functions-role"
  }
}

resource "aws_iam_role_policy_attachment" "step_functions" {
  role       = aws_iam_role.step_functions.name
  policy_arn = aws_iam_policy.step_functions.arn
}

# Event Bridge Role
data "aws_iam_policy_document" "event_bridge" {
  statement {
    effect = "Allow"
    actions = [
      "states:StartExecution"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:DeleteTargetGroup",
      "elasticloadbalancing:DescribeTargetGroups",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeListeners",
      "elasticloadbalancing:DescribeRules",
      "elasticloadbalancing:DescribeTargetHealth",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "event_bridge" {
  name   = "mlops-event-bridge-policy"
  policy = data.aws_iam_policy_document.event_bridge.json

  tags = {
    Name = "mlops-event-bridge-policy"
  }
}

data "aws_iam_policy_document" "event_bridge_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "event_bridge" {
  name               = "mlops-event-bridge-role"
  assume_role_policy = data.aws_iam_policy_document.event_bridge_assume_role.json

  tags = {
    Name = "mlops-event-bridge-role"
  }
}

resource "aws_iam_role_policy_attachment" "event_bridge" {
  role       = aws_iam_role.event_bridge.name
  policy_arn = aws_iam_policy.event_bridge.arn
}

# Glue Crawler Role
data "aws_iam_policy_document" "glue_crawler" {
  statement {
    effect = "Allow"
    actions = [
      "s3:List*",
      "s3:Get*",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "glue:GetCrawler",
      "glue:GetTable",
      "glue:GetDatabase",
      "glue:CreateTable",
      "glue:UpdateTable",
      "glue:BatchCreatePartition",
      "glue:BatchGetPartition",
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "glue_crawler" {
  name   = "mlops-glue-cralwer-policy"
  policy = data.aws_iam_policy_document.glue_crawler.json

  tags = {
    Name = "mlops-glue-crawler-policy"
  }
}

data "aws_iam_policy_document" "glue_crawler_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue_crawler" {
  name               = "mlops-glue-crawler-role"
  assume_role_policy = data.aws_iam_policy_document.glue_crawler_assume_role.json

  tags = {
    Name = "mlops-glue-crawler-role"
  }
}

resource "aws_iam_role_policy_attachment" "glue_crawler" {
  role       = aws_iam_role.glue_crawler.name
  policy_arn = aws_iam_policy.glue_crawler.arn
}


# Kinesis Firehose Role
data "aws_iam_policy_document" "kinesis" {
  statement {
    sid = "S3Access"

    effect = "Allow"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject"
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.predict_api.bucket}",
      "arn:aws:s3:::${aws_s3_bucket.predict_api.bucket}/*",
    ]
  }
}

resource "aws_iam_policy" "kinesis" {
  name   = "mlops-kinesis-policy"
  policy = data.aws_iam_policy_document.kinesis.json

  tags = {
    Name = "mlops-kinesis-policy"
  }
}

data "aws_iam_policy_document" "kinesis_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "kinesis" {
  name               = "mlops-kinesis-role"
  assume_role_policy = data.aws_iam_policy_document.kinesis_assume_role.json

  tags = {
    Name = "mlops-kinesis-role"
  }
}

resource "aws_iam_role_policy_attachment" "kinesis" {
  role       = aws_iam_role.kinesis.name
  policy_arn = aws_iam_policy.kinesis.arn
}
