#!/usr/bin/env bash

docker-compose exec web bash -c "python manage.py update_data" 