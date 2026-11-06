#!/bin/sh
# Run inside the Python environment where DESLab will be used.
set -eu
cd "$(dirname "$0")"
python3 -m pip install .
