from aws_cdk import (core,
                     aws_iam as iam)


class IamAdministratorRoleStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    identity_provider_name_parameter=core.CfnParameter(self,
      "IdentityProviderName",
      description="Identity Provider SAML Name"
      #substituded in arn:aws:iam::123456789234:saml-provider/IdentityProviderName
    )

    iam_path_parameter=core.CfnParameter(self,
      "IAMPath",
      default="/",
      description="IAM Path"
    )

    iam_path=iam_path_parameter.value_as_string
    identity_provider_name=identity_provider_name_parameter.value_as_string

    iam_create_role_managed_policy=iam.ManagedPolicy(
      self,
      "IAMCreateRolePolicy",
      managed_policy_name="IAMAdministrator",
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
            "iam:GetAccessKeyLastUsed",
            "iam:GetPolicyVersion",
            "iam:GetRole",
            "iam:GetRolePolicy",
            "iam:GetSAMLProvider",
            "iam:GetUser",
            "iam:GetUserPolicy",
            "iam:ListAccessKeys",
            "iam:ListAttachedRolePolicies",
            "iam:ListAttachedUserPolicies",
            "iam:ListRolePolicies",
            "iam:ListRoleTags",
            "iam:ListUserPolicies",
            "iam:ListUserTags",
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
      ]
    )

    iam_administrator_sandbox=iam.Role(
      self,
      "IAMSandboxAdministrator",
      role_name="IAMSandboxAdministrator",
      description="AWS IAM Sandbox Administrator Role to create IAM Foundational Roles",
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

    iam_administrator_sandbox.add_to_policy(
        iam.PolicyStatement(
          sid="DenyUpdatingIAMSandboxAdministratorRole",
          effect=iam.Effect.DENY,
          actions=[
            "iam:AttachRolePolicy",
            "iam:DeleteRolePolicy",
            "iam:DetachRolePolicy",
            "iam:PutRolePermissionsBoundary",
            "iam:PutRolePolicy",
            "iam:UpdateAssumeRolePolicy"
          ],
          resources=[
            iam_administrator_sandbox.role_arn
          ]
        )
    )

    iam_administrator_sandbox.add_to_policy(
        iam.PolicyStatement(
          sid="DenyUpdatingIAMSandboxAdministratorManagedPolicy",
          effect=iam.Effect.DENY,
          actions=[
            "iam:DeletePolicy",
            "iam:SetDefaultPolicyVersion"
          ],
          resources=[
            iam_create_role_managed_policy.managed_policy_arn
          ]
        )
    )

    iam_administrator_sandbox.add_managed_policy(iam_create_role_managed_policy)              
