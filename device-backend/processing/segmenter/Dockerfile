FROM docker.io/library/python:3.9.18-slim-bullseye

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
RUN mkdir -p /home/pi/PlanktoScope/device-backend/processing/segmenter
WORKDIR /home/pi/PlanktoScope/device-backend/processing/segmenter

# Install Python dependencies

# Note: cmake is needed to install ninja which is needed to install pyproject.toml-based projects.
# We must remove it in the same RUN command as where we installed it, if we want to keep it out of
# the container image.
COPY --chown=pi:pi pyproject.toml poetry.lock ./
RUN \
  export PATH="/home/pi/.local/bin:$PATH" && \
  pip install --no-cache-dir cryptography==43.0.3 poetry==2.1.2 \
  --extra-index-url https://www.piwheels.org/simple && \
  poetry install --only main --compile && \
  poetry --no-interaction cache list && \
  poetry --no-interaction cache clear pypi --all && \
  poetry --no-interaction cache clear piwheels --all && \
  rm -rf /home/pi/.cache/pypoetry/artifacts && \
  rm -rf /home/pi/.cache/pypoetry/cache && \
  pip cache purge && \
  rm -rf /home/pi/.cache/pip

# Set up application

# Note: we must explicitly set chown if we drop root, or else files will be copied with root
# permissions.
COPY --chown=pi:pi main.py .
COPY --chown=pi:pi planktoscope/ ./planktoscope
ENTRYPOINT ["/home/pi/.local/bin/poetry", "run", "python", "main.py"]
EXPOSE 8001
RUN mkdir -p /home/pi/device-backend-logs/processing/segmenter

# Set container image metadata
# Note: this is just to try to make GitHub aware that we've moved the segmenter source code from
# github.com/PlanktoScope/device-backend to github.com/PlanktoScope/PlanktoScope:
LABEL org.opencontainers.image.source = "https://github.com/PlanktoScope/PlanktoScope"
