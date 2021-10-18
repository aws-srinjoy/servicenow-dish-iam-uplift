import json, os, subprocess
from pathlib import Path

from aws_cdk import (
    core,
    aws_iam as iam,
    aws_ssm,
    aws_config,
    aws_lambda,
    aws_events_targets as events_targets,
    aws_events as events,
)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class HumanIamUsersStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        max_credential_age_parameter = core.CfnParameter(
            self,
            "maxcredentialage",
            type="String",
            description="The maximum age for days since creation allowed for IAM user access keys",
            default="60",
        )

        max_credential_age = max_credential_age_parameter.value_as_string

        iam_user_remediation_policy_statements = [
            iam.PolicyStatement(
                actions=[
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
            description="IAM user automatic remediation lambda remediation policy",
            path="/",
            statements=iam_user_remediation_policy_statements,
        )
        iam_user_remediation_automation_role = iam.Role(
            self,
            "IAM-user-deactivation-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        iam_user_remediation_automation_role.add_managed_policy(
            iam_user_remediation_managed_policy
        )
        iam_user_remediation_automation_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        iam_user_remediation_automation_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole",
            )
        )

        iam_user_search_lambda_policy_statements = [
            iam.PolicyStatement(
                actions=[
                    "iam:ListUsers",
                    "iam:ListAccessKeys",
                ],
                resources=["*"],
            ),
        ]
        iam_user_search_lambda_managed_policy = iam.ManagedPolicy(
            self,
            "IAMUserRemediationLambdaPolicy",
            description="IAM user lambda remediation policy",
            path="/",
            statements=iam_user_search_lambda_policy_statements,
        )
        iam_user_search_role = iam.Role(
            self,
            "IAM-human-user-search-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        iam_user_search_role.add_managed_policy(iam_user_search_lambda_managed_policy)
        iam_user_search_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        iam_user_search_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole",
            )
        )

        """
        boto3_lambda_layer = self.create_dependencies_layer(
            id="boto3layer",
            requirements_path="./layers/boto3/requirements.txt",
            output_dir="./layers/boto3",
        )
        """

        iam_users_deactivation_function = self.create_lambda_function(
            boto3_lambda_layer=None,  # boto3_lambda_layer,
            source_path="./functions/deactivate-iam-user",
            identifier="iam-user-deactivation",
            is_inline=True,
            environment={
                # "SSM_ROLE": ssm_automation_role.role_arn,
                "MAX_CREDENTIAL_AGE": max_credential_age,
            },
            role=iam_user_remediation_automation_role,
        )

        human_iam_users_search_function = self.create_lambda_function(
            boto3_lambda_layer=None,  # boto3_lambda_layer,
            source_path="./functions/search-human-iam-user",
            identifier="human-iam-user-search",
            is_inline=True,
            environment={
                "DEACTIVATE_FUNCTION_NAME": iam_users_deactivation_function.function_name,
                "MAX_CREDENTIAL_AGE": max_credential_age,
            },
            role=iam_user_search_role,
        )
        # human_iam_users_search_function.grant_invoke(iam_users_remediation_function)

        iam_user_search_role.add_to_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[iam_users_deactivation_function.function_arn],
            ),
        )

        rule_schedule = events.Rule(
            self,
            "Daily",
            enabled=True,
            schedule=events.Schedule.rate(core.Duration.hours(24)),
        )
        target_lambda = events_targets.LambdaFunction(human_iam_users_search_function)
        rule_schedule.add_target(target=target_lambda)

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
            timeout=core.Duration.minutes(3),
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
