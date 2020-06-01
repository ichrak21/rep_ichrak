# Author : Shanmugathas Vigneswaran
# Enterprise : FAR IT SAS Saint-Cloud

-include .env

.PHONY: all
.SILENT:

COM_COLOR   = \033[0;34m
OBJ_COLOR   = \033[0;36m
OK_COLOR    = \033[0;32m
ERROR_COLOR = \033[0;31m
WARN_COLOR  = \033[0;33m
NO_COLOR    = \033[m


# DYNAMIC INPUT
LOGIN ?= $(shell bash -c 'read -p "Artifactory LOGIN (Nokia Short ID) : " login; echo $$login')
PASSWORD ?= $(shell bash -c 'read -s -p "Artifactory PASWD: " pwd; echo $$pwd')

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
# A category can be added with @category
# HELP_FUN source = https://gist.github.com/prwhite/8168133
HELP_FUN = \
    %help; \
    while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
    print "usage: make [target]\n\n"; \
    for (sort keys %help) { \
    print "${NO_COLOR}$$_:${NO_COLOR}\n"; \
    for (@{$$help{$$_}}) { \
    $$sep = " " x (32 - length $$_->[0]); \
    print "  ${WARN_COLOR}$$_->[0]${NO_COLOR}$$sep${OK_COLOR}$$_->[1]${NO_COLOR}\n"; \
    }; \
    print "\n"; }


help: ##@other Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

init-local-dev-db: ##@dev intialize local database
	cd src ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py migrate ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py makemigrations ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py migrate ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py charger Pays ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py charger Region ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py charger Departement ;\
	DJANGO_DATABASE='local_dev' pipenv run python manage.py charger Commune

init-super-django-admin:
	DJANGO_DATABASE='local_dev' pipenv run python src/manage.py migrate --noinput ; \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('login_test0', 'email test', 'pwd test')" | DJANGO_DATABASE='local_dev' pipenv run python src/manage.py shell \
	cd src ;\
	pipenv run python manage.py syncdb --noinput ;\
	DJANGO_ADMIN_EMAIL='email@test.com' ; \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('test', '$(DJANGO_ADMIN_EMAIL)', 'test0')" \
    |$DJANGO_DATABASE pipenv run python manage.py shell && \

runserver-local: ##@dev run local django server
	DJANGO_DB='local_dev' pipenv run python manage.py runserver

docker-run-dummie-db: ##@dev run dummie PostgreSQL
	sudo docker run -it -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e TZ='Europe/Paris'  -p 5433:5432 postgres || echo 'PG alreay up'

docker-build: ##@dev build image
	sudo docker build -t ref-dev:0.0.1 -f Dockerfile .

docker-it: ##@dev run image it
	sudo docker run -it ref-dev:0.0.1 bash

local-server:
	DJANGO_DATABASE='local_dev' pipenv run python manage.py runserver

gitlab-test-dev: ##@ci-cd run job: test_dev
	gitlab-runner exec docker test_dev

gitlab-publish: ##@ci-cd run job: publish
	gitlab-runner exec docker publish

gitlab-deploy: ##@ci-cd run job: deploy_dev
	gitlab-runner exec docker deploy_dev

gitlab-do-all: gitlab-test-dev gitlab-publish gitlab-deploy ##@ci-cd run all job locally