.PHONY: all run build
ifndef VERBOSE
.SILENT:
endif

quotestr = $(subst ','\'', $1)

IMAGE_NAME := "require-id/core"
SERVICE_NAME := "require-id"
LOCAL_PORT := "4711"
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


start: run
go: run
serve: run
docker-run: run
run-docker: run
docker_run: run
run_docker: run

exec: shell
execute: shell
sh: shell
bash: shell

project-cli: project_cli
cli-project: project_cli
cli_project: project_cli
project-shell: project_cli
project_shell: project_cli
shell-project: project_cli
shell_project: project_cli
poetry-cli: project_cli
poetry_cli: project_cli
cli-poetry: project_cli
cli_poetry: project_cli
poetry-shell: project_cli
poetry_shell: project_cli
shell-poetry: project_cli
shell_poetry: project_cli
poetry_man: project_cli
poetry-man: project_cli
poetry_manual: project_cli
poetry-manual: project_cli
man_poetry: project_cli
man-poetry: project_cli
manual_poetry: project_cli
manual-poetry: project_cli

shell-only: cli
shell_only: cli
only-shell: cli
only_shell: cli
cmd: cli

install: build
image: build
docker: build
docker-build: build
docker_build: build
build-docker: build
build_docker: build

poet: poetry
deps: poetry
dependencies: poetry
poetry-update: poetry
poetry_update: poetry
update-poetry: poetry
update_poetry: poetry

lock: poetry_lock
poetry-lock: poetry_lock
lock-poetry: poetry_lock
lock_poetry: poetry_lock

list: poetry_show
show: poetry_show
list_dependencies: poetry_show
list-dependencies: poetry_show
poetry_list: poetry_show
poetry-list: poetry_show
poetry-show: poetry_show
list_poetry: poetry_show
list-poetry: poetry_show

poetry-add: poetry_add
add-poetry: poetry_add
add_poetry: poetry_add
add: poetry_add

poetry-remove: poetry_remove
remove-poetry: poetry_remove
remove_poetry: poetry_remove
poetry-delete: poetry_remove
poetry_delete: poetry_remove
delete-poetry: poetry_remove
delete_poetry: poetry_remove
poetry-uninstall: poetry_remove
uninstall-poetry: poetry_remove
remove: poetry_remove
delete: poetry_remove
uninstall: poetry_remove