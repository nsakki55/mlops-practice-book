.PHONY: all
all: help

AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)
REGION := ap-northeast-1

ECR_REPOSITORY := $(AWS_ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com
DOCKER_TAG := latest
DOCKER_IMAGE := mlops-practice
PORT := 8080
ALB_DNS := $(ALB_DNS)
GIT_SHA := $(shell git rev-parse --short HEAD)


format: ## Run ruff format
	uv run ruff format src

lint: ## Run ruff check
	uv run ruff check src --fix

mypy: ## Run mypy
	uv run mypy src

test: ## Run pytest
	uv run pytest

train: ## Run train
	uv run src/train.py

feature: ## Run feature extraction
	uv run src/feature_extraction.py

build-push: ## Push ml pipeline image to ECR
	docker build . --platform linux/x86_64 -f ./Dockerfile -t $(ECR_REPOSITORY)/$(DOCKER_IMAGE):$(DOCKER_TAG) -t $(ECR_REPOSITORY)/$(DOCKER_IMAGE):local
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_IMAGE) --all-tags

train-docker: ## Run ml Pipeline
	docker container run -it -v $(HOME)/.aws/credentials:/root/.aws/credentials:ro \
				-e AWS_PROFILE=$(AWS_PROFILE) \
				$(ECR_REPOSITORY)/$(DOCKER_IMAGE) \
				uv run src/train.py

up: ## Docker compose up
	docker compose up

predict: ## Request prediction to localhost
	curl -X 'POST' 'http://localhost:${PORT}/predict' \
	    -H 'accept: application/json' \
	    -H 'Content-Type: application/json' \
	    -d '{"impression_id": "a9e7126a585a69a32bc7414e9d0c0ada", \
	         "logged_at": "2018-12-13 07:44:00", \
	         "user_id": 87862, \
	         "app_code": 127, \
	         "os_version": "latest", \
	         "is_4g": 1}'

predict-ecs: ## Request prediction to ECS
	curl -X 'POST' '${ALB_DNS}:${PORT}/predict' \
	    -H 'accept: application/json' \
	    -H 'Content-Type: application/json' \
	    -d '{"impression_id": "a9e7126a585a69a32bc7414e9d0c0ada", \
	         "logged_at": "2018-12-13 07:44:00", \
	         "user_id": 16998, \
	         "app_code": 127, \
	         "os_version": "latest", \
	         "is_4g": 1}'

healthcheck: ## Request health check to localhost
	curl -X 'GET' 'http://localhost:${PORT}/healthcheck'

healthcheck-ecs: ## Request health check to ECS
	curl -X 'GET' '${ALB_DNS}:${PORT}/healthcheck'

request-test: ## Request prediction with test date
	./request-test.sh

run-crawl-train-data: ## Run glue crawler for train_data
	aws glue start-crawler --name mlops_train_data_crawler

run-crawl-predict-log: ## Run glue crawler for predict_log
	aws glue start-crawler --name mlops_predict_log_crawler

run-crawl-train-log: ## Run glue crawler for train_log
	aws glue start-crawler --name mlops_train_log_crawler

run-crawl-feature-store: ## Run glue crawler for feature_store
	aws glue start-crawler --name mlops_feature_store_crawler

help: ## Show options
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
