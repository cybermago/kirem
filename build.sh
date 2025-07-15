#!/usr/bin/env bash
# exit on error
set -o errexit

python3 -m pip install --upgrade pip

pip3 install -r requirements.txt

echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --no-input

echo "Iniciando migraçoes"
python3 manage.py makemigrations
python3 manage.py migrate
