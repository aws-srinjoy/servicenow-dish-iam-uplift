#!/usr/bin/env python3

from aws_cdk import core

from fargate_task.fargate_task_stack import FargateTaskStack


app = core.App()
FargateTaskStack(app, "fargate-task")

app.synth()
