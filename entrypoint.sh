#!/bin/bash

set -m
APP_HOST=0.0.0.0
APP_PORT=5050
APP_PATH="app:app"

gunicorn -w $(nproc --all) -b $APP_HOST:$APP_PORT $APP_PATH &
sleep 10
python -c "from app.tasks.celery import CeleryTasks; CeleryTasks._runner.apply_async()"
fg 1
rm -rf static/flask_gtts/*
