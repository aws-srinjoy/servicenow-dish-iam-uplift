#!/usr/local/bin/bash
set -Eeuox pipefail

for filename in guardrails/**/*.json; do
  scratch_file=$(mktemp)
  jq . "$filename" > "$scratch_file"
  cp "$scratch_file" "$filename" 
done
