#!/bin/bash
set -Eeuox pipefail

pandoc \
    overview.md \
    customer-outcomes.md \
    out-of-scope.md \
    example-sow.md \
    assumptions.md \
    artifacts.md \
    labor.md \
    user-stories-header.md \
    iam-health-check-user-stories.md \
    directive-controls-user-stories.md \
    access-analzyer-user-stories.md \
    pipeline-user-stories.md \
    config-rules-user-stories.md \
    cloudwatch-events-user-stories.md \
    iam-remediation-user-stories.md \
    owners.md \
    -t xwiki > delivery-kit.xwiki

cat header.xwiki delivery-kit.xwiki | pbcopy
