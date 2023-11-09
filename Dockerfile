FROM python:3.10.12-alpine

EXPOSE 8070

WORKDIR /code

RUN pip install --upgrade pip
RUN apk add gcc musl-dev libffi-dev
RUN apk add mysql-client
RUN pip install poetry

COPY  . /code

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --without test

CMD [ "poetry", "run", "uvicorn", "pera_fastapi.main:app", "--host", "0.0.0.0","--reload", "--port", "8070" ]

