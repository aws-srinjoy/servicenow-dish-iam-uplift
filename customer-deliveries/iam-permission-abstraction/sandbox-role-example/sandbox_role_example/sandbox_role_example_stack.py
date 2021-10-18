from aws_cdk import (
core,
aws_iam as iam
)


class SandboxRoleExampleStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    trusted_cidrs_parameter=core.CfnParameter(self,
      "TrustedCidrRanges",
      description="Trusted CIDR Ranges",
      type="CommaDelimitedList"
    )

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

    """
    application_roles_iam_path=core.CfnParameter(self,
      "ApplicationRolesIAMPath",
      default="/applicationroles",
      description="Applicaiton Roles IAM Path"
    )
    """

    max_session_duration=1
    trusted_cidrs=trusted_cidrs_parameter.value_as_list
    iam_path=iam_path_parameter.value_as_string
    application_roles_iam_path="sandbox"
    identity_provider_name=identity_provider_name_parameter.value_as_string


    sandbox_managed_policy=iam.ManagedPolicy(
      self,
      "SandboxManagedPolicy",
      managed_policy_name="Sandbox",
      description="Sandbox Managed Policy",
      path=iam_path,
      statements=[
        iam.PolicyStatement(
          sid="IAMSandbox",
          effect=iam.Effect.ALLOW,
          actions=[
                "iam:List*",
                "iam:GetPolicyVersion",
                "iam:GetAccountPasswordPolicy",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "iam:SimulateCustomPolicy",
                "iam:SimulatePrincipalPolicy",
                "iam:GetCredentialReport",
                "iam:ListPolicies",
                "iam:GetRole",
                "iam:GetPolicy",
                "iam:GetRolePolicy",
                "iam:GetAccountSummary",
                "iam:CreateInstanceProfile",
                "iam:GetServiceLastAccessedDetailsWithEntities",
                "iam:GetServiceLastAccessedDetails",
                "iam:GetServiceLinkedRoleDeletionStatus",
                "iam:GetSAMLProvider",
                "iam:GetInstanceProfile",
                "iam:GetLoginProfile",
          ],
          resources=[
            "*"
          ]
        ),
        #should be scoped to specific path and tags?
        iam.PolicyStatement(
          sid="IAMSandboxRestrictedUpdates",
          effect=iam.Effect.ALLOW,
          actions=[
                "iam:TagRole", 
                "iam:UntagRole",
                "iam:DeleteRole" 
          ],
          resources=[
            f"arn:aws:iam::*:role/{application_roles_iam_path}/*"
          ]
        ),
        iam.PolicyStatement(
          sid="WhitelistedSandboxServices",
          effect=iam.Effect.ALLOW,
          actions=[
                "s3:*",
                "ec2:*",
                "ec2messages:*",
                "elasticache:*",
                "secretsmanager:*",
                "waf:*",
                "eks:*",
                "elasticloadbalancing:*",
                "autoscaling:*",
                "ssm:*",
                "ssmmessages:*",
                "cloudwatch:*",
                "cloudtrail:*"
          ],
          resources=[
            "*"
          ]
        ),
        iam.PolicyStatement(
          sid="PassRoleRestrictionSandbox",
          effect=iam.Effect.ALLOW,
          actions=[
            "iam:PassRole"
          ],
          #FIX path name to be passed
          resources=[
            f"arn:*:iam::*:role/{application_roles_iam_path}/*"
          ],
          conditions={
            "StringEquals": {
              "iam:PassedToService": "ec2.amazonaws.com"
            }
          }
        ),
        iam.PolicyStatement(
          sid="DenyNonNetworkPerimeter",
          effect=iam.Effect.DENY,
          actions=[
            "*"
          ],
          resources=[
            "*"
          ],
          conditions={
            "NotIpAddress": {
              "aws:SourceIp": trusted_cidrs
            }
          }
        ),                        
      ]
    )
   
    create_role_sandbox=iam.ManagedPolicy(
      self,
      "CreateRoleSandbox",
      managed_policy_name="CreateRoleSandbox",
      description="Create Role Sandbox",
      path=iam_path,
      statements=[
        iam.PolicyStatement(
          sid="CreateRoleSandbox",
          effect=iam.Effect.ALLOW,
          actions=[
                "iam:CreateRole",
                "iam:UpdateRole",
                "iam:PutRolePolicy",
                "iam:PutRolePermissionsBoundary",
                "iam:DeleteRolePermissionsBoundary",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy"
          ],
          resources=[
            "*"
          ],
          conditions={
            "StringEquals": {
              "iam:PermissionsBoundary": sandbox_managed_policy.managed_policy_arn
            }
          }
        )
      ]
    )    

    sandbox_role=iam.Role(
      self,
      "SandboxRole",
      role_name="Sandbox",
      description="Sandbox Role",
      max_session_duration=core.Duration.hours(max_session_duration),
      path=iam_path,
      assumed_by=iam.FederatedPrincipal(
        f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:saml-provider/{identity_provider_name}",
        conditions={
          "StringEquals": {
            "SAML:aud": "https://signin.aws.amazon.com/saml"
          }
        },
        assume_role_action="sts:AssumeRoleWithSAML"
      ),
      permissions_boundary=sandbox_managed_policy
    )

    sandbox_role.add_managed_policy(sandbox_managed_policy)
    sandbox_role.add_managed_policy(create_role_sandbox)
    core.Tag.add(sandbox_role,"Privileged","False")
    core.Tag.add(sandbox_role,"Owner","")
    core.Tag.add(sandbox_role,"Description","Sandbox Role")

    sandbox_role.add_to_policy(
        iam.PolicyStatement(
          sid="DenyUpdatingSandboxRole",
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
            sandbox_role.role_arn
          ]
        )
    )

    #avoid circular dependency
    sandbox_role.add_to_policy(
        iam.PolicyStatement(
          sid="DenyUpdatingSandboxManagedPolicy",
          effect=iam.Effect.DENY,
          actions=[
            "iam:CreatePolicyVersion",
            "iam:DeletePolicy",
            "iam:DeletePolicyVersion",
            "iam:SetDefaultPolicyVersion"
          ],
          resources=[
            sandbox_managed_policy.managed_policy_arn
          ]
        )
    )

