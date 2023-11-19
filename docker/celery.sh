#!/bin/bash

cd pera_fastapi
celery --app=tasks.tasks:celery worker --loglevel=info -c 4