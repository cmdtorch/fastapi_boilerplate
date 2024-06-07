FROM python:3.12

WORKDIR /my_app
COPY ./req.txt /my_app/

RUN pip install -r req.txt

RUN pip install --no-cache-dir -r req.txt

COPY ./ /my_app

WORKDIR /my_app