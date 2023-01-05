#!/bin/bash
poetry install
mkdir -p deps
cd deps
git clone https://github.com/xoltar/phat
cd phat
poetry run pip install .
cd ../..
