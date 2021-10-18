import os, subprocess
import json

import boto3

from aws_cdk import core as cdk
from aws_cdk import (
    core,
    aws_config,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_cloudformation as cfn,
    cloudformation_include as cfn_inc,
)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class IamRoleLastUsedStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        max_days_for_last_used_role_parameter = cdk.CfnParameter(
            self,
            "MaxDaysForLastUsedRole",
            type="String",
            description="Max days that a role can be unused before being marked as noncompliant.",
            default="60",
        )
        
        max_days_for_last_used_role_value = (
            max_days_for_last_used_role_parameter.value_as_string
        )

        #ONE_HOUR 1 hour. SIX_HOURS 6 hours. THREE_HOURS 3 hours. TWELVE_HOURS 12 hours. TWENTY_FOUR_HOURS 24 hours.
        maximum_execution_frequency_parameter = cdk.CfnParameter(
            self,
            "MaximumExecutionFrequency",
            type="String",
            description="The maximum frequency at which the AWS Config rule runs evaluations.",
            default="One_Hour",
        )

        maximum_execution_frequency_value = maximum_execution_frequency_parameter.value_as_string
        
        access_level_value_key_parameter = cdk.CfnParameter(
            self,
            "AccessLevelKey",
            type="String",
            description="Access level tag key for the iam last used IAM role",
            default="access-level",
        )
        access_level_key_value = access_level_value_key_parameter.value_as_string

        builder_access_level_value_parameter = cdk.CfnParameter(
            self,
            "LambdaRoleAccessLevelValue",
            type="String",
            description="Access level tag value for the lambda role. This is the role attached to the Lambda. The default corresponds to the builder level of 2 when 4 levels are used.",
            default="2",
        )
        builder_access_level_value = (
            builder_access_level_value_parameter.value_as_string
        )

        execution_access_level_value_parameter = cdk.CfnParameter(
            self,
            "ExecutionRoleAccessLevelValue",
            type="String",
            description="Access level tag value for the execution role  role. This is the execution role that the config rule will assume to run the evaluations and update the configuration items. The default corresponds to the builder level of 3 when 4 levels are used.",
            default="3",
        )
        execution_access_level_value = (
            execution_access_level_value_parameter.value_as_string
        )

        function_name = "find-unused-iam-roles"
        find_last_used_roles_iam_execution_role = (
            "find-last-used-roles-iam-execution-role"
        )

        organizations_client = boto3.client("organizations")
        root = organizations_client.list_roots()["Roots"][0]
        root_id = root["Id"]
        root_account_id = root["Arn"].split(":")[4]

        lambda_role = iam.Role(
            self,
            f"{function_name}-role",
            # role_name="find-unused-iam-roles",
            description="Find unused IAM roles role",
            path="/",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        cdk.Tags.of(lambda_role).add(access_level_key_value, builder_access_level_value)

        # deploys the cfn template as part of this cdk stack. StackSet doesn't deploy to management account, so we include it here
        iam_execution_role_template = cfn_inc.CfnInclude(
            self,
            "iam-execution-role-management-account",
            template_file="iam-role.yaml",
            parameters={
                "pAccessLevelKey": access_level_key_value,
                "pExecutionRoleAccessLevelValue": execution_access_level_value,
                "pManagementAccountId": root_account_id,
                "pIAMRoleLastUsedName": lambda_role.role_name,
            },
        )

        # deploys cfn as stackset to all accounts within organization (though not management account)
        with open("iam-role.yaml", "r") as myfile:
            iam_execution_role_cfn = myfile.read()

        cfn.CfnStackSet(
            self,
            "iam-execution-role-stack-set",
            permission_model="SERVICE_MANAGED",
            stack_set_name=f"{function_name}-iam-execution-role-stack-set",
            auto_deployment=cfn.CfnStackSet.AutoDeploymentProperty(
                enabled=True,
                retain_stacks_on_account_removal=False,
            ),
            capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            description=f"iam execution role for {function_name}",
            stack_instances_group=[
                cfn.CfnStackSet.StackInstancesProperty(
                    regions=["us-east-1"],
                    deployment_targets=cfn.CfnStackSet.DeploymentTargetsProperty(
                        organizational_unit_ids=[root_id],
                    ),
                ),
            ],
            operation_preferences=cfn.CfnStackSet.OperationPreferencesProperty(
                failure_tolerance_count=5,
                max_concurrent_percentage=100,
            ),
            template_body=iam_execution_role_cfn,
            parameters=[
                cfn.CfnStackSet.ParameterProperty(
                    parameter_key="pAccessLevelKey",
                    parameter_value=access_level_key_value,
                ),
                cfn.CfnStackSet.ParameterProperty(
                    parameter_key="pExecutionRoleAccessLevelValue",
                    parameter_value=execution_access_level_value,
                ),
                cfn.CfnStackSet.ParameterProperty(
                    parameter_key="pManagementAccountId",
                    parameter_value=root_account_id,
                ),
                cfn.CfnStackSet.ParameterProperty(
                    parameter_key="pIAMRoleLastUsedName",
                    parameter_value=lambda_role.role_name,
                ),
            ],
        )

        code_path = os.path.join("functions", "iam_role_last_used")

        lambda_layer = self.create_dependencies_layer(
            id="lambdalayer",
            requirements_path=os.path.join(code_path, "requirements.txt"),
            output_dir="./lambda_layer",
        )
        lambda_code = _lambda.Code.asset(code_path)
        lambda_handler = "app.lambda_handler"

        lambda_function = _lambda.Function(
            self,
            "find-unused-iam-roles-lambda",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=lambda_code,
            layers=[lambda_layer],
            handler=lambda_handler,
            role=lambda_role,
            # function_name=function_name,
            description="finds unused iam roles",
            retry_attempts=2,
            timeout=core.Duration.minutes(2),
        )

        accounts = []
        paginator = organizations_client.get_paginator("list_accounts")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for acct in page["Accounts"]:
                accounts.append(acct)

        for account in accounts:
            lambda_function.add_permission(
                f"config-invoke-by-{account['Id']}",
                principal=iam.ServicePrincipal(
                    service="config.amazonaws.com",
                ),
                source_account=account["Id"],
            )

        lambda_policy = iam.ManagedPolicy(
            self,
            f"{function_name}-policy",
            description="Unused iam roles policy",
            path="/",
            statements=[
                iam.PolicyStatement(
                    sid="CloudWatchLogs",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    # get a circular dependency, use the stack name as the log group prefix
                    # f"{lambda_function.log_group.log_group_arn}",
                    resources=[
                        f"arn:aws:logs:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:log-group:/aws/lambda/{self.stack_name}*:*",
                    ],
                ),
                iam.PolicyStatement(
                    sid="AssumeRoles",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sts:AssumeRole",
                    ],
                    resources=[
                        f"arn:aws:iam::*:role/{find_last_used_roles_iam_execution_role}",
                    ],
                ),
                iam.PolicyStatement(
                    sid="SNSPublish",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sns:Publish",
                        "sns:ListTopics",
                    ],
                    resources=[
                        "arn:aws:sns:*:*:*",
                    ],
                ),
            ],
        )
        lambda_role.add_managed_policy(lambda_policy)
        cdk.Tags.of(lambda_policy).add(
            access_level_key_value, builder_access_level_value
        )

        rule_input_parameters = {
            "ExecutionRoleName": find_last_used_roles_iam_execution_role,
            "max_days_for_last_used": max_days_for_last_used_role_value,
        }

        # need to use periodic and make an api call to get account authorization details,
        # as the config configuration item doesn't contain the last used region
        # and is also not updated when the role is used
        rule = aws_config.CfnOrganizationConfigRule(
            self,
            f"find-unused-iam-roles",
            organization_config_rule_name="find-unused-iam-roles",
            organization_custom_rule_metadata={
                "description": f"Finds unused IAM roles",
                "lambdaFunctionArn": lambda_function.function_arn,
                "organizationConfigRuleTriggerTypes": ["ScheduledNotification"],
                "inputParameters": json.dumps(rule_input_parameters),
                # "maximum_execution_frequency": "One_Hour",
                "maximum_execution_frequency": aws_config.MaximumExecutionFrequency.ONE_HOUR,
                "resourceTypesScope": ["AWS::IAM::Role"],
            },
        )

    """
    Performs a local pip install to create a folder of the dependencies.
    CDK will then bundle the layer folder, create assets zip, create hash, and upload to the assets zip to the s3 bucket to create the layer.
    https://github.com/aws-samples/aws-cdk-examples/issues/130
    """

    def create_dependencies_layer(
        self, id: str, requirements_path: str, output_dir: str
    ) -> _lambda.LayerVersion:
        # Install requirements for layer
        if not os.environ.get("SKIP_PIP"):
            subprocess.check_call(
                # Note: Pip will create the output dir if it does not exist
                f"pip install -r {requirements_path} -t {output_dir}/python".split()
            )
        return _lambda.LayerVersion(self, id, code=_lambda.Code.from_asset(output_dir))
