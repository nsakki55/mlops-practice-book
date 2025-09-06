resource "aws_lb" "mlops" {
  load_balancer_type = "application"
  name               = "mlops-alb"

  security_groups = [aws_security_group.alb.id]
  subnets         = aws_subnet.public[*].id
}


# ELB Target Group
resource "aws_lb_target_group" "predict_api_main" {
  name = "predict-api-main-target-group"

  port                 = 8080
  protocol             = "HTTP"
  target_type          = "ip"
  vpc_id               = aws_vpc.mlops.id
  deregistration_delay = 0
  health_check {
    interval            = 5
    timeout             = 2
    healthy_threshold   = 2
    unhealthy_threshold = 2
    port                = 8080
    path                = "/healthcheck"
  }
}

# ELB Target Group
resource "aws_lb_target_group" "predict_api_sub" {
  name = "predict-api-sub-target-group"

  port                 = 8080
  protocol             = "HTTP"
  target_type          = "ip"
  vpc_id               = aws_vpc.mlops.id
  deregistration_delay = 0
  health_check {
    interval            = 5
    timeout             = 2
    healthy_threshold   = 2
    unhealthy_threshold = 2
    port                = 8080
    path                = "/healthcheck"
  }
}

# Listener
resource "aws_lb_listener" "predict_api" {
  load_balancer_arn = aws_lb.mlops.arn
  port              = "8080"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.predict_api_main.arn
  }
}

resource "aws_lb_listener_rule" "predict_api" {
  listener_arn = aws_lb_listener.predict_api.arn
  priority     = 100

  action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.predict_api_main.arn
        weight = 100
      }
      target_group {
        arn    = aws_lb_target_group.predict_api_sub.arn
        weight = 0
      }
    }
  }

  condition {
    path_pattern {
      values = ["/predict"]
    }
  }
}

# To reduce ELB costs, create the event bridge to delete the ELB and target groups.
locals {
  delete_elb_state = "ENABLED" # Change to "DISABLED" to disable the schedule
  target_group_arns = [
    aws_lb_target_group.predict_api_main.arn,
    aws_lb_target_group.predict_api_sub.arn
  ]
}

resource "aws_scheduler_schedule" "elb_delete" {
  name                = "mlops-elb-delete-schedule"
  schedule_expression = "cron(0 */2 * * ? *)"
  group_name          = "default"
  state               = local.delete_elb_state

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:elasticloadbalancingv2:deleteLoadBalancer"
    role_arn = aws_iam_role.event_bridge.arn
    input = jsonencode({
      LoadBalancerArn = aws_lb.mlops.arn
    })
  }
}


resource "aws_scheduler_schedule" "elb_target_delete" {
  count               = length(local.target_group_arns)
  name                = "mlops-elb-target-delete-${count.index}-schedule"
  schedule_expression = "cron(0 */2 * * ? *)"
  group_name          = "default"
  state               = local.delete_elb_state

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:elasticloadbalancingv2:deleteTargetGroup"
    role_arn = aws_iam_role.event_bridge.arn
    input = jsonencode({
      TargetGroupArn = local.target_group_arns[count.index]
    })
  }
}
