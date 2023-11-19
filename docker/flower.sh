#!/bin/bash

cd pera_fastapi
celery --app=tasks.tasks:celery flower --loglevel=info
