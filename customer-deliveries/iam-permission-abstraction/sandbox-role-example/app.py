#!/usr/bin/env python3

from aws_cdk import core

from sandbox_role_example.sandbox_role_example_stack import SandboxRoleExampleStack


app = core.App()
SandboxRoleExampleStack(app, "sandbox-role-example")

app.synth()
