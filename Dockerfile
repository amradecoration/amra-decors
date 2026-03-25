FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app

# Update apt and install dependencies line-by-line
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python3 -m pip install --upgrade pip

COPY . .

RUN chmod 700 setup.sh
RUN chmod 700 migration.sh
RUN chmod 700 run.sh

RUN ./setup.sh

CMD [ "./run.sh" ]
