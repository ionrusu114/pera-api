#!/bin/bash

cd pera_fastapi

alembic upgrade head

# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8070 --log-level=info --reload

poetry run uvicorn pera_fastapi.main:app --host 0.0.0.0 --port 8070 --reload