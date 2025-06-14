resource "aws_cloudwatch_dashboard" "mlops" {
  dashboard_name = "mlops"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 6
        height = 6
        properties = {
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${aws_ecs_service.predict_api_main.name}", "ClusterName", "${aws_ecs_cluster.mlops.name}"],
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${aws_ecs_service.predict_api_sub.name}", "ClusterName", "${aws_ecs_cluster.mlops.name}"],
          ]
          region = local.aws_region
        }
      },
      {
        type   = "metric"
        x      = 6
        y      = 0
        width  = 6
        height = 6
        properties = {
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${aws_ecs_service.predict_api_main.name}", "ClusterName", "${aws_ecs_cluster.mlops.name}"],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${aws_ecs_service.predict_api_sub.name}", "ClusterName", "${aws_ecs_cluster.mlops.name}"],

          ]
          region = local.aws_region
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 6
        height = 6
        properties = {
          view    = "timeSeries"
          stacked = false
          metrics = [
            [
              "AWS/ApplicationELB",
              "TargetResponseTime",
              "TargetGroup",
              "${aws_lb_target_group.predict_api_sub.arn_suffix}",
              "LoadBalancer",
              "${aws_lb.mlops.arn_suffix}"
            ],
            [
              "AWS/ApplicationELB",
              "TargetResponseTime",
              "TargetGroup",
              "${aws_lb_target_group.predict_api_main.arn_suffix}",
              "LoadBalancer",
              "${aws_lb.mlops.arn_suffix}"
            ],
          ]
          region = "${local.aws_region}"
        }
      },
      {
        type   = "metric"
        x      = 18
        y      = 0
        width  = 6
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "TargetGroup", "${aws_lb_target_group.predict_api_main.arn_suffix}", "LoadBalancer", "${aws_lb.mlops.arn_suffix}"],
            ["AWS/ApplicationELB", "RequestCount", "TargetGroup", "${aws_lb_target_group.predict_api_sub.arn_suffix}", "LoadBalancer", "${aws_lb.mlops.arn_suffix}"],
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          stat    = "Sum"
        }
      },
      {
        type   = "metric",
        x      = 0,
        y      = 6,
        width  = 6,
        height = 6,
        properties = {
          sparkline = true,
          view      = "singleValue",
          metrics = [
            ["ECS/ContainerInsights", "RunningTaskCount", "ServiceName", "${aws_ecs_service.predict_api_main.name}", "ClusterName", "${aws_ecs_cluster.mlops.name}"],
            ["ECS/ContainerInsights", "RunningTaskCount", "ServiceName", "${aws_ecs_service.predict_api_sub.name}", "ClusterName", "${aws_ecs_cluster.mlops.name}"],
          ],
          region = local.aws_region
        }
      },
      {
        "type" : "metric",
        "x" : 6,
        "y" : 6,
        "width" : 6,
        "height" : 6,
        "properties" : {
          "sparkline" : true,
          "view" : "singleValue",
          "metrics" : [
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", "${aws_lb.mlops.arn_suffix}"]
          ],
          "region" : local.aws_region,
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          query   = <<EOT
          SOURCE '${aws_cloudwatch_log_group.predict_api.name}'
          | fields @timestamp, @message, @logStream, @log, jsonParse(@message) as json_message
          | filter ispresent(json_message.container_id)
          | sort @timestamp desc
          | unnest json_message.log into event
          | filter ispresent(event) and event != ""
          | filter event not like 'healthcheck'
          EOT
          region  = local.aws_region
          stacked = false
          title   = aws_cloudwatch_log_group.predict_api.name
          view    = "table"
        }
      }
    ]
  })
}
