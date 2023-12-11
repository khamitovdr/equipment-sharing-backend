#!/bin/bash

docker compose down -v
sudo rm -r project/migrations/
find project/static -type d -name "info" -prune -o -type f ! -name '.gitignore' -exec rm {} \;
docker compose up -d --build
sleep 3
docker compose exec web aerich init-db

# sleep 7
# ./project/env/bin/python ./test_and_fulfillment/init_script.py
