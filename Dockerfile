FROM python:3.8-alpine3.10

WORKDIR /usr/src/app

# update apk repo
RUN echo "https://dl-4.alpinelinux.org/alpine/v3.10/main" >> /etc/apk/repositories && \
    echo "https://dl-4.alpinelinux.org/alpine/v3.10/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

COPY . .

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./script.py"]
CMD ["vandy"]