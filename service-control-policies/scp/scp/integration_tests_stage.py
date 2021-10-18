from aws_cdk import core

from .integration_tests.role_stack import ScpIntegrationTestsRoleStack

from .role_hierarchy.scp_stack import ScpStack

from .integration_tests.integration_tests_stack import IntegrationTestsStack


class SCPIntegrationTestsStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs):
        super().__init__(scope, id, **kwargs)

        # The integration test role is created before creating and attaching the SCP
        scp_integration_tests_role_stack = ScpIntegrationTestsRoleStack(
            self,
            "ScpIntegrationTestsRoleStack",
            props,
            env={
                "account": props["TEST_ACCOUNT_NUMBER"],
                "region": "us-east-1",
            },
        )

        scp_stack = ScpStack(
            self,
            props["stack_name"],
            props,
            env={
                "account": props["PIPELINE_ACCOUNT_NUMBER"],
                "region": "us-east-1",
            },
        )
        scp_stack.add_dependency(scp_integration_tests_role_stack)

        """
        self.integration_tests_stack = IntegrationTestsStack(
            self,
            "IntegrationTestsStack",
            props,
            env={
                "account": props["PIPELINE_ACCOUNT_NUMBER"],
                "region": "us-east-1",
            },
        )
        """
