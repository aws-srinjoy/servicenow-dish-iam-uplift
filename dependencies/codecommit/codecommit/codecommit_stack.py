from aws_cdk import (
    core,
    aws_codecommit as codecommit,
    aws_codegurureviewer as codegurureviewer,
    aws_iam as iam,
)


class CodecommitStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo = codecommit.Repository(
            self,
            "iam-permissions-guardrails",
            repository_name="IAM-Permissions-Guardrails",
            description="IAM Permissions Guardrails",
        )

        codegurureviewer.CfnRepositoryAssociation(
            self, "codegurureviewer", name=repo.repository_name, type="CodeCommit"
        )

