#!/usr/bin/env python3

from aws_cdk import core

from rds_instance_example.rds_instance_example_stack import RdsInstanceExampleStack


app = core.App()
stack = RdsInstanceExampleStack(app, "rds-instance-example-abac")
core.Tags.of(stack).add("Project", "test")

app.synth()
