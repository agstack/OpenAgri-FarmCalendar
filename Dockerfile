ARG SOURCE_REPO=https://github.com/openagri-eu/openagri-farmcalendar
FROM python:3.12
LABEL org.opencontainers.image.source=${SOURCE_REPO}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PIP_VERSION_TO_INSTALL="24.0"

# install essential OS libs
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    git \
    cmake \
    pkg-config \
    build-essential \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -U pip==${PIP_VERSION_TO_INSTALL} && \
    rm -rf /tmp/pip* /root/.cache

# Set the working directory to /var/www
WORKDIR /var/www

COPY requirements.txt /var/www/
RUN pip install -r requirements.txt && \
    rm -rf /tmp/pip* /root/.cache

# Copy the current directory contents into the container at /var/www
COPY . /var/www

# Add the entrypoint script and set the execute permissions
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
