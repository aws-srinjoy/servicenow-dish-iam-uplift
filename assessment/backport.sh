#!/bin/bash
set -Eeuox pipefail

future-fstrings-show assessment.py > assessment_format.py
future-fstrings-show services-last-used.py > services-last-used-format.py
future-fstrings-show iam-roles-metrics.py > iam-roles-metrics-format.py

