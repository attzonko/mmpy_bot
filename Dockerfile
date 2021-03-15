FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
COPY dev-requirements.txt dev-requirements.txt
RUN pip install -r requirements.txt -r dev-requirements.txt
COPY . .
RUN pip install -e .[dev]
ENTRYPOINT python entrypoint.py
