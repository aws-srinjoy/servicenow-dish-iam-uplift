#!/bin/bash
set -Eeuox pipefail

find . -name "guardrails.md" |  sort -t '\0' -n | while read line; do
  echo "$line"
  cat headers/guardrrails-header.md "$line" > file3.txt; mv file3.txt "$line"
  #cat headers/guardrrails-header.md "$line"| pandoc -t xwiki >> guardrails.xwiki
  #pandoc headers/guardrrails-header.md -t xwiki >> guardrails.xwiki
  #pandoc "$line" -t xwiki >> guardrails.xwiki
done
