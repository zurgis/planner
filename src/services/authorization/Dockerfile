FROM python:3.10-alpine3.17 as requirements

WORKDIR /usr/src

RUN apk update && apk add bash \
        curl \
        gcc \
        musl-dev \
        libffi-dev \
    && rm -rf /var/cache/apk/* \
    && curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python \
    && cd /usr/local/bin \
    && ln -s /etc/poetry/bin/poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml .

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == true ] ; then poetry export --output requirements.txt --without-hashes --dev ; \
    else poetry export --output requirements.txt --without-hashes ; fi"

FROM python:3.10-alpine3.17

WORKDIR /usr/src

RUN apk add \
        gcc \
        musl-dev \
        libffi-dev \
    && rm -rf /var/cache/apk/*

COPY --from=requirements /usr/src/requirements.txt .

COPY app app

RUN pip install -U pip --no-cache-dir -r requirements.txt && rm requirements.txt

CMD ["python", "app/main.py"]
