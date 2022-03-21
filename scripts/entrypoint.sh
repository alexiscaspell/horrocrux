#!/usr/bin/env bash

# split off the first argument as the generator name
GENERATOR_NAME="./project_generator.pyc"
shift

# python "${GENERATOR_NAME}" "$1" "$@"
python "${GENERATOR_NAME}" "$1" "$2"
