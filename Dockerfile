FROM python:3.11-rc-slim

WORKDIR /usr/src/app

ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -y && apt upgrade -y
RUN apt-get install -y locales libusb-1.0-0 gcc cups
RUN usermod -aG lp root
RUN dpkg-reconfigure locales
RUN pip install --upgrade pip

COPY --chown=root:root . .
RUN pip install -r requirements/docker.txt
