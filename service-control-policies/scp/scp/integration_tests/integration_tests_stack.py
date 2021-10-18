from aws_cdk import core, aws_iam as iam

from .integration_tests import IntegrationTests


class IntegrationTestsStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.integration_tests = IntegrationTests(
            self,
            "IntegrationTests",
            props,
        )
