#!/bin/bash

set -x

autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables app --exclude=__init__.py
black app
isort app