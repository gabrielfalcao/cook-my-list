MAKEFILE_PATH		:= $(realpath $(firstword $(MAKEFILE_LIST)))
GIT_ROOT		:= $(shell dirname $(MAKEFILE_PATH))
VENV_ROOT		:= $(GIT_ROOT)/.venv

PACKAGE_NAME		:= scraper_engine
MAIN_CLI_NAME		:= cook-my-list
REQUIREMENTS_FILE	:= development.txt

PACKAGE_PATH		:= $(GIT_ROOT)/$(PACKAGE_NAME)
REQUIREMENTS_PATH	:= $(GIT_ROOT)/$(REQUIREMENTS_FILE)

BASE_TAG		:= latest
PROD_TAG		?= $(shell git log --pretty="format:%H" -n1 . | tail -1)
DOCKER_AUTHOR		:= gabrielfalcao
BASE_IMAGE		:= cook-my-list-base
PROD_IMAGE		:= cook-my-list

DOCKER_ENV		:= $(GIT_ROOT)/tools/docker.env
KUBE_ENV_CATTLE		:= $(GIT_ROOT)/kube/cattle/kube.env
KUBE_ENV_PET		:= $(GIT_ROOT)/kube/pets/kube.env
KUBE_ENV		:= $(KUBE_ENV_CATTLE) $(KUBE_ENV_PET)

KUBE_BUTLER_YML_CATTLE	:= $(GIT_ROOT)/kube/cattle/cook-my-list.yml
KUBE_BUTLER_YML_PET	:= $(GIT_ROOT)/kube/pets/cook-my-list.yml
KUBE_BUTLER_YML		:= $(KUBE_BUTLER_YML_CATTLE) $(KUBE_BUTLER_YML_PET)
BUILD_PATHS		:= build docs/build frontend/build
DOCKER_IMAGE_NAME	:= gabrielfalcao/cook-my-list
BRANCH_NAME		:= $(shell git branch | grep '^[*]' | awk '{print $$2}')
DOCKER_IMAGE_TAG	:= $(shell git rev-parse origin/$(BRANCH_NAME))
TMP_KUBE		:= $(GIT_ROOT)/wip/cattle.yml
K8S_NAMESPACE		:= cook-my-list-ns
KUSTOMIZATION_PATH	:= $(GIT_ROOT)/kube
KUSTOMIZATION_CATTLE_YML:= $(KUSTOMIZATION_PATH)/cattle/kustomization.yml
KUSTOMIZATION_PET_YML	:= $(KUSTOMIZATION_PATH)/pets/kustomization.yml
KUSTOMIZATION_YML	:= $(KUSTOMIZATION_CATTLE_YML) $(KUSTOMIZATION_PET_YML)

K8S_MAX_LOG_REQUESTS	:= 100


# database env vars
ALEMBIC_CONFIG		?= $(PACKAGE_PATH)/alembic.ini
POSTGRES_HOST		?= localhost
POSTGRES_USER		?= scraper_engine
POSTGRES_PASSWORD	?= scraper_engine
POSTGRES_DB		?= scraper_engine
SQLALCHEMY_URI		?= postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST)/$(POSTGRES_DB)
export VENV		?= $(VENV_ROOT)
PYTEST			:= $(VENV)/bin/pytest
MAIN_CLI_PATH		:= $(VENV)/bin/$(MAIN_CLI_NAME)
export SQLALCHEMY_URI
export ALEMBIC_CONFIG
export POSTGRES_HOST
export POSTGRES_USER
export POSTGRES_PASSWORD
export POSTGRES_DB

######################################################################
# Phony targets (only exist for typing convenience and don't represent
#                real paths as Makefile expects)
######################################################################

# default target when running `make` without arguments
all: | $(MAIN_CLI_PATH)

$(ALEMBIC_CONFIG): | $(VENV)/bin/python $(VENV)/bin/alembic
	$(VENV)/bin/python tools/create-alembic-ini.py

