locals {
  github_repository = "<your-github-username>/<your-repository-name>"
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}


data "aws_iam_policy_document" "github_actions" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRoleWithWebIdentity",
    ]
    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.github_actions.arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${local.github_repository}:*"]
    }

  }
}

data "aws_iam_policy_document" "github_actions_workflow" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "iam:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecr:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecs:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "glue:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "ec2:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "firehose:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "elasticloadbalancing:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "states:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "application-autoscaling:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "scheduler:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "athena:*"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }
}

# GitHub Actions Role
resource "aws_iam_role" "github_actions" {
  name = "mlops-github-actions-role"
  assume_role_policy = data.aws_iam_policy_document.github_actions.json

  tags = {
    Name = "mlops-github-actions-role"
  }
}

resource "aws_iam_policy" "github_actions_workflow" {
  name   = "github-actions-policy"
  policy = data.aws_iam_policy_document.github_actions_workflow.json
}

resource "aws_iam_role_policy_attachment" "github_actions_workflow" {
  policy_arn = aws_iam_policy.github_actions_workflow.arn
  role       = aws_iam_role.github_actions.name
}
