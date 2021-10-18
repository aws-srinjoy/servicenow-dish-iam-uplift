from aws_cdk import (
  core,
  aws_iam as iam,
  aws_config
)


class IamBestPracticesStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    testuser=iam.User(
      self,
      "testuser",
      user_name="testuser"
    )

    #https://github.com/aws/aws-cdk/issues/1612
    accesskey=iam.CfnAccessKey(
      self,
      "testuseraccesskey",
      user_name="testuser",
    )

    #[IAM.1]    
    accesskeysrotated1day=aws_config.ManagedRule(
      self,
      "accesskeysrotated1day",
      config_rule_name="ACCESS_KEYS_ROTATED_1DAY",
      identifier="ACCESS_KEYS_ROTATED",
      description="Access Keys Rotated every 1 day",
      input_parameters={
        "maxAccessKeyAge":1
      }
    )

    accesskeysrotated90day=aws_config.ManagedRule(
      self,
      "accesskeysrotated90day",
      config_rule_name="ACCESS_KEYS_ROTATED_90DAY",
      identifier="ACCESS_KEYS_ROTATED",
      description="Access Keys Rotated every 90 day",
      input_parameters={
        "maxAccessKeyAge":90
      }
    )

    #[IAM.2]
    iamuseruncheckedcredentials1days=aws_config.ManagedRule(
      self,
      "iamuseruncheckedcredentials1days",
      config_rule_name="IAM_USER_UNUSED_CREDENTIALS_CHECK_1DAY",
      identifier="IAM_USER_UNUSED_CREDENTIALS_CHECK",
      description="1 Day Checks whether your AWS Identity and Access Management (IAM) users have passwords or active access keys that have not been used within the specified number of days you provided. ",
      input_parameters={
        "maxCredentialUsageAge":1
      }
    )

    iamuseruncheckedcredentials90days=aws_config.ManagedRule(
      self,
      "iamuseruncheckedcredentials90days",
      config_rule_name="IAM_USER_UNUSED_CREDENTIALS_CHECK_90DAYS",      
      identifier="IAM_USER_UNUSED_CREDENTIALS_CHECK",
      description="Checks whether your AWS Identity and Access Management (IAM) users have passwords or active access keys that have not been used within the specified number of days you provided.",
      input_parameters={
        "maxCredentialUsageAge":90
      }
    )

    #[IAM.3]
    rootaccesskeycheck=aws_config.ManagedRule(
      self,
      "rootaccesskeycheck",
      config_rule_name="IAM_ROOT_ACCESS_KEY_CHECK",
      identifier="IAM_ROOT_ACCESS_KEY_CHECK",
      description="Checks whether the root user access key is available. The rule is COMPLIANT if the user access key does not exist.",
    )    

    #[IAM.4]
    rootmfaenabled=aws_config.ManagedRule(
      self,
      "rootmfaenabled",
      config_rule_name="ROOT_ACCOUNT_MFA_ENABLED",
      identifier="ROOT_ACCOUNT_MFA_ENABLED",
      description="Root MFA Enabled",
    )

    #[IAM.5]
    rootmfaenabled=aws_config.ManagedRule(
      self,
      "roothardwaremfaenabled",
      config_rule_name="ROOT_ACCOUNT_HARDWARE_MFA_ENABLED",
      identifier="ROOT_ACCOUNT_HARDWARE_MFA_ENABLED",
      description="Checks whether your AWS account is enabled to use multi-factor authentication (MFA) hardware device to sign in with root credentials.",
    )   

    testgroup_withiamuser=iam.Group(
      self,
      "testgroupwithiamuser",
      group_name="testgroupwithiamuser",
    )

    testuser_attachedtogroup=iam.User(
      self,
      "testuserattachedtogroup",
      user_name="testuserattachedtogroup",
    )
    testuser_attachedtogroup.add_to_group(testgroup_withiamuser)

    #[IAM.7]
    iamgrouphasusers=aws_config.ManagedRule(
      self,
      "iamgrouphasusers",
      config_rule_name="IAM_GROUP_HAS_USERS_CHECK",
      identifier="IAM_GROUP_HAS_USERS_CHECK",
      description="Checks whether IAM groups have at least one IAM user.",
    )       

    testgroup_blacklistedsysadmin=iam.Group(
      self,
      "testgroupblacklistedsysadmin",
      group_name="testgroupblacklistedsysadmin",
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("job-function/SystemAdministrator")],
    )

    testuser_blacklistedpoliciesadmin=iam.User(
      self,
      "testuserblacklistedpoliciesadmin",
      user_name="testuserblacklistedpoliciesadmin",
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")]
    )

    testrole_blacklistedpoliciessysadmin=iam.Role(
      self,
      "testroleblacklistedpoliciessysadmin",
      role_name="testroleblacklistedpoliciessysadmin",
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("job-function/SystemAdministrator")],
      assumed_by=iam.FederatedPrincipal(
        f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:saml-provider/identity_provider_name",
        conditions={
          "StringEquals": {
            "SAML:aud": "https://signin.aws.amazon.com/saml"
          }
        },
        assume_role_action="sts:AssumeRoleWithSAML"
      )      
    )

    testuser_blacklistedpoliciespoweruser=iam.User(
      self,
      "testuserblacklistedpoliciespoweruser",
      user_name="testuserblacklistedpoliciespoweruser",
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("PowerUserAccess")]
    )

    testrole_blacklistedpoliciesall=iam.Role(
      self,
      "testroleblacklistedpoliciesall",
      role_name="testroleblacklistedpoliciesall",
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
        iam.ManagedPolicy.from_aws_managed_policy_name("job-function/SystemAdministrator"),
        iam.ManagedPolicy.from_aws_managed_policy_name("PowerUserAccess")
      ],
      assumed_by=iam.FederatedPrincipal(
        f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:saml-provider/identity_provider_name",
        conditions={
          "StringEquals": {
            "SAML:aud": "https://signin.aws.amazon.com/saml"
          }
        },
        assume_role_action="sts:AssumeRoleWithSAML"
      )      
    )

    #[IAM.8]
    administrativepoliciesblacklisted=aws_config.ManagedRule(
      self,
      "administrativepoliciesblacklisted",
      config_rule_name="IAM_POLICY_BLACKLISTED_CHECK",
      identifier="IAM_POLICY_BLACKLISTED_CHECK",
      description="Check for blacklisted AWS Managed Policies attached",
      input_parameters={
        "policyArns":"arn:aws:iam::aws:policy/AdministratorAccess,arn:aws:iam::aws:policy/job-function/SystemAdministrator,arn:aws:iam::aws:policy/PowerUserAccess",
      }
    ) 

    #[IAM.10]
    passwordpolicyiamusers=aws_config.ManagedRule(
      self,
      "passwordpolicyiamusers",
      config_rule_name="IAM_PASSWORD_POLICY",
      identifier="IAM_PASSWORD_POLICY",
      description="Checks whether the account password policy for IAM users meets the specified requirements.",
      input_parameters={
        "RequireUppercaseCharacters": "true",
        "RequireLowercaseCharacters": "true",
        "RequireSymbols": "true",
        "RequireNumbers": "true",
        "MinimumPasswordLength": "14",
        "PasswordReusePrevention": "24",
        "MaxPasswordAge": "90"
      }
    ) 
