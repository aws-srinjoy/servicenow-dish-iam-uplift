#!/usr/bin/env python3

from aws_cdk import core

from codecommit.codecommit_stack import CodecommitStack


app = core.App()
env_replication=core.Environment(region="us-east-1")
CodecommitStack(app, "codecommit-iam-permissions-guardrails",env=env_replication)

app.synth()
