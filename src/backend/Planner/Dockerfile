FROM python:3.10-alpine3.16

WORKDIR /usr/src

RUN apk update && apk add bash curl && rm -rf /var/cache/apk/* \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/etc/poetry python \
    && cd /usr/local/bin \
    && ln -s /etc/poetry/bin/poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml .

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY app app

CMD ["python", "app/main.py"]
