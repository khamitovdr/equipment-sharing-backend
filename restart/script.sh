#!/bin/bash

docker compose down -v
sudo rm -r project/migrations/
docker compose up -d --build
sleep 5
docker compose exec web aerich init-db

./project/env/bin/python ./restart/init_script.py
