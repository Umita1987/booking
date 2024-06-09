The uvicorn web server is used to run FastAPI. The command to run looks like this:

uvicorn app.main:app --reload
It must be run on the command line, necessarily located in the root directory of the project.

Celery & Flower
To run Celery, use the command

celery --app=app.tasks.celery:celery worker -l INFO -P solo
Please note that -P solo is only used on Windows, as Celery has problems working on Windows.
To start Flower, use the command

celery --app=app.tasks.celery:celery flower
Dockerfile
To run a web server (FastAPI) inside a container, you need to uncomment the code inside the Dockerfile and have an already running PostgreSQL instance on your computer. The code to run Dockerfile:

docker build .
The command is also run from the root directory where the Dockerfile file is located.

Docker compose
To run all services (DB, Redis, web server (FastAPI), Celery, Flower, Grafana, Prometheus), you must use the docker-compose file.yml and commands

docker compose build
docker compose up
Moreover, the build command needs to be run only if you changed something inside the Dockerfile, that is, you changed the logic of compiling the image.
