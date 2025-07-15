#!/usr/bin/env bash
# exit on error
set -o errexit

python3 -m pip install --upgrade pip

export DATABASE_URL="postgresql://neondb_owner:npg_0LsqPuf4IvwE@ep-crimson-wind-acsoculi-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

pip3 install -r requirements.txt

echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --no-input

echo "Iniciando migraçoes"
python3 manage.py makemigrations
python3 manage.py migrate
