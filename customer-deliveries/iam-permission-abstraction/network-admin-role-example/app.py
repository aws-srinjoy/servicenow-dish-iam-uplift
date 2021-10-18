#!/usr/bin/env python3

from aws_cdk import core

from network_admin_role_example_administrator_stack import NetworkAdminRoleExampleAdministratorStack
from network_admin_role_example_readonly import NetworkAdminRoleExampleReadOnlyStack

app = core.App()
NetworkAdminRoleExampleAdministratorStack(app, "network-admin-role-example-administrator")
NetworkAdminRoleExampleReadOnlyStack(app, "network-admin-role-example-readonly")

app.synth()
