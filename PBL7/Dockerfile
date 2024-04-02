FROM python:3.9.2-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

# RUN celery -A PBL7 flower --port=5000 --broker=redis://redis@localhost:6379
# RUN celery --broker=redis://redis@localhost:6379/0 flower

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]