db-create:
	-@2>/dev/null dropdb $(POSTGRES_DB) > /dev/null || echo "database does not exist yet"
	-@2>/dev/null dropuser $(POSTGRES_USER) > /dev/null || echo "user does not exist yet"
	@echo "creating postgresql user and database from scratch"
	@createuser $(POSTGRES_USER)
	@createdb --owner=$(POSTGRES_USER) $(POSTGRES_DB)
	@echo "setting password for postgresql user $(POSTGRES_USER)"
	@psql -U scraper_engine -c "ALTER USER $(POSTGRES_USER) WITH PASSWORD '$(POSTGRES_PASSWORD)';"


db-migrate: | $(ALEMBIC_CONFIG) $(VENV)/bin/alembic
	@echo "running migrations"
	@(cd $(PACKAGE_PATH) && $(VENV)/bin/alembic upgrade head)

db: db-create db-migrate
# creates virtualenv
venv: | $(VENV)

# updates pip and setuptools to their latest version
develop: | $(VENV)/bin/python $(VENV)/bin/pip

# installs the requirements and the package dependencies
setup: | $(MAIN_CLI_PATH)

# Convenience target to ensure that the venv exists and all
# requirements are installed
dependencies:
	@rm -f $(MAIN_CLI_PATH) # remove MAIN_CLI_PATH to trigger pip install
	$(MAKE) develop setup

# Run all tests, separately
tests: unit functional | $(MAIN_CLI_PATH)  # runs all tests

# -> unit tests
unit functional: | $(VENV)/bin/pytest  # runs only unit tests
	$(PYTEST) tests/$@

# run main command-line tool
web workers crawler: | $(MAIN_CLI_PATH)
	@$(MAIN_CLI_PATH) $@

worker-get-recipe:
	@$(MAIN_CLI_PATH) worker:get_recipe

queue:
	@$(MAIN_CLI_PATH) worker:queue

