import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import datetime
import uuid

import boto3

import json

securityhub_client=boto3.client('securityhub')
iam_client=boto3.client('iam')

account_id=boto3.client('sts').get_caller_identity().get('Account')
region='us-east-1'

#https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html
#arn:partition:securityhub:region:account-id:product/company-id/product-id.
product_arn=f"arn:aws:securityhub:{region}:{account_id}:product/{account_id}/default"
print(product_arn)

product_severity=int(8)
product_normalized=int(80)
compliance_rating="FAILED"

#256 characters
#title="title here"
#description="description here"

def format_finding(iam_finding):
  iso8061Time=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
  asffID = str(uuid.uuid4())
  iam_role_arn=iam_finding['iam_role_arn']
  iam_role_name=iam_finding['iam_role_name']
  title=iam_finding['title']
  description=iam_finding['description']
  remediation=iam_finding['remediation']

  role_info=iam_client.get_role(RoleName=iam_role_name)['Role']
  role_id=role_info['RoleId']
  AssumeRolePolicyDocument=json.dumps(role_info['AssumeRolePolicyDocument'])
  CreateDate=role_info['CreateDate'].isoformat()
  MaxSessionDuration=role_info['MaxSessionDuration']
  Path=role_info['Path'] 

  finding= {
                'SchemaVersion': '2018-10-08',
                'Id': asffID,
                'ProductArn': product_arn,
                'ProductFields': {
                    'ProviderName': 'IAMPermissionsGuardrails',
                    'ProviderVersion': 'v0.0.1',
                    },
                'GeneratorId': asffID,
                'AwsAccountId': account_id,
                'Types': [ 'Software and Configuration Checks' ],
                'FirstObservedAt': iso8061Time,
                'UpdatedAt': iso8061Time,
                'CreatedAt': iso8061Time,
                'Severity': {
                    'Product': product_severity,
                    'Normalized': product_normalized
                },
                'Title': title,
                'Description': description,
                'Remediation': {
                  'Recommendation': {
                    'Text': remediation
                  }
                },
                'Resources': [
                    {
                        'Type': 'AwsIamRole',
                        'Id': iam_role_arn,
                        'Partition': 'aws',
                        'Region': region,
                        'Details': {
                          'AwsIamRole': {
                              'AssumeRolePolicyDocument': AssumeRolePolicyDocument,
                              'CreateDate': CreateDate,
                              'RoleId': role_id,
                              'RoleName': iam_role_name,
                              'MaxSessionDuration': MaxSessionDuration,
                              'Path': Path
                          }
                        }
                    }
                ],
                'WorkflowState': 'NEW',
                'Compliance': {'Status': compliance_rating},
                'RecordState': 'ACTIVE'
            }
  
  return finding

def import_finding(iam_findings):
  try:
    findings=[]
    for iam_finding in iam_findings:
      try:
        finding=format_finding(iam_finding) 
        findings.append(finding)
      except:
        logger.exception("Error formatting finding")

    response = securityhub_client.batch_import_findings(
        Findings=findings
    )
    logger.info(f"{response}")
  except:
    logger.exception("Error with Security Hub batch import findings")
