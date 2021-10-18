from aws_cdk import (
    core,
    aws_iam as iam,
)


class ScpIntegrationTestsRoleStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        scp_integration_tests_role = iam.Role(
            self,
            "ScpIntegrationTestsRole",
            role_name=props["ScpIntegrationTestsRoleName"],
            description="SCP integration tests role",
            path="/",
            assumed_by=iam.AccountPrincipal(props["PIPELINE_ACCOUNT_NUMBER"]),
        )

        scp_integration_tests_policy = iam.Policy(
            self,
            "ScpIntegrationTestsPolicy",
            statements=[
                iam.PolicyStatement(
                    sid="IAMandSTS",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "iam:*",
                        "sts:AssumeRole",
                    ],
                    resources=["*"],
                ),
            ],
        )

        scp_integration_tests_role.attach_inline_policy(scp_integration_tests_policy)

        core.Tags.of(scp_integration_tests_role).add(
            props["LEVEL_KEY"], props["INTEGRATION_TESTS_ROLE_LEVEL_VALUE"]
        )
