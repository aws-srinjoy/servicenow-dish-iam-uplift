# Short Description

For client import a CMK, unlike most managed KMS keys or CMK, the key material can be deleted. When you delete imported key material, the CMK becomes unusable right away, which could cause service interruption to our customer. It is critical to put permission monitoring on imported keys to prevent unwanted delete action.


This artifact create a custom config rule to check policy of each imported key, it report key as NON_COMPLIANT when there are outside of white list principles has kms:DeleteImportedKeyMaterial permission.


The yaml file is the cloudformation template in written in AWS Serverless Application Model framework.

# Template parameter

WhitelistedPrincipalArns is a comma seperated list, it can not be a group, need to be either list of user and role arns, since you cannnot specify group as key policy principles.


# Deploy Steps
rdk deploy IMPORTED_KEY_MATERIAL_NOT_DELETE_PERMISSION

#Test
rdk test-local IMPORTED_KEY_MATERIAL_NOT_DELETE_PERMISSION


