# syntax=docker/dockerfile:1
# base image
FROM python:3.10-slim-buster
WORKDIR /app
COPY ConsoleServer.py ConsoleServer.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
CMD [ "python3", "ConsoleServer.py" ]