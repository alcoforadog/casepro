FROM python:3

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash

RUN apt-get update && apt-get upgrade -y \
        -o Dpkg::Options::="--force-confdef" \
        -o Dpkg::Options::="--force-confold"

RUN apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gcc \
        python-dev \
        python3-dev \
        nodejs \
        node-less

WORKDIR /usr/src/app

COPY . .

RUN npm install        

RUN pip install --no-cache-dir -r pip-requires.txt

RUN cp docker/settings.py casepro/settings.py

EXPOSE 8000

RUN chmod +x /usr/src/app/docker/entrypoint.sh

ENTRYPOINT [ "/usr/src/app/docker/entrypoint.sh" ]