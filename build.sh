#!/bin/bash
pip install --upgrade pip setuptools wheel
pip install --only-binary :all: pandas==2.0.3
pip install -r backend/requirements.txt