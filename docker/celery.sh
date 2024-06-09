#!/bin/bash

# shellcheck disable=SC1046
if [[ "${1}" == "celery" ]]; then
    celery -A celery worker -l INFO
if [[ "${1}" == "celery_beat" ]]; then
    celery -A celery worker -l INFO -B
elif [[ "${1}" == "flower" ]]; then
    celery --app=tasks.celery:celery flower
fi
fi