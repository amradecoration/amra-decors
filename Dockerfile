FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app

# Update apt and install dependencies line-by-line
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        curl \
        openjdk-11-jdk \
        fonts-liberation \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcairo2 \
        libgtk-3-0 \
        libpango-1.0-0 \
        libxcomposite1 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libnspr4 \
        libnss3 \
        xdg-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add NodeSource PPA and install Node 20 (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs
 
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
ENV PATH=/root/.local/bin:$JAVA_HOME/bin:$PATH

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libqt5svg5 \
        libfontconfig1 \
        libxrender1 \
        util-linux \
        openssl \
        ca-certificates \
        curl \
        dnsutils \
        netcat \
        wkhtmltopdf \
        bsdmainutils \
        dnsutils \
        procps && \
    echo "✅ Installed all dependencies" && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python3 -m pip install --upgrade pip

COPY . .

RUN chmod 700 setup.sh
RUN chmod 700 migration.sh
RUN chmod 700 run.sh

RUN ./setup.sh

CMD [ "./run.sh" ]
