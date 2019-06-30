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
EXTRAOPTIONS := $(shell if [ `docker version -f '{{.Server.Experimental}}'` = true ]; then echo --squash; fi)
CONFIG_DATA := $(shell if [ -e "config.json" ]; then cat config.json; else cat config.example.json; fi)
IMAGE_BUILT := $(shell if [ `docker images ${IMAGE_NAME}:dev -q` ]; then echo -n 1; fi)

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
	@echo "- Docker: routing HTTP traffic on port ${LOCAL_PORT} -> 80"
	docker run -ti -p ${LOCAL_PORT}:80 -v ${PWD}/app:/app -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' --name ${SERVICE_NAME} ${IMAGE_NAME}:dev

shell:
	docker exec -ti ${SERVICE_NAME} /bin/bash

cli:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}/app:/app -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' ${IMAGE_NAME}:dev /bin/bash

project_cli:
	if [ ! ${IMAGE_BUILT} ]; then make build; fi
	docker run -ti -v ${PWD}/app:/app -v ${PWD}:/project -w /project -e CONFIG_DATA='$(call quotestr,$(CONFIG_DATA))' ${IMAGE_NAME}:dev /bin/bash

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
	sam local start-api --profile ${AWS_PROFILE} --template app/template.yml

deploy:
	sam package --template-file app/template.yml --profile ${AWS_PROFILE} --s3-bucket ${AWS_LAMBDA_S3} --region ${AWS_REGION} --output-template-file app/packaged.yml
	sam deploy --profile ${AWS_PROFILE} --region ${AWS_REGION} --template-file app/packaged.yml --stack-name ${AWS_STACK} --capabilities CAPABILITY_IAM