# Pushes release of this package to pypi
push-release:  # pushes distribution tarballs of the current version
	$(VENV)/bin/twine upload dist/*.tar.gz

# Prepares release of this package prior to pushing to pypi
build-release:
	rm -rf ./dist  # remove local packages
	$(VENV)/bin/twine check dist/*.tar.gz
	$(VENV)/bin/python setup.py build sdist

# Convenience target that runs all tests then builds and pushes a release to pypi
release: tests build-release push-release
	$(MAKE) build-release
	$(MAKE) push-release

# Convenience target to delete the virtualenv
clean:
	@rm -rf .venv .coverage

# Convenience target to format code with black with PEP8's default
# 80 character limit per line
black: | $(VENV)/bin/black
	@$(VENV)/bin/black -l 80 $(PACKAGE_PATH) tests


## DOCKER
docker-base-image:
	docker images | grep "$(BASE_IMAGE):$(BASE_TAG)" || docker build -f Dockerfile.base -t "$(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)" .

docker-image: docker-base-image
	docker tag "$(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)" "$(DOCKER_AUTHOR)/$(BASE_IMAGE)"
	docker build -f Dockerfile -t $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG) .
	docker tag $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG) $(DOCKER_AUTHOR)/$(PROD_IMAGE):latest

docker-push:
	@2>/dev/null docker login -p $$(echo  "a2ltazI1MDIK" | base64 -d) -u gabrielfalcao
	docker push $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG)

docker-push-all: docker-push
	docker push $(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)
	docker push $(DOCKER_AUTHOR)/$(BASE_IMAGE)
	docker push $(DOCKER_AUTHOR)/$(PROD_IMAGE)


##############################################################
# Real targets (only run target if its file has been "made" by
#               Makefile yet)
##############################################################

# creates virtual env if necessary and installs pip and setuptools
$(VENV): | $(REQUIREMENTS_PATH)  # creates $(VENV) folder if does not exist
	echo "Creating virtualenv in $(VENV)" && python3 -mvenv $(VENV)

# installs pip and setuptools in their latest version, creates virtualenv if necessary
$(VENV)/bin/python $(VENV)/bin/pip: # installs latest pip
	@test -e $(VENV)/bin/python || $(MAKE) $(VENV)
	@test -e $(VENV)/bin/pip || $(MAKE) $(VENV)
	@echo "Installing latest version of pip and setuptools"
	@echo $(VENV)/bin/pip install -U pip setuptools

 # installs latest version of the "black" code formatting tool
$(VENV)/bin/black: | $(VENV)/bin/pip
	$(VENV)/bin/pip install -U black

# installs this package in "edit" mode after ensuring its requirements are installed
$(VENV)/bin/alembic $(VENV)/bin/pytest $(MAIN_CLI_PATH): | $(VENV) $(VENV)/bin/pip $(VENV)/bin/python $(REQUIREMENTS_PATH)
	$(VENV)/bin/pip install -r $(REQUIREMENTS_PATH)
	$(VENV)/bin/pip install -e .

# ensure that REQUIREMENTS_PATH exists
$(REQUIREMENTS_PATH):
	@echo "The requirements file $(REQUIREMENTS_PATH) does not exist"
	@echo ""
	@echo "To fix this issue:"
	@echo "  edit the variable REQUIREMENTS_NAME inside of the file:"
	@echo "  $(MAKEFILE_PATH)."
	@echo ""
	@exit 1


port-forward:
	kubectl -n $(K8S_NAMESPACE) port-forward service/cook-my-list-queue 5555:5555

kube: clean $(TMP_KUBE) $(KUSTOMIZATION_YML)

undeploy: undeploy-application undeploy-infra

undeploy-application:
	kubectl -n $(K8S_NAMESPACE) delete service -l app.kubernetes.io/name=cook-my-list
	kubectl -n $(K8S_NAMESPACE) delete statefulset -l app.kubernetes.io/name=cook-my-list
	kubectl -n $(K8S_NAMESPACE) delete deployment -l app.kubernetes.io/name=cook-my-list

undeploy-infra:
	kubectl -n $(K8S_NAMESPACE) delete service -l cook-my-list/role=infra
	kubectl -n $(K8S_NAMESPACE) delete statefulset -l cook-my-list/role=infra
	kubectl -n $(K8S_NAMESPACE) delete deployment -l cook-my-list/role=infra


undeploy-all:
	kubectl -n $(K8S_NAMESPACE) delete deployment,service,statefulset --all

undeploy-volume-claims:
	kubectl -n $(K8S_NAMESPACE) delete pvc -l app.kubernetes.io/name=cook-my-list
	kubectl -n $(K8S_NAMESPACE) delete pv -l app.kubernetes.io/name=cook-my-list

k8s-delete-all-resources:
	test -f $(TMP_KUBE) && kubectl -n $(K8S_NAMESPACE) delete -f $(TMP_KUBE)

k8s-delete-pvs:
	kubectl -n $(K8S_NAMESPACE) get pvc --field-selector metadata.namespace=$(K8S_NAMESPACE) -o yaml | kubectl -n $(K8S_NAMESPACE)  delete -f -

k8s-delete-ns:
	kubectl delete ns $(K8S_NAMESPACE)
	$(MAKE) k8s-resources
logs-web:
	kubectl -n cook-my-list-ns logs --max-log-requests $(K8S_MAX_LOG_REQUESTS) --prefix --ignore-errors=true deployment/cook-my-list-web -f --all-containers

logs-workers:
	kubectl -n cook-my-list-ns logs --max-log-requests $(K8S_MAX_LOG_REQUESTS) --prefix --ignore-errors=true deployment/cook-my-list-build-info-worker -f --all-containers

logs-queue:
	kubectl -n cook-my-list-ns logs --max-log-requests $(K8S_MAX_LOG_REQUESTS) --prefix --ignore-errors=true deployment/cook-my-list-queue -f --all-containers

k8s-resources:
	kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl -n $(K8S_NAMESPACE) get --show-kind --ignore-not-found -n $(K8S_NAMESPACE)

k8s-purge-redis:
	 kubectl -n $(K8S_NAMESPACE) exec deployment/cook-my-list-queue -- bash -c "cook-my-list purge --redis-queue"

k8s-purge-all:
	 kubectl -n $(K8S_NAMESPACE) exec deployment/cook-my-list-queue -- bash -c "cook-my-list purge --elasticsearch --redis-queue --http-cache"

k8s-shell-queue:
	 kubectl -n $(K8S_NAMESPACE) exec -ti deployment/cook-my-list-queue -- bash

k8s-shell-kibana:
	 kubectl -n $(K8S_NAMESPACE) exec -ti service/cook-my-list-kibana -- bash

k8s-shell-redis:
	 kubectl -n $(K8S_NAMESPACE) exec -ti service/cook-my-list-redis -- bash

k8s-job:
	 kubectl -n $(K8S_NAMESPACE) exec deployment/cook-my-list-queue -- bash -c "cook-my-list builds --redis-only > /dev/null 2> /dev/null &"

redeploy:
	$(MAKE) undeploy
	$(MAKE) deploy

python-format:
	find drone_ci_butler -name '*.py' | xargs $(VENV)/bin/isort --profile=attrs --fass --star-first --honor-noqa . # --profile=attrs
	$(VENV)/bin/autoflake -ir drone_ci_butler
	$(VENV)/bin/autoflake -ir tests
	$(VENV)/bin/black drone_ci_butler
	$(VENV)/bin/black tests

# generates environment variables with secrets
$(DOCKER_ENV) $(KUBE_ENV): clean
	-$(ITERM2) name $(shell basename $(shell dirname $@)) env && $(ITERM2) color yellow 3
	@$(MAIN_CLI_PATH) env > $@
	@echo "\033[1;37mCREATED \033[1;32m$@\033[0m"

$(KUBE_BUTLER_YML):
	-$(ITERM2) name $(shell basename $@) && $(ITERM2) color grey 6
	@cp -f ~/.cook-my-list.yml $@
	@echo "\033[1;37mUPDATED \033[1;32m$@\033[0m"

$(TMP_KUBE): $(KUBE_ENV) $(KUBE_BUTLER_YML) $(KUSTOMIZATION_YML)
	-$(ITERM2) name $(shell basename $@) && $(ITERM2) color blue 3
	@kustomize build kube/cattle > $@
	@echo "\033[1;37mCREATED \033[1;32m$(TMP_KUBE)\033[0m"
	@echo "\t⬆️️ \033[1;34mthis is the 'kubernetes' file\033[0m"

deploy: $(TMP_KUBE)
	-$(ITERM2) name deploy && $(ITERM2) color grey 6
	@echo "\033[0;34mImage \033[1;35m$(DOCKER_IMAGE_NAME)\033[0m"
	@echo "\033[0;34mTag \033[1;36m$(DOCKER_IMAGE_TAG)\033[0m"
	@kubectl get ns $(K8S_NAMESPACE) || kubectl create ns $(K8S_NAMESPACE)
	@kubectl -n $(K8S_NAMESPACE) apply -f $(TMP_KUBE)

k9s:
	-@$(ITERM2) name k8s 🛳 && $(ITERM2) color k
	k9s -n $(K8S_NAMESPACE)

env-docker: | $(DOCKER_ENV)

compose: env-docker
	docker-compose up #  --abort-on-container-exit

check:
	@$(MAIN_CLI_PATH) check
	@$(MAIN_CLI_PATH) check-db
	@$(MAIN_CLI_PATH) check-es
	@$(MAIN_CLI_PATH) check-redis


###############################################################
# Declare all target names that exist for convenience and don't
# represent real paths, which is what Make expects by default:
###############################################################

.PHONY: \
	all \
	black \
	build-release \
	clean \
	dependencies \
	develop \
	docker-base-image \
	docker-image \
	docker-push \
	docker-push-all \
	push-release \
	release \
	setup \
	run \
	tests \
	unit \
	functional
