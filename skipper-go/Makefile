BINARY_NAME=backrunner
PLATFORM=linux/amd64
REGION=us-east-2
ENVIRONMENT=mainnet

SHELL := /bin/bash

COMMIT:=$(shell git rev-parse --short HEAD)
TAG=$(COMMIT)
REGISTRY=ghcr.io
REPO=skip-mev/skipper-go
IMAGE=$(REGISTRY)/$(REPO):$(TAG)
NOMAD_FILE:=nomad/skipper-go-evmos.nomad
LEVANT_VAR_FILE:=$(shell mktemp -d)/levant.yaml

ifneq ($(GITHUB_TAG),)
  TAG=$(GITHUB_TAG)
endif

ifdef GITHUB_ACTIONS
  GITHUB_ACTIONS_FLAGS = --cache-to type=gha --cache-from type=gha
endif


build:
	go mod tidy
	go build -o ${BINARY_NAME} main.go


build-docker:
	docker buildx build \
		--platform ${PLATFORM} \
		-t ${IMAGE} \
		-t ${REGISTRY}/${REPO}:latest \
		-t ${REGISTRY}/${REPO}:${COMMIT} \
                --push \
		${GITHUB_ACTIONS_FLAGS} \
		-f Dockerfile \
		. 

deploy:
	touch ${LEVANT_VAR_FILE}
	yq e -i '.env |= "${ENVIRONMENT}"' ${LEVANT_VAR_FILE}
	yq e -i '.image |= "${IMAGE}"' ${LEVANT_VAR_FILE}
	levant deploy -force-count -var-file=${LEVANT_VAR_FILE} ${NOMAD_FILE}
