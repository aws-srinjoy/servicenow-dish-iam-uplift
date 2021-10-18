#!/bin/bash
set -Eeuox pipefail

python3 transform-to-iam-policies.py --filename input.json --output_dir policies-to-analyze
parliament --version
parliament --minimum_severity LOW --directory policies-to-analyze --json | jq .
