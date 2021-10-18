import os

from aws_cdk import (
    core,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    pipelines,
    aws_codecommit as codecommit,
    aws_events_targets as events_targets,
    aws_events as events,
)

from .integration_tests_stage import SCPIntegrationTestsStage
from .integration_tests.integration_tests import IntegrationTests


class PipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs):
        BRANCH = props["BRANCH"] #self.node.try_get_context("branch") # branch_param.value_as_string  # "mainline"

        super().__init__(scope, f"{id}-{BRANCH}", **kwargs)

        PIPELINE_ACCOUNT_NUMBER = kwargs["env"]["account"]
        SOURCE_REGION = "us-east-1"
        # test_account_param.value_as_string  # "416368782481"
        TEST_ACCOUNT_NUMBER = props["TEST_ACCOUNT_NUMBER"] #self.node.try_get_context("test-account-number")

        # self.stack_name=f"{self.stack_name}-{BRANCH}"

        print(PIPELINE_ACCOUNT_NUMBER)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        repository = codecommit.Repository.from_repository_arn(
            self,
            "repo",
            f"arn:aws:codecommit:{SOURCE_REGION}:{PIPELINE_ACCOUNT_NUMBER}:IAM-Permissions-Guardrails",
        )

        build_environment = codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
            compute_type=codebuild.ComputeType.LARGE,
        )

        pipeline = pipelines.CdkPipeline(
            self,
            "Pipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name=f"scp-pipeline-{BRANCH}",
            source_action=cpactions.CodeCommitSourceAction(
                action_name="CodeCommit",
                output=source_artifact,
                repository=repository,
                branch=BRANCH,
            ),
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command="npm install -g aws-cdk && cdk version && pwd && ls && pip install --upgrade pip && pip install -r requirements.txt",
                # build_command="pytest unittests",
                synth_command="cdk synth",
                subdirectory="./service-control-policies/scp",
                environment=build_environment,
            ),
        )

        scp_stage_name = "scp-integration-tests-stage"
        scp_stack_name = f"role-hierarchy-scp-stack-{BRANCH}"
        scp_name = f"role-hierarchy-{BRANCH}"
        props = {
            "TEST_ACCOUNT_NUMBER": TEST_ACCOUNT_NUMBER,
            "ScpIntegrationTestsRoleName": "ScpIntegrationTestsRole",
            "LEVEL_KEY": "scp-testing-level-key",
            "LEVEL0": "level0",
            "LEVEL1": "level1",
            "LEVEL2": "level2",
            "LEVEL3": "level3",
            "INTEGRATION_TESTS_ROLE_LEVEL_VALUE": "level0",
            "PIPELINE_ACCOUNT_NUMBER": PIPELINE_ACCOUNT_NUMBER,
            "stack_name": scp_stack_name,
            "scp_name": scp_name,
            "BRANCH": BRANCH,
            "build_environment": build_environment,
            "source_artifact": source_artifact,
            "scp_stack_name": f"{scp_stage_name}-{scp_stack_name}",
            "SCP_NAME": scp_name,
        }

        scp_integration_test_stage = SCPIntegrationTestsStage(
            self,
            scp_stage_name,
            env={
                "account": PIPELINE_ACCOUNT_NUMBER,
                "region": "us-east-1",
            },
            props=props,
        )
        integrestion_testing_stage = pipeline.add_application_stage(
            scp_integration_test_stage
        )

        self.integration_tests = IntegrationTests(
            self,
            "IntegrationTests",
            props=props,
        )
        integrestion_testing_stage.add_actions(self.integration_tests.actions)

        target_codepipeline = events_targets.CodePipeline(
            pipeline=pipeline.code_pipeline
        )
        rule_schedule = events.Rule(
            self,
            "Daily",
            enabled=True,
            schedule=events.Schedule.rate(core.Duration.hours(1)),
        )
        rule_schedule.add_target(target=target_codepipeline)
