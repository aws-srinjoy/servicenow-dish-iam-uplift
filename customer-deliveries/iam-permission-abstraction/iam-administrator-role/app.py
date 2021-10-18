#!/usr/bin/env python3

from aws_cdk import core

from iam_administrator_role.iam_administrator_role_stack import IamAdministratorRoleStack


app = core.App()
IamAdministratorRoleStack(app, "iam-administrator-role")

app.synth()
