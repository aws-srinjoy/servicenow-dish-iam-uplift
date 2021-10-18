#!/usr/bin/env python3

from aws_cdk import core

from iam_roles.iam_roles_stack import IamRolesStack


app = core.App()
for i in range(10):
  IamRolesStack(app, f"iam-roles-{i}",1+(i*100),100+(i*100))

app.synth()
