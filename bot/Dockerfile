FROM python:3.5.2-alpine
MAINTAINER Kevin James <KevinJames@thekev.in>

COPY requirements.txt /src/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /src/requirements.txt

COPY . /src
RUN pip install /src

CMD jarvis
