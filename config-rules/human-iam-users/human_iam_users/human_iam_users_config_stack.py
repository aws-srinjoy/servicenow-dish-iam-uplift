import json, os, subprocess
from pathlib import Path

from aws_cdk import core, aws_iam as iam, aws_ssm, aws_config, aws_lambda

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from cfn_flip import to_json


class HumanIamUsersStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        max_credential_age = "0"

        iam_user_unsed_credentials_config_rule = aws_config.ManagedRule(
            self,
            id="iam_user_unused_credentials_config_rule",
            identifier="IAM_USER_UNUSED_CREDENTIALS_CHECK",
            input_parameters={"maxCredentialUsageAge": max_credential_age},
        )

        # https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-aws-revoke-iam-user.html
        ssm_policy_statements = [
            iam.PolicyStatement(
                actions=[
                    "ssm:StartAutomationExecution",
                    "ssm:GetAutomationExecution",
                    "config:ListDiscoveredResources",
                    "iam:DeleteAccessKey",
                    "iam:DeleteLoginProfile",
                    "iam:GetAccessKeyLastUsed",
                    "iam:GetLoginProfile",
                    "iam:GetUser",
                    "iam:ListAccessKeys",
                    "iam:UpdateAccessKey",
                ],
                resources=["*"],
            ),
        ]
        iam_user_remediation_managed_policy = iam.ManagedPolicy(
            self,
            "IAMUserRemediationPolicy",
            description="IAM user ssm remediation policy",
            path="/",
            statements=ssm_policy_statements,
        )
        ssm_automation_role = iam.Role(
            self,
            "IAM-user-remediation-role",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
        )
        ssm_automation_role.add_managed_policy(iam_user_remediation_managed_policy)

        iam_user_remediation_lambda_policy_statements = [
            iam.PolicyStatement(
                actions=[
                    "ssm:StartAutomationExecution",
                    "ssm:GetAutomationExecution",
                    "iam:ListUsers",
                    "iam:ListAccessKeys",
                    "iam:PassRole",
                ],
                resources=["*"],
            ),
            iam.PolicyStatement(
                actions=[
                    "iam:PassRole",
                ],
                resources=[ssm_automation_role.role_arn],
            ),
        ]
        iam_user_remediation_lambda_managed_policy = iam.ManagedPolicy(
            self,
            "IAMUserRemediationLambdaPolicy",
            description="IAM user lambda remediation policy",
            path="/",
            statements=iam_user_remediation_lambda_policy_statements,
        )
        lambda_automation_role = iam.Role(
            self,
            "IAM-user-lambda-remediation-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_automation_role.add_managed_policy(
            iam_user_remediation_lambda_managed_policy
        )
        lambda_automation_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        lambda_automation_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole",
            )
        )

        systemmanagerdoc = "ssm.yaml"
        ssm_yaml = Path(systemmanagerdoc).read_text()
        ssm_json = json.loads(to_json(ssm_yaml))

        ssmdoc = aws_ssm.CfnDocument(
            self, "remediate-iam-users", content=ssm_json, document_type="Automation"
        )

        iam_user_remediation = aws_config.CfnRemediationConfiguration(
            self,
            "human-iam-user-remediation",
            config_rule_name=iam_user_unsed_credentials_config_rule.config_rule_name,
            target_id=ssmdoc.ref,
            target_type="SSM_DOCUMENT",
            automatic=False,
            parameters={
                "AutomationAssumeRole": {
                    "StaticValue": {"Values": [ssm_automation_role.role_arn]}
                },
                "MaxCredentialUsageAge": {
                    "StaticValue": {"Values": [max_credential_age]}
                },
                "IAMResourceId": {"ResourceValue": {"Value": "RESOURCE_ID"}},
            },
            resource_type="AWS::IAM::User",
            target_version="1",
        )

        boto3_lambda_layer = self.create_dependencies_layer(
            id="boto3layer",
            requirements_path="./layers/boto3/requirements.txt",
            output_dir="./layers/boto3",
        )

        is_inline = False

        human_iam_users_remeidation_function = self.create_lambda_function(
            boto3_lambda_layer,
            "./functions/remediate-human-iam-user",
            "test",
            is_inline,
            environment={"SSM_ROLE": ssm_automation_role.role_arn},
            role=lambda_automation_role,
        )

        iam_user_remediation.node.add_dependency(human_iam_users_remeidation_function)
        iam_user_remediation.node.add_dependency(iam_user_unsed_credentials_config_rule)

    def create_lambda_function(
        self,
        boto3_lambda_layer,
        source_path,
        identifier,
        is_inline,
        environment={},
        role=None,
    ):
        lambda_function = None
        lambda_code = None
        lambda_handler = None
        if is_inline:
            with open(f"{source_path}/app.py", encoding="utf8") as fp:
                handler_code = fp.read()
                lambda_code = aws_lambda.InlineCode(handler_code)
                lambda_handler = "index.handler"
        else:
            lambda_code = aws_lambda.AssetCode(source_path)
            lambda_handler = "app.handler"

        lambda_function = aws_lambda.Function(
            self,
            identifier,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler=lambda_handler,
            code=lambda_code,
            environment=environment,
            role=role,
        )
        if boto3_lambda_layer:
            lambda_function.add_layers(boto3_lambda_layer)
        return lambda_function

    # https://github.com/aws-samples/aws-cdk-examples/issues/130
    def create_dependencies_layer(
        self, id: str, requirements_path: str, output_dir: str
    ) -> aws_lambda.LayerVersion:
        # Install requirements for layer
        if not os.environ.get("SKIP_PIP"):
            subprocess.check_call(
                # Note: Pip will create the output dir if it does not exist
                f"pip install -r {requirements_path} -t {output_dir}/python".split()
            )
        return aws_lambda.LayerVersion(
            self, id, code=aws_lambda.Code.from_asset(output_dir)
        )
