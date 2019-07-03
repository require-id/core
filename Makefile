.PHONY: all run build
ifndef VERBOSE
.SILENT:
endif

quotestr = $(subst ','\'', $1)

IMAGE_NAME := "require-id/core"
SERVICE_NAME := "require-id"
LOCAL_PORT := "4711"
AWS_PROFILE := "require-id"
AWS_REGION := "eu-west-1"
AWS_LAMBDA_S3 := "require-id-lambda"
AWS_STACK := "require-id"
DOCKER_NETWORK := "require-id"
EXTRAOPTIONS := $(shell if [ `docker version -f '{{.Server.Experimental}}'` = true ]; then echo --squash; fi)
CONFIG_DATA := $(shell if [ -e "config.json" ]; then cat config.json; else cat config.example.json; fi)
IMAGE_BUILT := $(shell if [ `docker images ${IMAGE_NAME}:dev -q` ]; then echo -n 1; fi)
APP_API_KEY := $(shell (if [ -e "config.json" ]; then cat config.json; else cat config.example.json; fi) | python -c 'import sys, json; print(json.load(sys.stdin)["app_api_key"])')

ifeq (build,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif

ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif

default:
	@echo "Basic commands:         |"
	@echo "  $$ make build          | build image with Docker"
	@echo "  $$ make run            | start in Docker container"

build:
	docker build -t ${IMAGE_NAME}:latest --compress ${EXTRAOPTIONS} .
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:dev

run:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker rm ${SERVICE_NAME} 2> /dev/null &> /dev/null || true
	docker network create --driver bridge ${DOCKER_NETWORK} 2> /dev/null &> /dev/null || true
	@echo "- Docker: routing HTTP traffic on local port ${LOCAL_PORT} -> container (:80) -> service (:8080)"
	@echo "- Request API: $$ curl -H \"X-API-Key: ${APP_API_KEY}\" http://127.0.0.1:4711/api/status"
	docker run -ti -p ${LOCAL_PORT}:80 -v ${PWD}/app:/app --network=${DOCKER_NETWORK} -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' --name ${SERVICE_NAME} ${IMAGE_NAME}:dev

test:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker rm ${SERVICE_NAME} 2> /dev/null &> /dev/null || true
	docker network create --driver bridge ${DOCKER_NETWORK} 2> /dev/null &> /dev/null || true
	docker run -ti -p ${LOCAL_PORT}:80 -v ${PWD}/app:/app --network=${DOCKER_NETWORK} -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' --name ${SERVICE_NAME} ${IMAGE_NAME}:dev sh -c "pytest tests/ && flake8 --ignore E501"

shell:
	docker exec -ti ${SERVICE_NAME} /bin/bash

cli:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker network create --driver bridge ${DOCKER_NETWORK} 2> /dev/null &> /dev/null || true
	docker run -ti -v ${PWD}/app:/app --network=${DOCKER_NETWORK} -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' ${IMAGE_NAME}:dev /bin/bash

project_cli:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker network create --driver bridge ${DOCKER_NETWORK} 2> /dev/null &> /dev/null || true
	docker run -ti -v ${PWD}/app:/app -v ${PWD}:/project -w /project --network=${DOCKER_NETWORK} -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' ${IMAGE_NAME}:dev /bin/bash

poetry:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}:/project -w /project ${IMAGE_NAME}:dev poetry update --lock
	make build

poetry_show:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}:/project -w /project ${IMAGE_NAME}:dev poetry show

poetry_lock:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}:/project -w /project ${IMAGE_NAME}:dev poetry lock

poetry_add:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}:/project -w /project ${IMAGE_NAME}:dev poetry add ${RUN_ARGS}
	make build

poetry_remove:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}:/project -w /project ${IMAGE_NAME}:dev poetry remove ${RUN_ARGS}
	make build

sam_api:
	sam local start-api --profile ${AWS_PROFILE} --template template.yml

deploy:
	sam package --template-file template.yml --profile ${AWS_PROFILE} --s3-bucket ${AWS_LAMBDA_S3} --region ${AWS_REGION} --output-template-file packaged.yml
	sam deploy --profile ${AWS_PROFILE} --region ${AWS_REGION} --template-file packaged.yml --stack-name ${AWS_STACK} --capabilities CAPABILITY_IAM
	rm packaged.yml
