data "aws_availability_zones" "available" {
  state = "available"
}

# VPC
resource "aws_vpc" "mlops" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "mlops-vpc"
  }
}

# SecurityGroup for ML Pipeline
resource "aws_security_group" "train" {
  name        = "mlops-train-sg"
  description = "security group for train"
  vpc_id      = aws_vpc.mlops.id

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "mlops-train-sg"
  }
}

# SecurityGroup for application load balancer
resource "aws_security_group" "alb" {
  name        = "mlops-alb-sg"
  description = "security group for alb of prediction server"
  vpc_id      = aws_vpc.mlops.id
  ingress {
    from_port = 8080
    to_port   = 8080
    protocol  = "tcp"
    # Warning: In production, restrict the source of requests
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "mlops-predictor-alb-sg"
  }
}

# SecurityGroup for predict api
resource "aws_security_group" "predict_api" {
  name        = "mlops-predict-api-sg"
  description = "security group for predict api"
  vpc_id      = aws_vpc.mlops.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "mlops-predictor-api-sg"
  }
}

# Subnet
resource "aws_subnet" "public" {
  count             = length(data.aws_availability_zones.available.names)
  vpc_id            = aws_vpc.mlops.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = element(data.aws_availability_zones.available.names, count.index)

  tags = {
    Name = "public-subnet-${element(data.aws_availability_zones.available.names, count.index)}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "mlops" {
  vpc_id = aws_vpc.mlops.id

  tags = {
    Name = "mlops-igw"
  }
}

# Route Table (Public)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.mlops.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mlops.id
  }

  tags = {
    Name = "mlops-public-route-table"
  }
}

# Association (Public ${var.aws_region}a)
resource "aws_route_table_association" "public" {
  count          = length(data.aws_availability_zones.available.names)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
