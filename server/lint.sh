#!/bin/bash

poetry run black .
poetry run ruff check --fix .