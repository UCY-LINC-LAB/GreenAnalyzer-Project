#!/bin/bash
# Apply database migrations
echo "START MIGRATIONS"
python manage.py makemigrations
python manage.py makemigrations GreenAnalyzer
python manage.py migrate
echo "FINISH MIGRATIONS"
python manage.py runserver 0.0.0.0:8000
