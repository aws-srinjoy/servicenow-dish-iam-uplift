import os.path

dirname = os.path.dirname(__file__)

from aws_cdk import (
    core,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_iam as iam,
)


class TestingRoleCleanupStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        integration_tests_code_build = codebuild.PipelineProject(
            self,
            "RoleCleanup",
            build_spec=codebuild.BuildSpec.from_source_filename(
                # os.path.join(dirname, "buildspec.yaml")
                "./service-control-policies/scp/scp/cleanup/buildspec.yaml"
            ),
            environment=props["build_environment"],
            environment_variables={
                "SCP_INTEGRATION_TESTS_ROLE_NAME": codebuild.BuildEnvironmentVariable(
                    value=props["ScpIntegrationTestsRoleName"]
                ),
            },
        )
        iam_sts_actions = iam.PolicyStatement(
            # sid="CloudWatchLogs",
            effect=iam.Effect.ALLOW,
            actions=["cloudformation:*"],
            resources=["*"],
        )

        integration_tests_code_build.add_to_role_policy(iam_sts_actions)

        integration_tests_output = codepipeline.Artifact("IntegrationTestsOutput")
        integration_tests_actions = cpactions.CodeBuildAction(
            action_name="Run_Integration_Tests",
            project=integration_tests_code_build,
            input=props["source_artifact"],
            outputs=[integration_tests_output],
        )

        self.actions = integration_tests_actions
