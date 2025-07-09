FROM python:3.9

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# diretório de trabalho
WORKDIR /code

COPY requirements.txt .
# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# coletar arquivos estáticos
RUN python manage.py collectstatic --noinput
# running migrations
RUN python manage.py migrate

EXPOSE 8000

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "config.wsgi", "--bind", ":8000"]
