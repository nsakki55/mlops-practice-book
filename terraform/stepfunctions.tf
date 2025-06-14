resource "aws_sfn_state_machine" "train" {
  name     = "mlops-train-pipeline"
  role_arn = aws_iam_role.step_functions.arn
  definition = templatefile("./statemachine_definitions/train_pipeline.json", {
    cluster_arn         = aws_ecs_cluster.mlops.arn
    task_definition_arn = aws_ecs_task_definition.train.arn
    security_group      = aws_security_group.train.id
    subnet_ids          = jsonencode([for subnet in aws_subnet.public : subnet.id])
    cluster             = aws_ecs_cluster.mlops.name
    main_service        = aws_ecs_service.predict_api_main.name
    sub_service         = aws_ecs_service.predict_api_sub.name
  })

  tags = {
    Name = "mlops-train-batch-state-machine"
  }

  depends_on = [
    aws_iam_role.step_functions
  ]
}

resource "aws_scheduler_schedule" "train" {
  name                = "mlops-train-pipeline-schedule"
  schedule_expression = "cron(0 0 * * ? *)"
  group_name          = "default"
  flexible_time_window {
    mode = "OFF"
  }
  target {
    arn      = aws_sfn_state_machine.train.arn
    role_arn = aws_iam_role.event_bridge.arn
  }
  state = "DISABLED"
}
