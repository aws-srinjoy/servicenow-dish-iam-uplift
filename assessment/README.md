# General IAM Assessment

## Disclaimers
* This is a data gathering tool, nothing more, nothing less. Requires data to be interpreted by an AWS IAM SME
* The customer is not getting any grade
* This is not an audit, only an opportunity to identity potential areas to improve the customer's security posture and help prioritize next steps
* There is no seal of approval being issued or granted here

## Installation
* You will need this folder, as there are helper files here
* Install the depenencies ``` pip install -r requirements.txt```

## Components
* [IAM Environment Assessment](#iam-environment-assessment)
* [AWS Services Last Used](#aws-services-last-used)
* [AWS IAM Role Permission Metrics](#aws-iam-role-permission-metrics)
* [AWS IAM Permissions Guardrails Checks](#aws-iam-permissions-guardrails-checks)

### IAM Environment Assessment (IAM Deco)
Point this at an AWS Account and the script will generate various IAM metrics against IAM best practices.

You will need to include ```iam_client.py```

```python3 iamdeco.py```

```
Checking IAM Roles

    35 IAM Roles found
        6 IAM Roles not used within the past 90 days
        2 IAM Roles not used within the past 180 days
        0 IAM Roles not used within the past 365 days
        15 IAM Roles never used

    The following IAM Paths are being used
        / 15 times
        /service-role/ 4 times
        /aws-reserved/sso.amazonaws.com/ 6 times
        /aws-service-role/access-analyzer.amazonaws.com/ 1 times
        /aws-service-role/guardduty.amazonaws.com/ 1 times
        /aws-service-role/stacksets.cloudformation.amazonaws.com/ 1 times
        /aws-service-role/config.amazonaws.com/ 1 times
        /aws-service-role/config-multiaccountsetup.amazonaws.com/ 1 times
        /aws-service-role/isengard.aws.internal/ 1 times
        /aws-service-role/organizations.amazonaws.com/ 1 times
        /aws-service-role/sso.amazonaws.com/ 1 times
        /aws-service-role/support.amazonaws.com/ 1 times
        /aws-service-role/trustedadvisor.amazonaws.com/ 1 times

    The following IAM Roles are federated
        arn:aws:iam::913733971067:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AWSAdministratorAccess_23df949f2a0cd7e2
        arn:aws:iam::913733971067:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AWSPowerUserAccess_082bfbc4ddac7156
        arn:aws:iam::913733971067:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AWSReadOnlyAccess_035a84091581f36c
        arn:aws:iam::913733971067:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AWSServiceCatalogAdminFullAccess_739b39056d144753
        arn:aws:iam::913733971067:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_AWSServiceCatalogEndUserAccess_4bf9018843ffbb27
        arn:aws:iam::913733971067:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_CustomPermissionSet_c0783458f937adcb

    There are 74 wildcard Resource elements used by the policies in the IAM Roles

Checking for IAM Users
        arn:aws:iam::913733971067:user/cfn found

        1 IAM Users found
        0 passwords active found
        1 active access keys out of 1
        1 access keys not rotated within the past 90 days
        0 access keys not rotated within the past 180 days
        0 access keys not rotated within the past 365 days

Checking for SAML Providers
    The following SAML Providers are configured
        arn:aws:iam::913733971067:saml-provider/AWSSSO_16bea4beac9024d7_DO_NOT_DELETE was created 2019-07-17 12:42:07+00:00 and is vald until 2119-07-17 12:42:06+00:00

Checking for root usage
        No recent root usage detected in the last 90 days. Please check in your centralized logging for historical usage.

Checking for VPC Endpoints
    eu-north-1
        0 total VPC endpoints enabled
    ap-south-1
        0 total VPC endpoints enabled
    eu-west-3
        0 total VPC endpoints enabled
    eu-west-2
        0 total VPC endpoints enabled
    eu-west-1
        0 total VPC endpoints enabled
    ap-northeast-3
        0 total VPC endpoints enabled
    ap-northeast-2
        0 total VPC endpoints enabled
    ap-northeast-1
        0 total VPC endpoints enabled
    sa-east-1
        0 total VPC endpoints enabled
    ca-central-1
        0 total VPC endpoints enabled
    ap-southeast-1
        0 total VPC endpoints enabled
    ap-southeast-2
        0 total VPC endpoints enabled
    eu-central-1
        0 total VPC endpoints enabled
    us-east-1
        0 total VPC endpoints enabled
    us-east-2
        0 total VPC endpoints enabled
    us-west-1
        0 total VPC endpoints enabled
    us-west-2
        0 total VPC endpoints enabled

Checking for SSH Keys
    eu-north-1
        0 SSH Keypairs
    ap-south-1
        0 SSH Keypairs
    eu-west-3
        0 SSH Keypairs
    eu-west-2
        0 SSH Keypairs
    eu-west-1
        0 SSH Keypairs
    ap-northeast-3
        0 SSH Keypairs
    ap-northeast-2
        0 SSH Keypairs
    ap-northeast-1
        0 SSH Keypairs
    sa-east-1
        0 SSH Keypairs
    ca-central-1
        0 SSH Keypairs
    ap-southeast-1
        0 SSH Keypairs
    ap-southeast-2
        0 SSH Keypairs
    eu-central-1
        0 SSH Keypairs
    us-east-1
        0 SSH Keypairs
    us-east-2
        0 SSH Keypairs
    us-west-1
        0 SSH Keypairs
    us-west-2
        0 SSH Keypairs

Checking for the principals creating SSH Keys
    eu-north-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ap-south-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    eu-west-3
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    eu-west-2
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    eu-west-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ap-northeast-3
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ap-northeast-2
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ap-northeast-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    sa-east-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ca-central-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ap-southeast-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    ap-southeast-2
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    eu-central-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    us-east-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    us-east-2
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    us-west-1
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.
    us-west-2
        0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.

Checking for EC2 Instance Metadata V2
    eu-north-1
        0 EC2 instances
    ap-south-1
        0 EC2 instances
    eu-west-3
        0 EC2 instances
    eu-west-2
        0 EC2 instances
    eu-west-1
        0 EC2 instances
    ap-northeast-3
        0 EC2 instances
    ap-northeast-2
        0 EC2 instances
    ap-northeast-1
        0 EC2 instances
    sa-east-1
        0 EC2 instances
    ca-central-1
        0 EC2 instances
    ap-southeast-1
        0 EC2 instances
    ap-southeast-2
        0 EC2 instances
    eu-central-1
        0 EC2 instances
    us-east-1
        0 EC2 instances
    us-east-2
        0 EC2 instances
    us-west-1
        0 EC2 instances
    us-west-2
        0 EC2 instances

Checking for IAM Access Analyzer findings
    eu-north-1
        No IAM Access Analyzers configured
    ap-south-1
        No IAM Access Analyzers configured
    eu-west-3
        No IAM Access Analyzers configured
    eu-west-2
        No IAM Access Analyzers configured
    eu-west-1
        No IAM Access Analyzers configured
    ap-northeast-3
        No IAM Access Analyzers configured
    ap-northeast-2
        No IAM Access Analyzers configured
    ap-northeast-1
        No IAM Access Analyzers configured
    sa-east-1
        No IAM Access Analyzers configured
    ca-central-1
        No IAM Access Analyzers configured
    ap-southeast-1
        No IAM Access Analyzers configured
    ap-southeast-2
        No IAM Access Analyzers configured
    eu-central-1
        No IAM Access Analyzers configured
    us-east-1
        No Public Resources found
    us-east-2
        No IAM Access Analyzers configured
    us-west-1
        No IAM Access Analyzers configured
    us-west-2
        No IAM Access Analyzers configured

Checking for Session Manager instances
    eu-north-1
	0 instances are enabled with Session Manager.
    ap-south-1
	0 instances are enabled with Session Manager.
    eu-west-3
	0 instances are enabled with Session Manager.
    eu-west-2
	0 instances are enabled with Session Manager.
    eu-west-1
	0 instances are enabled with Session Manager.
    ap-northeast-3
	0 instances are enabled with Session Manager.
    ap-northeast-2
	0 instances are enabled with Session Manager.
    ap-northeast-1
	0 instances are enabled with Session Manager.
    sa-east-1
	0 instances are enabled with Session Manager.
    ca-central-1
	0 instances are enabled with Session Manager.
    ap-southeast-1
	0 instances are enabled with Session Manager.
    ap-southeast-2
	0 instances are enabled with Session Manager.
    eu-central-1
	0 instances are enabled with Session Manager.
    us-east-1
	0 instances are enabled with Session Manager.
    us-east-2
	0 instances are enabled with Session Manager.
    us-west-1
	0 instances are enabled with Session Manager.
    us-west-2
	0 instances are enabled with Session Manager.

Checking for recent principals attaching IAM Roles to compute

	Checking for principals recently invoking ec2:RunInstances.
                0 Principals recently invoking ec2:RunInstances. Please check in your centralized logging for historical usage.

	Checking for principals recently attaching a managed policy to an IAM Role invoking iam:AttachRolePolicy.
                2 unique principals have recently invoked iam:AttachRolePolicy
                    jjjoy-Isengard has recently invoked iam:AttachRolePolicy 4 times
                    Isengard has recently invoked iam:AttachRolePolicy 2 times

	Checking for principals recently attaching a inline policy to an IAM Role invoking iam:PutRolePolicy.
                1 unique principals have recently invoked iam:PutRolePolicy
                    Isengard has recently invoked iam:PutRolePolicy 1 times

	Checking for principals recently invoking iam:CreateRole.
                2 unique principals have recently invoked iam:CreateRole
                    jjjoy-Isengard has recently invoked iam:CreateRole 4 times
                    Isengard has recently invoked iam:CreateRole 2 times
```

### AWS Services Last Used

Point this at an AWS Account to generate data to generate IAM metrics on over-provisioned AWS IAM Roles that are assigned permissions for  AWS Services though are not utilizing the assigned AWS Services.


```python3 services-last-used.py```

Example Output

```
Checking IAM Roles, IAM Users Services Last Used

        2 IAM Users found
        44 IAM Roles found
        2187 times AWS Services granted access
        62 times AWS Services granted access and not used within the past 90 days
        54 times AWS Services granted access and not used within the past 180 days
        0 times AWS Services granted access and and not used within the past 365 days
        2073 times AWS Services granted access and never used
```

### AWS IAM Role Permission Metrics

Point this at an AWS Account to generate all IAM Actions allowed per role. Note that this will take a while, one customer with 2,000 IAM roles took about 24 hours to complete.

A file results.json will contain all the IAM Actions per IAM Role in JSON format.

You can also ```check-guardrails.py``` (see below) to evaluate against the IAM Permissions Guardrails. Or analyze the JSON file with your custom tooling.

```python3 iam-roles-metrics.py```

```
INFO:__main__:Analyzing IAM Roles for account 123456789123
INFO:__main__:Total number of possible IAM Actions by access level
INFO:__main__:Write 3711
INFO:__main__:Read 1798
INFO:__main__:List 1245
INFO:__main__:Tagging 271
INFO:__main__:Permissions management 134
INFO:__main__:Found Roles 11
INFO:__main__:Completed 10 roles out of 11
INFO:__main__:Time Taken was 319.31162601799997
INFO:__main__:Found Users 1
INFO:__main__:Total Users 1
INFO:__main__:Total Roles 11
INFO:__main__:Total IAM Actions Allowed By Access Level
INFO:__main__:Permissions management IAM Actions Used by IAM Roles 133 out of 134
INFO:__main__:Tagging IAM Actions Used by IAM Roles 269 out of 271
INFO:__main__:List IAM Actions Used by IAM Roles 1227 out of 1245
INFO:__main__:Read IAM Actions Used by IAM Roles 1791 out of 1798
INFO:__main__:Write IAM Actions Used by IAM Roles 3678 out of 3711
INFO:__main__:Permissions management IAM Actions Used by IAM Users 133 out of 134
INFO:__main__:Tagging IAM Actions Used by IAM Users 269 out of 271
INFO:__main__:List IAM Actions Used by IAM Users 1227 out of 1245
INFO:__main__:Read IAM Actions Used by IAM Users 1791 out of 1798
INFO:__main__:Write IAM Actions Used by IAM Users 3678 out of 3711
INFO:__main__:Total Time Taken was 380.58292308299997
```

### AWS IAM Permissions Guardrails Checks

Performs the AWS IAM Permissions Guardrails checks.

This currently takes the results of ```iam-roles-metrics.py```.

```
python3 check-guardrails.py
```

```
------------------------------
IAM-IAM-2
Check that the management of IAM Roles and Policies for authorized principals only, ideally build automation roles only.

Rationale
The creation, update, and deletion of roles and policies and SAML provides needs to occur on approved changes to the IAM environment. However, these changes should be gated and restricted to authorized roles only, such as build automation, to prevent against any unintended principal granting themselves unauthorized permissions. The following permissions should be scoped appropriately. AttachRolePolicy AttachUserPolicy CreateAccountAlias UpdateAssumeRolePolicy CreateSAMLProvider CreateServiceLinkedRole DeleteAccountAlias DeleteAccountPasswordPolicy DeletePolicy DeletePolicyVersion DeleteRole DeleteRolePermissionsBoundary DeleteRolePolicy DeleteSAMLProvider DeleteServiceLinkedRole DeleteUserPermissionsBoundary DetachRolePolicy PutRolePermissionsBoundary PutRolePolicy PutUserPermissionsBoundary UpdateAccountPasswordPolicy UpdateAssumeRolePolicy UpdateRole UpdateRoleDescription UpdateSAMLProvider

References
https://docs.aws.amazon.com/IAM/latest/APIReference/API_Operations.html


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        iam:DeleteRolePermissionsBoundary
        iam:PutUserPermissionsBoundary
        iam:AttachUserPolicy
        iam:CreateServiceLinkedRole
        iam:DeletePolicy
        iam:DeleteRole
        iam:CreateSAMLProvider
        iam:DeleteRolePolicy
        iam:UpdateRoleDescription
        iam:DeletePolicyVersion
        iam:DeleteUserPermissionsBoundary
        iam:DeleteSAMLProvider
        iam:CreateAccountAlias
        iam:PutRolePermissionsBoundary
        iam:AttachRolePolicy
        iam:UpdateAssumeRolePolicy
        iam:UpdateRole
        iam:DeleteServiceLinkedRole
        iam:DetachRolePolicy
        iam:DeleteAccountPasswordPolicy
        iam:DeleteAccountAlias
        iam:PutRolePolicy
        iam:UpdateSAMLProvider
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        iam:DeleteRolePermissionsBoundary
        iam:PutUserPermissionsBoundary
        iam:AttachUserPolicy
        iam:CreateServiceLinkedRole
        iam:DeletePolicy
        iam:DeleteRole
        iam:CreateSAMLProvider
        iam:DeleteRolePolicy
        iam:UpdateRoleDescription
        iam:DeletePolicyVersion
        iam:DeleteUserPermissionsBoundary
        iam:DeleteSAMLProvider
        iam:CreateAccountAlias
        iam:PutRolePermissionsBoundary
        iam:AttachRolePolicy
        iam:UpdateAssumeRolePolicy
        iam:UpdateRole
        iam:DeleteServiceLinkedRole
        iam:DetachRolePolicy
        iam:DeleteAccountPasswordPolicy
        iam:DeleteAccountAlias
        iam:PutRolePolicy
        iam:UpdateSAMLProvider
    arn:aws:iam::123456789123:user/cfn
        iam:DeleteRolePermissionsBoundary
        iam:PutUserPermissionsBoundary
        iam:AttachUserPolicy
        iam:CreateServiceLinkedRole
        iam:DeletePolicy
        iam:DeleteRole
        iam:CreateSAMLProvider
        iam:DeleteRolePolicy
        iam:UpdateRoleDescription
        iam:DeletePolicyVersion
        iam:DeleteUserPermissionsBoundary
        iam:DeleteSAMLProvider
        iam:CreateAccountAlias
        iam:PutRolePermissionsBoundary
        iam:AttachRolePolicy
        iam:UpdateAssumeRolePolicy
        iam:UpdateRole
        iam:DeleteServiceLinkedRole
        iam:DetachRolePolicy
        iam:DeleteAccountPasswordPolicy
        iam:DeleteAccountAlias
        iam:PutRolePolicy
        iam:UpdateSAMLProvider
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        iam:DeleteRolePermissionsBoundary
        iam:PutUserPermissionsBoundary
        iam:AttachUserPolicy
        iam:CreateServiceLinkedRole
        iam:DeletePolicy
        iam:DeleteRole
        iam:CreateSAMLProvider
        iam:DeleteRolePolicy
        iam:UpdateRoleDescription
        iam:DeletePolicyVersion
        iam:DeleteUserPermissionsBoundary
        iam:DeleteSAMLProvider
        iam:CreateAccountAlias
        iam:PutRolePermissionsBoundary
        iam:AttachRolePolicy
        iam:UpdateAssumeRolePolicy
        iam:UpdateRole
        iam:DeleteServiceLinkedRole
        iam:DetachRolePolicy
        iam:DeleteAccountPasswordPolicy
        iam:DeleteAccountAlias
        iam:PutRolePolicy
        iam:UpdateSAMLProvider
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        iam:DeleteRolePermissionsBoundary
        iam:PutUserPermissionsBoundary
        iam:AttachUserPolicy
        iam:CreateServiceLinkedRole
        iam:DeletePolicy
        iam:DeleteRole
        iam:CreateSAMLProvider
        iam:DeleteRolePolicy
        iam:UpdateRoleDescription
        iam:DeletePolicyVersion
        iam:DeleteUserPermissionsBoundary
        iam:DeleteSAMLProvider
        iam:CreateAccountAlias
        iam:PutRolePermissionsBoundary
        iam:AttachRolePolicy
        iam:UpdateAssumeRolePolicy
        iam:UpdateRole
        iam:DeleteServiceLinkedRole
        iam:DetachRolePolicy
        iam:DeleteAccountPasswordPolicy
        iam:DeleteAccountAlias
        iam:PutRolePolicy
        iam:UpdateSAMLProvider
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        iam:DeleteRolePermissionsBoundary
        iam:PutUserPermissionsBoundary
        iam:AttachUserPolicy
        iam:CreateServiceLinkedRole
        iam:DeletePolicy
        iam:DeleteRole
        iam:CreateSAMLProvider
        iam:DeleteRolePolicy
        iam:UpdateRoleDescription
        iam:DeletePolicyVersion
        iam:DeleteUserPermissionsBoundary
        iam:DeleteSAMLProvider
        iam:CreateAccountAlias
        iam:PutRolePermissionsBoundary
        iam:AttachRolePolicy
        iam:UpdateAssumeRolePolicy
        iam:UpdateRole
        iam:DeleteServiceLinkedRole
        iam:DetachRolePolicy
        iam:DeleteAccountPasswordPolicy
        iam:DeleteAccountAlias
        iam:PutRolePolicy
        iam:UpdateSAMLProvider
    arn:aws:iam::123456789123:role/aws-service-role/organizations.amazonaws.com/AWSServiceRoleForOrganizations
        iam:CreateServiceLinkedRole
------------------------------
IAM-CLOUDTRAIL-1
Check that Principals aren’t allowed to DeleteTrail or StopLogging

Rationale
As Cloudtrail is the source for auditing of activity within your AWS Account, it is important to verify that this functionality cannot be disabled by most entities within your Organization. This permission should be limited to breakglass roles (those who own the logging capability). It is also important to call out that Cloudtrail supports Resource Level Permissions for individual trails, so this can be scoped to Infosec/Logging Team owned Trails if the usecase exists for other independent teams to need access to manage their own trails

References
https://docs.aws.amazon.com/awscloudtrail/latest/userguide/security_iam_id-based-policy-examples.html https://docs.aws.amazon.com/IAM/latest/UserGuide/list_awscloudtrail.html


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        cloudtrail:DeleteTrail
        cloudtrail:StopLogging
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        cloudtrail:DeleteTrail
        cloudtrail:StopLogging
    arn:aws:iam::123456789123:user/cfn
        cloudtrail:DeleteTrail
        cloudtrail:StopLogging
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        cloudtrail:DeleteTrail
        cloudtrail:StopLogging
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        cloudtrail:DeleteTrail
        cloudtrail:StopLogging
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        cloudtrail:DeleteTrail
        cloudtrail:StopLogging
------------------------------
IAM-EC2-1
Check that the ability to terminate EC2 instances are appropriately scoped or are only assumable to authorized principals.

Rationale
In Production or Production-like environments,no one other than IaC tools should have access to delete resources. Even in development, unintentional termination of EC2 instances can delay project timelines or delivery. If ec2:TerminateInstances has a wildcard resource policy ( Resource *) that isn’t scoped with a condition statement such as ec2:ResourceTag, unauthorized EC2 instances might be inadvertently terminated.

References
nan


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        ec2:TerminateInstances
    arn:aws:iam::123456789123:role/IncidenceResponseClientRole-DO-NOT-DELETE
        ec2:TerminateInstances
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        ec2:TerminateInstances
    arn:aws:iam::123456789123:user/cfn
        ec2:TerminateInstances
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        ec2:TerminateInstances
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        ec2:TerminateInstances
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        ec2:TerminateInstances
------------------------------
IAM-CLOUDTRAIL-2
Check that only authorized principals are able to UpdateTrail.

Rationale
Unauthorized principals could potentially turn off log file validation, turn off multi region trails, or turn off organizational trails. As Cloudtrail is the source for auditing of activity within your AWS Account, it is important to verify that this functionality is only for authorized principals within your Organization. Examples of authorized principals include break glass roles or those who own the logging capability, such as Security or the Logging Team.

References
https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_UpdateTrail.html


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        cloudtrail:UpdateTrail
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        cloudtrail:UpdateTrail
    arn:aws:iam::123456789123:user/cfn
        cloudtrail:UpdateTrail
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        cloudtrail:UpdateTrail
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        cloudtrail:UpdateTrail
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        cloudtrail:UpdateTrail
------------------------------
IAM-EC2-2
Check EC2 instances can only run instances with approved Amazon Machine Images (AMIs).

Rationale
For security hardening, vulnerability management, and configuration management purposes, only approved AMIs should be used to launch instances in Production or Production-like environments.

References
https://aws.amazon.com/premiumsupport/knowledge-center/restrict-launch-tagged-ami/ https://aws.amazon.com/blogs/aws/amazon-ec2-resource-level-permissions-for-runinstances/ https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazonec2.html#amazonec2-ec2_ResourceTag___TagKey_


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        ec2:RunInstances
    arn:aws:iam::123456789123:role/IncidenceResponseClientRole-DO-NOT-DELETE
        ec2:RunInstances
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        ec2:RunInstances
    arn:aws:iam::123456789123:user/cfn
        ec2:RunInstances
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        ec2:RunInstances
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        ec2:RunInstances
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        ec2:RunInstances
------------------------------
IAM-GUARDDUTY-1
Ensure GuardDuty master account does not have permission to StopMonitoringMembers action

Rationale
The master account should not have permissions to deregister a centralized member account unless it is done by a security admin Makes the accounts go “invisible” which can lead to malicious activities which cannot be viewed at org master level

References
nan


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        guardduty:StopMonitoringMembers
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        guardduty:StopMonitoringMembers
    arn:aws:iam::123456789123:user/cfn
        guardduty:StopMonitoringMembers
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        guardduty:StopMonitoringMembers
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        guardduty:StopMonitoringMembers
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        guardduty:StopMonitoringMembers
------------------------------
IAM-EC2-3
Check that all network modification permissions are granted to authorized roles only, ideally the AWS Account provisioning role.

Rationale
For all environments it is important to maintain and manage authorized network permitters and boundaries. Unauthorized network modifications could expose the network or service to attacks or data exfiltration. These actions are commonly associated with account provisioning rather than daily or frequent usage.

References
https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_Operations.html


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
    arn:aws:iam::123456789123:role/IncidenceResponseClientRole-DO-NOT-DELETE
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
    arn:aws:iam::123456789123:user/cfn
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        ec2:DeleteVpc
        ec2:DisassociateRouteTable
        ec2:AssociateSubnetCidrBlock
        ec2:CreateDhcpOptions
        ec2:CreateRoute
        ec2:CreateVpnConnectionRoute
        ec2:DetachInternetGateway
        ec2:DeleteRouteTable
        ec2:DeleteVpcPeeringConnection
        ec2:DisableVgwRoutePropagation
        ec2:CreateVpnConnection
        ec2:DeleteNetworkAcl
        ec2:ModifySubnetAttribute
        ec2:AttachInternetGateway
        ec2:DeleteNatGateway
        ec2:DeleteCustomerGateway
        ec2:AssociateRouteTable
        ec2:CreateCustomerGateway
        ec2:ModifyVpcEndpointServicePermissions
        ec2:DisassociateVpcCidrBlock
        ec2:CreateVpnGateway
        ec2:ModifyVpcEndpointServiceConfiguration
        ec2:AttachVpnGateway
        ec2:ReplaceRouteTableAssociation
        ec2:DeleteDhcpOptions
        ec2:ModifyVpcEndpoint
        ec2:ModifyVpcAttribute
        ec2:DetachVpnGateway
        ec2:CreateVpcEndpointServiceConfiguration
        ec2:CreateVpcPeeringConnection
        ec2:DisassociateSubnetCidrBlock
        ec2:DeleteVpnConnectionRoute
        ec2:DeleteVpcEndpointServiceConfigurations
        ec2:EnableVgwRoutePropagation
        ec2:CreateInstanceExportTask
        ec2:DeleteSubnet
        ec2:DeleteVpcEndpoints
        ec2:ReplaceRoute
        ec2:AssociateDhcpOptions
        ec2:CreateSubnet
        ec2:CreateVpc
        ec2:DeleteInternetGateway
        ec2:CreateRouteTable
        ec2:DeleteEgressOnlyInternetGateway
        ec2:DeleteVpnGateway
        ec2:DeleteRoute
        ec2:DeleteVpnConnection
        ec2:CreateInternetGateway
        ec2:AssociateVpcCidrBlock
        ec2:CreateVpcEndpoint
        ec2:DeleteNetworkAclEntry
------------------------------
IAM-EC2-4
Check that sensitive more frequently used EC2 actions are appropriately scoped to approprariate roles and resources.

Rationale
These EC2 actions might be more frequently needed, particularly in a development environment. However, these are sensitive EC2 permissions and should be appropriately scoped and for authorized roles only.

References
https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazonec2.html#amazonec2-policy-keys https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_Operations.html


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
    arn:aws:iam::123456789123:role/IncidenceResponseClientRole-DO-NOT-DELETE
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
    arn:aws:iam::123456789123:user/cfn
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        ec2:DisassociateAddress
        ec2:ReplaceIamInstanceProfileAssociation
        ec2:CopyFpgaImage
        ec2:DeregisterImage
        ec2:DisassociateIamInstanceProfile
        ec2:ModifyFpgaImageAttribute
        ec2:CreateImage
        ec2:AttachVolume
        ec2:CreateFpgaImage
        ec2:DeleteFpgaImage
        ec2:ModifyImageAttribute
        ec2:CopyImage
------------------------------
IAM-CODECOMMIT-1
DeleteRepository action for CodeCommit is only allowed to whitelisted roles

Rationale
CodeCommit acts as the source of truth for the versioning of different projects used by the application and/or central IT teams. If privileges to delete repository are not clearly managed, it can lead to accidental deletion of repository leading to data loss

References
nan


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        codecommit:DeleteRepository
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        codecommit:DeleteRepository
    arn:aws:iam::123456789123:user/cfn
        codecommit:DeleteRepository
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        codecommit:DeleteRepository
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        codecommit:DeleteRepository
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        codecommit:DeleteRepository
------------------------------
IAM-IAM-1
Check that the management of AWS IAM Users, secret access keys, and multi-factor authentication is for authorized principals only.

Rationale
While AWS IAM Users are typically not recommended today, in favor of federated principals, IAM Users might be needed for break glass procedures or operational availability when an identity provider is unavailable and federation is not possible. However, in general these actions are sensitive should be scoped appropriately. AddUserToGroup AttachGroupPolicy CreateLoginProfile CreateUser CreateVirtualMFADevice DeactivateMFADevice DeleteAccessKey DeleteGroup DeleteGroupPolicy DeleteLoginProfile DeleteUser DeleteUserPolicy DeleteVirtualMFADevice DetachGroupPolicy DetachUserPolicy EnableMFADevice PutGroupPolicy PutUserPolicy RemoveUserFromGroup ResyncMFADevice UpdateAccessKey UpdateGroup UpdateLoginProfile UpdateUser

References
https://docs.aws.amazon.com/IAM/latest/APIReference/API_Operations.html


    arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole
        iam:CreateUser
        iam:UpdateGroup
        iam:AddUserToGroup
        iam:AttachGroupPolicy
        iam:ResyncMFADevice
        iam:EnableMFADevice
        iam:DeleteLoginProfile
        iam:PutGroupPolicy
        iam:UpdateUser
        iam:PutUserPolicy
        iam:RemoveUserFromGroup
        iam:DeleteGroup
        iam:UpdateAccessKey
        iam:DeleteVirtualMFADevice
        iam:DeleteUser
        iam:DeleteAccessKey
        iam:DeleteUserPolicy
        iam:DeleteGroupPolicy
        iam:DetachUserPolicy
        iam:DetachGroupPolicy
    arn:aws:iam::123456789123:role/ConduitAccessClientRole-DO-NOT-DELETE
        iam:CreateUser
        iam:UpdateGroup
        iam:AddUserToGroup
        iam:AttachGroupPolicy
        iam:ResyncMFADevice
        iam:EnableMFADevice
        iam:DeleteLoginProfile
        iam:PutGroupPolicy
        iam:UpdateUser
        iam:PutUserPolicy
        iam:RemoveUserFromGroup
        iam:DeleteGroup
        iam:UpdateAccessKey
        iam:DeleteVirtualMFADevice
        iam:DeleteUser
        iam:DeleteAccessKey
        iam:DeleteUserPolicy
        iam:DeleteGroupPolicy
        iam:DetachUserPolicy
        iam:DetachGroupPolicy
    arn:aws:iam::123456789123:user/cfn
        iam:CreateUser
        iam:UpdateGroup
        iam:AddUserToGroup
        iam:AttachGroupPolicy
        iam:ResyncMFADevice
        iam:EnableMFADevice
        iam:DeleteLoginProfile
        iam:PutGroupPolicy
        iam:UpdateUser
        iam:PutUserPolicy
        iam:RemoveUserFromGroup
        iam:DeleteGroup
        iam:UpdateAccessKey
        iam:DeleteVirtualMFADevice
        iam:DeleteUser
        iam:DeleteAccessKey
        iam:DeleteUserPolicy
        iam:DeleteGroupPolicy
        iam:DetachUserPolicy
        iam:DetachGroupPolicy
    arn:aws:iam::123456789123:role/BurnerConsoleAccessClientRole-DO-NOT-DELETE
        iam:CreateUser
        iam:UpdateGroup
        iam:AddUserToGroup
        iam:AttachGroupPolicy
        iam:ResyncMFADevice
        iam:EnableMFADevice
        iam:DeleteLoginProfile
        iam:PutGroupPolicy
        iam:UpdateUser
        iam:PutUserPolicy
        iam:RemoveUserFromGroup
        iam:DeleteGroup
        iam:UpdateAccessKey
        iam:DeleteVirtualMFADevice
        iam:DeleteUser
        iam:DeleteAccessKey
        iam:DeleteUserPolicy
        iam:DeleteGroupPolicy
        iam:DetachUserPolicy
        iam:DetachGroupPolicy
    arn:aws:iam::123456789123:role/ConduitAccountSetupRole
        iam:CreateUser
        iam:UpdateGroup
        iam:AddUserToGroup
        iam:AttachGroupPolicy
        iam:ResyncMFADevice
        iam:EnableMFADevice
        iam:DeleteLoginProfile
        iam:PutGroupPolicy
        iam:UpdateUser
        iam:PutUserPolicy
        iam:RemoveUserFromGroup
        iam:DeleteGroup
        iam:UpdateAccessKey
        iam:DeleteVirtualMFADevice
        iam:DeleteUser
        iam:DeleteAccessKey
        iam:DeleteUserPolicy
        iam:DeleteGroupPolicy
        iam:DetachUserPolicy
        iam:DetachGroupPolicy
    arn:aws:iam::123456789123:role/IibsAdminAccess-DO-NOT-DELETE
        iam:CreateUser
        iam:UpdateGroup
        iam:AddUserToGroup
        iam:AttachGroupPolicy
        iam:ResyncMFADevice
        iam:EnableMFADevice
        iam:DeleteLoginProfile
        iam:PutGroupPolicy
        iam:UpdateUser
        iam:PutUserPolicy
        iam:RemoveUserFromGroup
        iam:DeleteGroup
        iam:UpdateAccessKey
        iam:DeleteVirtualMFADevice
        iam:DeleteUser
        iam:DeleteAccessKey
        iam:DeleteUserPolicy
        iam:DeleteGroupPolicy
        iam:DetachUserPolicy
        iam:DetachGroupPolicy
```
