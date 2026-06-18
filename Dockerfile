# syntax=docker/dockerfile:1

FROM python:3.14-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

CMD [ "python3", "api/api.py", "run", "--host=0.0.0.0"]
