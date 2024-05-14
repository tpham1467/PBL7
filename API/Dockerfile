FROM --platform=linux/amd64 python:3.9.2

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN echo pwd
COPY ./.env.example /usr/src/app/.env

RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY . /usr/src/app/

RUN cd ..
RUN cd /tmp
RUN apt update

# Install 114 chrome to get dependencies
RUN apt-get install fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libu2f-udev libvulkan1 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils -y
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN dpkg -i google-chrome-stable_current_amd64.deb
RUN dpkg -i chrome_114_amd64*.deb
RUN apt-get install -f


# Download chrome driver
RUN apt-get install curl -y
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip

# Unzip and copy chromedriver to /usr/bin/
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver

