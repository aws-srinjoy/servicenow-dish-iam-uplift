#!/usr/local/bin/bash
set -Eeuox pipefail

fileName=names.csv

declare -A address
while IFS='=' read name add
do
    echo "$name" "$add"
    address[$name]=$add
done < names.csv

declare -p address
echo "value: ${address[cloudtrail]}"

pandoc \
  headers/overview.md \
  headers/tenents.md \
  headers/mission-statement.md \
  headers/resources.md \
  headers/description.md \
  headers/contributing.md \
  headers/code.md \
  -t xwiki > guardrails.xwiki

#pandoc headers/guardrrails-header.md -t xwiki >> guardrails.xwiki
#pandoc cloudtrail/guardrails.md -t xwiki >> guardrails.xwiki

find . -name "guardrails.md" |  sort -t '\0' -n | while read line; do
  p=$(dirname $line)
  abbr=$(basename $p)
  echo "Abbr $abbr"
  abbreviation="${address[$abbr]}"
  echo "Found $abbreviation"
  echo "## $abbreviation" | pandoc -t xwiki >> guardrails.xwiki
  pandoc "$line" -t xwiki >> guardrails.xwiki
  #cat headers/guardrrails-header.md "$line"| pandoc -t xwiki >> guardrails.xwiki
  #pandoc headers/guardrrails-header.md -t xwiki >> guardrails.xwiki
  #pandoc "$line" -t xwiki >> guardrails.xwiki
done

cat headers/header.xwiki guardrails.xwiki > iam-permissions-guardrails.xwiki 

pandoc \
  headers/delivery-kit-owners.md \
  headers/guardrail-contributors.md \
  -t xwiki >> iam-permissions-guardrails.xwiki

cat iam-permissions-guardrails.xwiki | pbcopy
