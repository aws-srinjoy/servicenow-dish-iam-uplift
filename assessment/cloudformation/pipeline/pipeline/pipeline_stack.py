from aws_cdk import (
    core,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_s3 as s3,
    aws_ecr as ecr,
)


class PipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # https://github.com/aws-samples/aws-cdk-examples/blob/ffda295e6f7b2cb1776661a7284dc3b16ee0496c/python/codepipeline-docker-build/Base.py

        namespace = "iam-permissions-guardrails"

        # pipeline requires versioned bucket
        bucket = s3.Bucket(
            self,
            "SourceBucket",
            bucket_name=f"{namespace}-{core.Aws.ACCOUNT_ID}-{core.Aws.REGION}",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        # ecr repo to push docker container into
        ecr_repo = ecr.Repository(
            self,
            "ECR",
            repository_name=f"{namespace}",
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        repo = codecommit.Repository(
            self,
            "IAMPermissionsGuardrailsRepo",
            repository_name="IAM-Permissions-Guardrails",
            description="IAM Permissions Guardrails",
        )

        # codebuild project meant to run in pipeline
        cb_docker_build = codebuild.PipelineProject(
            self,
            "DockerBuild",
            project_name=f"{namespace}-Docker-Build",
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename="docker_build_buildspec.yml"
            ),
            environment=codebuild.BuildEnvironment(
                privileged=True,
            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                "ecr": codebuild.BuildEnvironmentVariable(
                    value=ecr_repo.repository_uri
                ),
                "tag": codebuild.BuildEnvironmentVariable(value="latest"),
            },
            description="Pipeline for CodeBuild",
            timeout=core.Duration.minutes(60),
        )
        # codebuild iam permissions to read write s3
        bucket.grant_read_write(cb_docker_build)

        # codebuild permissions to interact with ecr
        ecr_repo.grant_pull_push(cb_docker_build)

        source_output = codepipeline.Artifact(artifact_name="source")
        cdk_build_output = codepipeline.Artifact("CdkBuildOutput")
        codepipeline.Pipeline(
            self,
            "Pipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.CodeCommitSourceAction(
                            action_name="CodeCommit_Source",
                            repository=repo,
                            branch="mainline",
                            output=source_output,
                        )
                    ],
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="docker-image-build",
                            project=cb_docker_build,
                            input=source_output,
                            outputs=[cdk_build_output],
                        )
                    ],
                ),
            ],
        )

        core.CfnOutput(
            self,
            "ECRURI",
            description="ECR URI",
            value=ecr_repo.repository_uri,
        )
        core.CfnOutput(
            self, "S3Bucket", description="S3 Bucket", value=bucket.bucket_name
        )
