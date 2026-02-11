FROM python:3.11.7-slim as development_build

ENV PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_ROOT_USER_ACTION=ignore \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./apt_requirements.txt /usr/src/app/apt-requirements.txt

# System deps:
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  $(cat ./apt-requirements.txt) \
  # Cleaning cache:
  && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip \
  && pip install uv \
  && uv --version


# set work directory
COPY requirements.txt /usr/src/app/

# Install dependencies:
RUN uv pip install --system -r requirements.txt
# copy project
COPY . /usr/src/app/