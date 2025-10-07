FROM docker.io/library/python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install OS dependencies

COPY apt-packages /tmp/
RUN \
  apt-get update && \
  apt-get -y upgrade && \
  grep -v '^#' /tmp/apt-packages | xargs apt-get -y install --no-install-recommends && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  rm /tmp/apt-packages

RUN useradd --create-home pi
USER pi:pi
RUN mkdir -p /home/pi/PlanktoScope/segmenter
WORKDIR /home/pi/PlanktoScope/segmenter

ENV MQTT_HOSTNAME=host.docker.internal

# Install Python dependencies

# Note: cmake is needed to install ninja which is needed to install pyproject.toml-based projects.
# We must remove it in the same RUN command as where we installed it, if we want to keep it out of
# the container image.
COPY --chown=pi:pi pyproject.toml uv.lock ./
RUN \
  uv sync && \
  uv clean --force

# Set up application

# Note: we must explicitly set chown if we drop root, or else files will be copied with root
# permissions.
COPY --chown=pi:pi main.py .
COPY --chown=pi:pi planktoscope/ ./planktoscope
ENTRYPOINT ["uv", "run", "main.py"]
EXPOSE 8001
