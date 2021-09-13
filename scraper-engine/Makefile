MAKEFILE_PATH		:= $(realpath $(firstword $(MAKEFILE_LIST)))
GIT_ROOT		:= $(shell dirname $(MAKEFILE_PATH))
VENV_ROOT		:= $(GIT_ROOT)/.venv

PACKAGE_NAME		:= scraper_engine
MAIN_CLI_NAME		:= scraper-engine
REQUIREMENTS_FILE	:= development.txt

PACKAGE_PATH		:= $(GIT_ROOT)/$(PACKAGE_NAME)
REQUIREMENTS_PATH	:= $(GIT_ROOT)/$(REQUIREMENTS_FILE)
PYTEST			:= $(VENV_ROOT)/bin/pytest
MAIN_CLI_PATH		:= $(VENV_ROOT)/bin/$(MAIN_CLI_NAME)

BASE_TAG		:= latest
PROD_TAG		?= $(shell git log --pretty="format:%H" -n1 . | tail -1)
DOCKER_AUTHOR		:= gabrielfalcao
BASE_IMAGE		:= cookmylist-server-base
PROD_IMAGE		:= k8s-cookmylist-server

# database env vars
ALEMBIC_CONFIG		?= $(PACKAGE_PATH)/alembic.ini
POSTGRES_HOST		?= localhost
POSTGRES_USER		?= scraper_engine
POSTGRES_PASSWORD	?= scraper_engine
POSTGRES_DB		?= scraper_engine
SQLALCHEMY_URI		?= postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST)/$(POSTGRES_DB)
export VENV		?= $(VENV_ROOT)
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
	echo "Creating virtualenv in $(VENV_ROOT)" && python3 -mvenv $(VENV)

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
