import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import argparse

import boto3
from botocore.waiter import SingleWaiterConfig, Waiter

delegated_account=""
parser = argparse.ArgumentParser()
parser.add_argument("--delegated_account", "-delegate", help="Delegated Account, typically your audit or security account number", required=True)
args = parser.parse_args()
logger.info(f"args {args}")

if args.delegated_account:
  logger.info("Delegated account number is:  %s" % args.delegated_account)
  delegated_account = args.delegated_account


waiter_config = SingleWaiterConfig({
  'delay': 10,
  'operation': 'DescribeStackSetOperation',
  'maxAttempts': 360,
  'acceptors': [
    {
      'argument': 'StackSetOperation.Status',
      'expected': 'SUCCEEDED',
      'matcher': 'path',
      'state': 'success'
    },
    {
      'argument': 'StackSetOperation.Status',
      'expected': 'FAILED',
      'matcher': 'path',
      'state': 'failure'
    },
    {
      'argument': 'StackSetOperation.Status',
      'expected': 'STOPPED',
      'matcher': 'path',
      'state': 'failure'
    },
    {
      'expected': 'ValidationError',
      'matcher': 'error',
      'state': 'failure'
    }
  ]
})

cloudformation_client=boto3.client("cloudformation")

cfn=None
with open('org-analyzer.yaml', 'r') as myfile:
  cfn = myfile.read()

StackSetName="access-analyzer-organization"

sts_client=boto3.client("sts")
master_account_id=sts_client.get_caller_identity()['Account']

response=cloudformation_client.create_stack_set(
  StackSetName=StackSetName,
  Description="Access Analyzer Organizations",
  TemplateBody=cfn,
  Capabilities=["CAPABILITY_IAM","CAPABILITY_NAMED_IAM"],
  PermissionModel='SELF_MANAGED',
  AdministrationRoleARN=f'arn:aws:iam::{master_account_id}:role/service-role/AWSControlTowerStackSetRole',
  ExecutionRoleName='AWSControlTowerExecution',
  #AutoDeployment={
  #  'Enabled':True,
  #  'RetainStacksOnAccountRemoval': False
  #}
)
stack_set_id=response['StackSetId']
print("Stack Set Id is {}".format((stack_set_id)))

waiter = Waiter('StackSetOperationComplete', waiter_config, cloudformation_client.describe_stack_set_operation)

audit_account_id=delegated_account

ec2_client = boto3.client('ec2')
all_regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

response=cloudformation_client.create_stack_instances(
  StackSetName=StackSetName,
  DeploymentTargets={
    'Accounts':[audit_account_id]
  },
  Regions=all_regions,
   OperationPreferences={
     'FailureToleranceCount': 1,
     'MaxConcurrentCount': 10
   }
)

operation_id=response['OperationId']
print("Create Stack Instances Operation Id is {}".format((operation_id)))

waiter.wait(
    StackSetName=StackSetName,
    OperationId=operation_id
)

