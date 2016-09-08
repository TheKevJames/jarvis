FROM python:2.7.12-alpine
MAINTAINER Kevin James <KevinJames@thekev.in>

COPY requirements.txt /src/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /src/requirements.txt

COPY . /src
RUN cd /src && python setup.py install

CMD jarvis
