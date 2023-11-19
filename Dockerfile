FROM python:3.10.12-alpine

EXPOSE 8070

WORKDIR /code

RUN pip install --upgrade pip
RUN apk add gcc musl-dev libffi-dev
RUN apk add mysql-client
RUN pip install poetry
RUN apk add --no-cache bash
COPY  . /code



COPY docker/pera_api.sh docker/celery.sh docker/flower.sh /code/docker/
RUN chmod +x /code/docker/pera_api.sh /code/docker/celery.sh /code/docker/flower.sh

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --without test

# WORKDIR /code/pera_fastapi

# CMD [ "poetry", "run", "uvicorn", "pera_fastapi.main:app", "--host", "0.0.0.0","--reload", "--port", "8070" ]