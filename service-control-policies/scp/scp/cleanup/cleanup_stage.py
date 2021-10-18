from aws_cdk import core

from .cleanup_stack import TestingRoleCleanupStack


class TestingRoleCleanupStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs):
        super().__init__(scope, id, **kwargs)

        TestingRoleCleanupStack(self, "integration-tests--role-cleanup-stack", props)
