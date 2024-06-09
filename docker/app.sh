#!/bin/bash

alembic upgrade 5fc95c875135

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000