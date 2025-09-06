resource "aws_ecs_cluster" "mlops" {
  name = "mlops-ecs"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "train" {
  name              = "/mlops/ecs/train"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "fluentbit" {
  name              = "/mlops/ecs/fluentbit"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "predict_api" {
  name              = "/mlops/ecs/predict-api"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "train" {
  family                   = "train"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./container_definitions/train.json", {
    ecr_uri           = aws_ecr_repository.mlops.repository_url,
    image_tag         = "latest",
    model_name        = "sgd_classifier_ctr",
    train_datetime_ub = "2018-12-10 00:00:00"
  })
  task_role_arn      = aws_iam_role.ecs_task.arn
  execution_role_arn = aws_iam_role.ecs_task_execution.arn
}

resource "aws_ecs_task_definition" "train_experiment" {
  family                   = "train-experiment"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./container_definitions/train.json", {
    ecr_uri           = aws_ecr_repository.mlops.repository_url,
    image_tag         = "local",
    model_name        = "sgd_classifier_ctr",
    train_datetime_ub = "2018-12-10 00:00:00",
  })
  task_role_arn      = aws_iam_role.ecs_task.arn
  execution_role_arn = aws_iam_role.ecs_task_execution.arn
}

resource "aws_ecs_task_definition" "predict_api_main" {
  family                   = "predict-api-main"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./container_definitions/predict_api.json", {
    ecr_uri         = aws_ecr_repository.mlops.repository_url,
    model_name      = "sgd_classifier_ctr",
    model_version   = "latest",
    feature_version = "latest",
    fluent_bid_uri  = aws_ecr_repository.fluentbit.repository_url,
  })
  task_role_arn      = aws_iam_role.ecs_task.arn
  execution_role_arn = aws_iam_role.ecs_task_execution.arn
}

resource "aws_ecs_cluster_capacity_providers" "mlops" {
  cluster_name = aws_ecs_cluster.mlops.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
    base              = 0
  }
}

resource "aws_ecs_service" "predict_api_main" {
  name                              = "predict-api-main"
  cluster                           = aws_ecs_cluster.mlops.name
  task_definition                   = aws_ecs_task_definition.predict_api_main.arn
  desired_count                     = 0
  health_check_grace_period_seconds = 2

  # Rolling Update
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  # Circuit breaker
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }
  network_configuration {
    security_groups  = [aws_security_group.predict_api.id]
    subnets          = [for subnet in aws_subnet.public : subnet.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.predict_api_main.arn
    container_name   = "predict-api"
    container_port   = 8080
  }

  depends_on = [aws_ecs_task_definition.predict_api_main]
}



resource "aws_ecs_task_definition" "predict_api_sub" {
  family                   = "predict-api-sub"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./container_definitions/predict_api.json", {
    ecr_uri         = aws_ecr_repository.mlops.repository_url,
    model_name      = "lightgbm_ctr",
    model_version   = "latest",
    feature_version = "latest",
    fluent_bid_uri  = aws_ecr_repository.fluentbit.repository_url,
  })
  task_role_arn      = aws_iam_role.ecs_task.arn
  execution_role_arn = aws_iam_role.ecs_task_execution.arn
}

resource "aws_ecs_service" "predict_api_sub" {
  name                              = "predict-api-sub"
  cluster                           = aws_ecs_cluster.mlops.name
  task_definition                   = aws_ecs_task_definition.predict_api_sub.arn
  desired_count                     = 0
  health_check_grace_period_seconds = 2

  # Rolling Update
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  # Circuit breaker
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }
  network_configuration {
    security_groups  = [aws_security_group.predict_api.id]
    subnets          = [for subnet in aws_subnet.public : subnet.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.predict_api_sub.arn
    container_name   = "predict-api"
    container_port   = 8080
  }

  depends_on = [aws_ecs_task_definition.predict_api_sub]
}

resource "aws_appautoscaling_target" "predict_api_main" {
  min_capacity       = 1
  max_capacity       = 5 
  resource_id        = "service/${aws_ecs_cluster.mlops.name}/${aws_ecs_service.predict_api_main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "predict_api_main" {
  name               = "predict-api-main-request-count-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.predict_api_main.resource_id
  scalable_dimension = aws_appautoscaling_target.predict_api_main.scalable_dimension
  service_namespace  = aws_appautoscaling_target.predict_api_main.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 10
    scale_out_cooldown = 10
    target_value       = 90
  }
}

resource "aws_appautoscaling_target" "predict_api_sub" {
  min_capacity       = 1
  max_capacity       = 5
  resource_id        = "service/${aws_ecs_cluster.mlops.name}/${aws_ecs_service.predict_api_sub.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "predict_api_sub" {
  name               = "predict-api-sub-app-autoscaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.predict_api_sub.resource_id
  scalable_dimension = aws_appautoscaling_target.predict_api_sub.scalable_dimension
  service_namespace  = aws_appautoscaling_target.predict_api_sub.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 10
    scale_out_cooldown = 10
    target_value       = 90
  }
}

# To reduce ECS costs, create scheduled action to change the ECS Task count to 0
resource "aws_appautoscaling_scheduled_action" "predict_api_main" {
  name               = "predict-api-main-scheduled-action"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.mlops.name}/${aws_ecs_service.predict_api_main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "cron(0 0 * * * ?)"

  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
}

resource "aws_appautoscaling_scheduled_action" "predict_api_sub" {
  name               = "predict-api-sub-scheduled-action"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.mlops.name}/${aws_ecs_service.predict_api_sub.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "cron(0 0 * * * ?)"

  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
}
