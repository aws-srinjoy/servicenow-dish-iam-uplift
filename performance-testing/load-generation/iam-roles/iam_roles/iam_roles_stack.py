from aws_cdk import core, aws_iam as iam


class IamRolesStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, start_index, end_index, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        iam_path="/"
        identity_provider_name="test"
        iam_create_role_managed_policy=iam.ManagedPolicy(
          self,
          "IAMCreateRolePolicy",
          description="AWS IAM Admnistrator create role managed policy",
          path=f"{iam_path}",
          statements=[
            iam.PolicyStatement(
              sid="AllowCreateRoleAndCreateUser",
              effect=iam.Effect.ALLOW,
              actions=[
                "iam:AttachRolePolicy",
                "iam:AttachUserPolicy",
                "iam:CreateAccessKey",
                "iam:CreatePolicy",
                "iam:CreatePolicyVersion",
                "iam:CreateRole",
                "iam:CreateUser",
                "iam:DeleteAccessKey",
                "iam:PutUserPolicy",
                "iam:UpdateUser"
              ],
              resources=[
                "arn:aws:iam::*:saml-provider/*",
                "arn:aws:iam::*:policy/*",
                "arn:aws:iam::*:user/*",
                "arn:aws:iam::*:role/*"
              ]
            ),
            iam.PolicyStatement(
              sid="AllowIAMReadAndList",
              effect=iam.Effect.ALLOW,
              actions=[
                "iam:Get*",
                "iam:List*",
              ],
              resources=[
                "*"
              ]
            ),
            iam.PolicyStatement(
              sid="AllowZelkova",
              effect=iam.Effect.ALLOW,
              actions=[
                "zelkova:checkPolicyProperty",
                "zelkova:comparePolicies",
              ],
              resources=[
                "*"
              ]
            ),
            iam.PolicyStatement(
              sid="AllowIAMSimulator",
              effect=iam.Effect.ALLOW,
              actions=[
                "iam:SimulatePrincipalPolicy",
                "iam:SimulateCustomPolicy",
              ],
              resources=[
                "*"
              ]
            ),
          ]
        )

        inline_policy_1 = iam.Policy(self, 'InlinePolicy1');
        defaultStatement = iam.PolicyStatement(effect=iam.Effect.ALLOW)
        defaultStatement.add_all_resources()
        permissions = [
          "sagemaker:*",
          "ecr:*",
          "cloudwatch:*",
          "logs:*",

          "s3:GetBucketLocation",
          "s3:ListAllMyBuckets",

          "iam:ListRoles",
          "iam:GetRole"
        ]
        defaultStatement.add_actions(*permissions)
        inline_policy_1.add_statements(defaultStatement);

        for i in range(start_index,end_index):
          self.create_role(i,iam_path,identity_provider_name,[iam_create_role_managed_policy],[inline_policy_1])


    def create_role(self, index, iam_path, identity_provider_name, managed_policies, inline_policies):  
        iam_administrator_sandbox=iam.Role(
          self,
          f"IAMRoleForLoadGeneration{index}",
          description="IAM Role for load generation testing",
          max_session_duration=core.Duration.hours(1),
          path=f"{iam_path}",
          assumed_by=iam.FederatedPrincipal(
            f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:saml-provider/{identity_provider_name}",
            conditions={
              "StringEquals": {
                "SAML:aud": "https://signin.aws.amazon.com/saml"
              }
            },
            assume_role_action="sts:AssumeRoleWithSAML"
          )
        )
        admin_managed_policy=iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        iam_administrator_sandbox.add_managed_policy(admin_managed_policy)

        iam_administrator_sandbox.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess"))
        iam_administrator_sandbox.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"))
        iam_administrator_sandbox.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"))
        iam_administrator_sandbox.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonMCSFullAccess"))

        for managed_policy in managed_policies:
          iam_administrator_sandbox.add_managed_policy(managed_policy)

        for inline_policy in inline_policies:
          iam_administrator_sandbox.attach_inline_policy(inline_policy)
