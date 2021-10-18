#!/usr/bin/env python3

from aws_cdk import core

from create_test_iam_roles.create_test_iam_roles_stack import CreateTestIamRolesStack


app = core.App()
for number in range(40):
    CreateTestIamRolesStack(app, f"create-test-iam-roles-{number}")

app.synth()
