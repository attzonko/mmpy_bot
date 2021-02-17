#!/bin/bash
set -euo pipefail
pip install -r requirements.txt
pip install pytest-cov
pip install .
"$@"
