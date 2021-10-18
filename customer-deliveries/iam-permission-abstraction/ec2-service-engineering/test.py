#https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-api.html
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import boto3
sts_client = boto3.client('sts')

account="023793197476"
role_name="serviceengineering/ec2/ec2-service-engineering-EC2ServiceEngineeringRole2-ARXCKNO17OT0"

assumed_role_object=sts_client.assume_role(
    RoleArn=f"arn:aws:iam::{account}:role/{role_name}",
    RoleSessionName="EC2ServiceEngineeringRole"
)

credentials=assumed_role_object['Credentials']

iam_client=boto3.client(
    "iam",
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)

assume_role_policy_document="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::023793197476:saml-provider/test"
      },
      "Action": "sts:AssumeRoleWithSAML",
      "Condition": {
        "StringEquals": {
          "SAML:aud": "https://signin.aws.amazon.com/saml"
        }
      }
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::023793197476:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"""

try:
  iam_client.create_role(
    RoleName="test",
    AssumeRolePolicyDocument=assume_role_policy_document
  )
except:
  logging.exception("Error create role without path and permissions boundary")

try:
  iam_client.create_role(
    RoleName="test",
    AssumeRolePolicyDocument=assume_role_policy_document,
    Path="/serviceengineering/ec2/developer/"
  )
except:
  logging.exception("Error create role without permissions boundary")

try:
  iam_client.create_role(
    RoleName="test2",
    AssumeRolePolicyDocument=assume_role_policy_document,
    Path="/serviceengineering/ec2/developer/",
    PermissionsBoundary="arn:aws:iam::023793197476:policy/serviceengineering/ec2/CreateRoleEC2ServiceEngineeringDelegatedAdmin"
  )
  logger.info("Success!")
except:
  logging.exception("Error create role without permissions boundary")
