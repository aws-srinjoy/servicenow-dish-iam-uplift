#https://aws.amazon.com/premiumsupport/knowledge-center/restrict-launch-tagged-ami/
from aws_cdk import (
  core,
  aws_iam as iam
)


class Ec2ServiceEngineeringStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        max_session_duration=1

        ec2serviceengineering="serviceengineering/ec2"
        ec2serviceengineeringdev="developer"

        ec2_service_engineering_path_parameter=core.CfnParameter(self,
          "EC2ServiceEngineeringPathName",
          default=ec2serviceengineering,
          description="EC2 Service Engineering Path Name"
        )

        ec2_service_engineering_path=ec2_service_engineering_path_parameter.value_as_string

        ec2_service_engineering_development_sub_path_parameter=core.CfnParameter(self,
          "EC2ServiceEngineeringDevelopmentPathName",
          default=ec2serviceengineeringdev,
          description="EC2 Service Engineering Path Name"
        )

        ec2_service_engineering_development_sub_path=ec2_service_engineering_development_sub_path_parameter.value_as_string

        #substituded in the arn:aws:iam::123456789234:saml-provider/IdentityProviderName
        identity_provider_name_parameter=core.CfnParameter(self,
          "IdentityProviderName",
          description="Identity Provider SAML Name"
        )

        identity_provider_name=identity_provider_name_parameter.value_as_string

        ec2_service_engineering_development_policy=iam.ManagedPolicy(
          self,
          "CreateRoleEC2ServiceEngineeringDelegatedAdmin",
          managed_policy_name="CreateRoleEC2ServiceEngineeringDelegatedAdmin",
          description="EC2 Service Engineering Delegated Admin",
          path=f"/{ec2_service_engineering_path}/",
          statements=[
            iam.PolicyStatement(
              sid="CreateRoleEC2ServiceEngineering",
              effect=iam.Effect.ALLOW,
              actions=[
                    "iam:CreateRole",
                    "iam:PutRolePolicy",
                    "iam:PutRolePermissionsBoundary",
              ],
              resources=[
                f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:role/{ec2_service_engineering_path}/{ec2_service_engineering_development_sub_path}/*"
              ],
              conditions={
                "StringEquals": {
                  "iam:PermissionsBoundary":f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:policy/{ec2_service_engineering_path}/CreateRoleEC2ServiceEngineeringDelegatedAdmin",
                }
              }
            ),
            iam.PolicyStatement(
              sid="ModifyRoleEC2ServiceEngineering",
              effect=iam.Effect.ALLOW,
              actions=[
                    "iam:UpdateRole",
                    "iam:UpdateRoleDescription"
              ],
              resources=[
                f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:role/{ec2_service_engineering_path}/{ec2_service_engineering_development_sub_path}/*"
              ],
            ),
            iam.PolicyStatement(
              sid="ModifyRolePolicyEC2ServiceEngineeringDeveloper",
              effect=iam.Effect.ALLOW,
              actions=[
                    "iam:AttachRolePolicy",
                    "iam:DetachRolePolicy"
              ],
              resources=[
                f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:role/{ec2_service_engineering_path}/{ec2_service_engineering_development_sub_path}/*"
              ],
              conditions={
                "StringEquals": {
                  "iam:PolicyARN":f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:policy/{ec2_service_engineering_path}/{ec2_service_engineering_development_sub_path}/*"
                },
                "StringEquals": {
                  "iam:PermissionsBoundary":f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:role/{ec2_service_engineering_path}/{ec2_service_engineering_development_sub_path}/*"
                }
              },
            ),
            iam.PolicyStatement(
              sid="EC2DeveloperPassRoleActions",
              effect=iam.Effect.ALLOW,
              actions=[
                    "iam:PassRole",
              ],
              resources=[
                f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:role/{ec2_service_engineering_path}/{ec2_service_engineering_development_sub_path}/*"
              ],
              conditions={
                "StringLike": {
                  "iam:AssociatedResourceArn": [
                    f"arn:aws:ec2:us-east-1:{core.Aws.ACCOUNT_ID}:instance/*"
                  ]
                },
                "StringEquals": {
                  "iam:PassedToService":"ec2.amazonaws.com"
                },
              }
            ),
            iam.PolicyStatement(
              sid="EC2ReadOnly",
              effect=iam.Effect.ALLOW,
              actions=[
                "ec2:Describe*",
                "ec2:GetConsole*",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:GetMetricStatistics",
                "iam:ListInstanceProfiles"
              ],
              resources=[
                "*"
              ],
            ),
            iam.PolicyStatement(
              sid="EC2DeveloperActions",
              effect=iam.Effect.ALLOW,
              actions=[
                    "ec2:RunInstances",
              ],
              resources=[
                "arn:aws:ec2:us-east-1:AccountId:instance/*",
                "arn:aws:ec2:us-east-1:AccountId:key-pair/*",
                "arn:aws:ec2:us-east-1:AccountId:security-group/*",
                "arn:aws:ec2:us-east-1:AccountId:volume/*",
                "arn:aws:ec2:us-east-1:AccountId:network-interface/*",
                "arn:aws:ec2:us-east-1:AccountId:subnet/*",
                "arn:aws:ec2:us-east-1::image/*"
              ],
            )
          ]
        )

        federated_principal=iam.FederatedPrincipal(
            f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:saml-provider/{identity_provider_name}",
            conditions={
              "StringEquals": {
                "SAML:aud": "https://signin.aws.amazon.com/saml"
              }
            },
            assume_role_action="sts:AssumeRoleWithSAML"
        )

        ec2_service_engineering_role=iam.Role(
          self,
          "EC2ServiceEngineeringRole",
          #role_name="EC2ServiceEngineeringRole",
          description="EC2ServiceEngineeringRole",
          max_session_duration=core.Duration.hours(max_session_duration),
          path=f"/{ec2_service_engineering_path}/",
          assumed_by=federated_principal,
        )

        ec2_service_engineering_role.add_managed_policy(ec2_service_engineering_development_policy)
