#!/bin/sh
set -euox pipefail

mkdir -p results

ts=$(date -u +"%m-%d-%y-%H:%M:%S")
python3 iamdeco.py 2>&1 | tee results/assessment."$ts".txt
python3 services-last-used.py 2>&1 | tee results/services-last-used."$ts".txt
python3 iam-roles-metrics.py  2>&1 | tee results/iam-role-metrics."$ts".txt
python3 check-guardrails.py   2>&1 | tee results/check-guardrails."$ts".txt
python3 policy-validator.py   2>&1 | tee results/policy-validator."$ts".txt

python3 submit-report.py --timestamp "${ts}"
