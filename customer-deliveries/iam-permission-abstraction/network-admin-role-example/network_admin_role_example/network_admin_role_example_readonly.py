from aws_cdk import (
  core,
  aws_iam as iam
)

class NetworkAdminRoleExampleReadOnlyStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
      super().__init__(scope, id, **kwargs)

      """
      max_session_duration_parameter=core.CfnParameter(self,
        "MaxSessionDuration",
        default=1,
        description="Maximum Session Duration for Assume Role - Hours",
        type=""
      )
      """

      iam_path_parameter=core.CfnParameter(self,
        "IAMPath",
        default="/",
        description="IAM Path" 
      ) 

      identity_provider_name_parameter=core.CfnParameter(self,
        "IdentityProviderName",
        description="Identity Provider SAML Name"
        #substituded in arn:aws:iam::123456789234:saml-provider/IdentityProviderName
      )

      max_session_duration=1
      iam_path=iam_path_parameter.value_as_string
      identity_provider_name=identity_provider_name_parameter.value_as_string

      network_read_only_managed_policy=iam.ManagedPolicy(
        self,
        "NetworkReadOnlyPolicy",
        description="Network Read Only",
        path=iam_path,
        statements=[
          iam.PolicyStatement(
            sid="NetworkReadOnly",
            effect=iam.Effect.ALLOW,
            actions=[
              "route53resolver:Get*",
              "route53resolver:List*",
              "elasticloadbalancing:Describe*",
              "directconnect:Describe*",
              "autoscaling:Describe*",
              "cloudformation:Get*",
              "cloudformation:List*",
              "cloudformation:Describe*",
              "cloudformation:Detect*"
            ],
            resources=[
                "arn:aws:route53resolver:*:*:resolver-endpoint/*",
                "arn:aws:route53resolver:*:*:resolver-rule/*",
                "arn:aws:directconnect:*:*:dxvif/*",
                "arn:aws:directconnect:*:*:dxlag/*",
                "arn:aws:directconnect:*:*:dxcon/*",
                "arn:aws:directconnect::*:dx-gateway/*",
                "arn:aws:cloudformation:*:*:stack/*/*",
                "arn:aws:cloudformation:*:*:stackset/*:*"
            ]
          ),
          iam.PolicyStatement(
            sid="NetworkReadOnlyNoResource",
            effect=iam.Effect.ALLOW,
            actions=[
              "cloudformation:List*",
              "cloudformation:Describe*",
              "ec2:Describe*",
              "ec2:Get*"                       
            ],
            resources=[
              "*"
            ]
          )
        ]
      )

      network_administrator_read_only_role=iam.Role(
        self,
        "NetworkReadOnly",
        role_name="NetworkReadOnly",
        description="Network Read Only",
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
        )
      )

      network_administrator_read_only_role.add_managed_policy(network_read_only_managed_policy)    
      network_administrator_read_only_role.add_managed_policy(
        iam.ManagedPolicy.from_managed_policy_name(
          self,
          id="DenyNonNetworkPerimeter",
          managed_policy_name="DenyNonNetworkPerimeter"
        )

      )
      core.Tag.add(network_administrator_read_only_role,"Name","NetworkReadOnly")
