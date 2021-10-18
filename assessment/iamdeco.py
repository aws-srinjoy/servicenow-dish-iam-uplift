# -*- coding: future_fstrings -*-
"""
Amazon Web Services makes no warranties, express or implied, in this document.
Amazon Web Services (AWS) may have patents, patent applications, trademarks, copyrights, or other intellectual property rights covering subject matter in this document.  Except as expressly provided in any written license agreement from AWS, our provision of this document does not give you any license to these patents, trademarks, copyrights, or other intellectual property.
The descriptions of other companies’ products in this document, if any, are provided only as a convenience to you.  Any such references should not be considered an endorsement or support by AWS.  AWS cannot guarantee their accuracy, and the products may change over time. Also, the descriptions are intended as brief highlights to aid understanding, rather than as thorough coverage. For authoritative descriptions of these products, please consult their respective manufacturers.
Copyright © 2020 Amazon Web Services, Inc. and/or its affiliates. All rights reserved.
The following are trademarks of Amazon Web Services, Inc.: Amazon, Amazon Web Services Design, AWS, Amazon CloudFront, Cloudfront, Amazon DevPay, DynamoDB, ElastiCache, Amazon EC2, Amazon Elastic Compute Cloud, Amazon Glacier, Kindle, Kindle Fire, AWS Marketplace Design, Mechanical Turk, Amazon Redshift, Amazon Route 53, Amazon S3, Amazon VPC. In addition, Amazon.com graphics, logos, page headers, button icons, scripts, and service names are trademarks, or trade dress of Amazon in the U.S. and/or other countries. Amazon's trademarks and trade dress may not be used in connection with any product or service that is not Amazon's, in any manner that is likely to cause confusion among customers, or in any manner that disparages or discredits Amazon.
All other trademarks not owned by Amazon are the property of their respective owners, who may or may not be affiliated with, connected to, or sponsored by Amazon.
"""
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import functools

import json

from datetime import datetime,timezone

import functools

import boto3, botocore
from botocore.exceptions import ClientError

import textwrap

from collections import Counter

from iam_client import get_client, print_iam_apis_used

IS_COLORAMA_INSTALLED=False
try:
  import colorama
  from colorama import Fore
  colorama.init()
  IS_COLORAMA_INSTALLED=True
except:
  IS_COLORAMA_INSTALLED=False

#MAX_CONNECTIONS=100
#MAX_ATTEMPTS=25

#config=botocore.client.Config(max_pool_connections=MAX_CONNECTIONS,retries=dict(max_attempts=MAX_ATTEMPTS))

PAGE_SIZE=1000

def print_info(message):
  print(Fore.BLUE+message) if IS_COLORAMA_INSTALLED else print(message)

def print_fail(message):
  print(Fore.RED + message) if IS_COLORAMA_INSTALLED else print(message)

def print_pass(message):
  print(Fore.BLACK + message) if IS_COLORAMA_INSTALLED else print(message)

def iamcheck(identifier,evaluate_all_regions=False,client_name=None,message=None):
  def wrap(function):
    @functools.wraps(function)
    def wrapped_f(*args, **kwargs):
      if evaluate_all_regions:
        return evaluate_regions(client_name,function,message)
      else:
        boto3_client=get_client(client_name,max_attempts=3)
        return function(boto3_client,*args, **kwargs)
    wrapped_f.identifier=identifier
    return wrapped_f
  return wrap

@iamcheck(identifier="s3bucketreplication",evaluate_all_regions=False,client_name="s3",message="\nChecking for S3 bucket replication")
def get_s3_bucket_replication(s3_client):
    replication_configuration = []
    response = s3_client.list_buckets()
    for bucket in response['Buckets']:
        name = bucket["Name"]
        try:
            response = s3_client.get_bucket_replication(Bucket=name)
            replication_configuration.append(response["ReplicationConfiguration"])
        except ClientError as error:
            if error.response["Error"]["Code"] == "ReplicationConfigurationNotFoundError":
                #no bucket replication configured
                pass
            else:
                raise error
    if replication_configuration:
        print_pass(f"\tThe following S3 bucket replication configurations are enabled".expandtabs(8))
        print_pass(f"\t {replication_configuration}".expandtabs(12))
    else:
        print_pass(f"\tNo S3 buckets with replication configuration enabled".expandtabs(8))

@iamcheck("sessionmanager",True,"ssm","\nChecking for Session Manager instances")
def get_session_manager_instances(ssm_client):
  instance_count=0
  paginator=ssm_client.get_paginator('describe_instance_information')
  for page in paginator.paginate(PaginationConfig={'PageSize': 50}):
      for endpoints in page["InstanceInformationList"]:
        instance_count+=1

  print_pass(f"\t{instance_count} instances are enabled with Session Manager.")         

@iamcheck("sshkeypairscreators",True,"cloudtrail","\nChecking for the principals creating SSH Keys")
def get_ec2_ssh_keypairs_creators(cloudtrail_client):
    ssh_keypair_creators=cloudtrail_client.lookup_events(
        LookupAttributes=[
            {   
                'AttributeKey':'EventName',
                'AttributeValue':'CreateKeyPair'
            }
        ],
        MaxResults=100
    )
    events=ssh_keypair_creators['Events']
    usernames=set()
    for event in events:
      username=event['Username']
      usernames.add(username)
    if not events:
        print_pass(f"\t0 Principals recently creating SSH key pairs in the last 90 days. Please check in your centralized logging for historical usage.".expandtabs(8))
    else:
        print_fail(f"\t{usernames} are the principals that have recently created SSH key pairs in the last 90 days".expandtabs(8))

@iamcheck("sshkeypairs",True,"ec2","\nChecking for SSH Keys")
def get_ec2_ssh_keypairs(ec2_client):
    keypairs=ec2_client.describe_key_pairs()["KeyPairs"]
    #print(keypairs)
    number_ssh_keypairs=len(keypairs)
    message=f"\t{number_ssh_keypairs} SSH Keypairs".expandtabs(8)
    if number_ssh_keypairs==0:
        print_pass(message)
    else:
        print_fail(message)
    #return number_ssh_keypairs

@iamcheck("vpcendpoints",True,"ec2","\nChecking for VPC Endpoints")
def get_vpc_endpoints(ec2_client):
    vpc_endpoints=0
    paginator=ec2_client.get_paginator('describe_vpc_endpoints')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for endpoints in page["VpcEndpoints"]:
            #print(endpoints)
            service_name=endpoints["ServiceName"]
            policy_document=endpoints["PolicyDocument"]
            print_pass(f"\t {service_name} VPC Endpoint enabled".expandtabs(12))
            print_pass(textwrap.indent(f"{policy_document}", prefix=' '*12))
            vpc_endpoints+=1

    print_pass(f"\t{vpc_endpoints} total VPC endpoints enabled".expandtabs(8))

@iamcheck("rootinfo",client_name="cloudtrail")
def get_recent_root_usage(cloudtrail_client):
    #aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventSource,AttributeValue=iam.amazonaws.com
    #aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=root --max-items 25
    message="\nChecking for root usage"
    print_info(message)

    event_counter=Counter()
    paginator=cloudtrail_client.get_paginator('lookup_events')
    lookup_event={'AttributeKey':'Username','AttributeValue':'root'}
    parameters={'LookupAttributes':[lookup_event]}
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE},**parameters):
        for event in page["Events"]:
          event_name=event['EventName']
          event_counter[event_name]+=1
    
    if not event_counter:
        print_pass(f"\tNo recent root usage detected in the last 90 days. Please check in your centralized logging for historical usage.".expandtabs(8))
    else:
        print_fail(f"\tRecent root usage detected in the last 90 days".expandtabs(8))
        for event_name,count in event_counter.items():
          print_fail(f"\t{event_name} was called {count} times.".expandtabs(12))

@iamcheck("ec2instancev2metadata",True,"ec2","\nChecking for EC2 Instance Metadata V2")
def get_ec2_instances_v2_metdata(ec2_client):
    ec2_instances=0
    v2_only_instances=0
    paginator=ec2_client.get_paginator('describe_instances')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for reservations in page['Reservations']:
            for instances in reservations['Instances']:
                metadata_options=instances['MetadataOptions']
                http_tokens=metadata_options['HttpTokens']
                ec2_instances+=1
                if http_tokens=="required":
                    v2_only_instances+=1
    if ec2_instances==0:
        print_pass(f"\t0 EC2 instances".expandtabs(8))
    elif v2_only_instances==ec2_instances:
        print_pass(f"\t {v2_only_instances} out of {ec2_instances} EC2 instances have V2 Metadata required".expandtabs(8))
    else:
        print_fail(f"\t {ec2_instances-v2_only_instances} out of {ec2_instances} EC2 instances have V2 Metadata optional".expandtabs(8))

def count_wildcard_resources(role_name,iam_client):
  wildcard_resource_count=0
  managed_policies=iam_client.list_attached_role_policies(RoleName=role_name)
  attachedpolicies=managed_policies['AttachedPolicies']
  for attachedpolicy in attachedpolicies:
    policyarn=attachedpolicy['PolicyArn']
    policy_metadata=iam_client.get_policy(PolicyArn=policyarn)
    default_version_id=policy_metadata["Policy"]["DefaultVersionId"]
    try:
      policy_document=iam_client.get_policy_version(PolicyArn=policyarn,VersionId=default_version_id)
      role_policy_document=policy_document['PolicyVersion']['Document']
      statements=role_policy_document["Statement"]
      wildcard_resource_count+=evaluate_statement_for_wildcard_resource(statements)
    except:
      logger.exception("Error get policy version and evaluating statements")
  policy_names=iam_client.list_role_policies(RoleName=role_name)["PolicyNames"]
  for policy_name in policy_names:
    inline_policy=iam_client.get_role_policy(RoleName=role_name,PolicyName=policy_name)
    inline_policy_document=inline_policy["PolicyDocument"]
    statements=inline_policy_document["Statement"] 
    wildcard_resource_count+=evaluate_statement_for_wildcard_resource(statements)

  return wildcard_resource_count

def evaluate_statement_for_wildcard_resource(statements):
  wildcard_resource_count=0
  if isinstance(statements,list):
    for statement in statements:
      wildcard_resource_count+=statement_count_wildcard_resources(statement)
  else:
    wildcard_resource_count+=statement_count_wildcard_resources(statements)
  return wildcard_resource_count

def statement_count_wildcard_resources(statement):
  wildcard_resource_count=0
  if statement["Effect"]=="Allow":
    resource=""
    if "Resource" in statement:
      resource=statement["Resource"]
    if "NotResource" in statement:
      resource=statement["NotResource"]
    if isinstance(resource,list):
      for r in resource:
        if r=="*":
          wildcard_resource_count+=1
    elif resource=="*":
      wildcard_resource_count+=1
  return wildcard_resource_count

@iamcheck("roleinfo",client_name="iam")
def get_iam_roles(iam_client):
    message="\nChecking IAM Roles"
    print_info(message)
    role_count=0
    age_90_days=0
    age_180_days=0
    age_365_days=0
    age_never=0
    path_counter=Counter()
    federated_roles=[]
    wildcard_resource_count=0

    paginator=iam_client.get_paginator('list_roles')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for role in page['Roles']:
            role_count+=1
            role_name=role['RoleName']
            role_arn=role['Arn']
            role_data=iam_client.get_role(RoleName=role_name)
  
            role_info=role_data['Role']
            path=role_info['Path']
            path_counter[path]+=1

            wildcard_resource_count+=count_wildcard_resources(role_name,iam_client)

            role_last_used=role_info['RoleLastUsed']
            if 'LastUsedDate' in role_last_used:
                last_used_date=role_last_used['LastUsedDate']
                time_period=datetime.now(timezone.utc)-last_used_date
                if time_period.days>=90:
                    age_90_days+=1
                if time_period.days>=180:
                    age_180_days+=1
                if time_period.days>=365:
                    age_365_days+=1 
            else:
                age_never+=1

            assume_role_policy_document=role_info['AssumeRolePolicyDocument']['Statement']
            for statement in assume_role_policy_document:
              principal=statement['Principal']
              if 'Federated' in principal:
                federated_roles.append(role_arn)
            
    print_pass(f"\n\t{role_count} IAM Roles found".expandtabs(4))
    print_fail(f"\t{age_90_days} IAM Roles not used within the past 90 days".expandtabs(8))
    print_fail(f"\t{age_180_days} IAM Roles not used within the past 180 days".expandtabs(8))
    print_fail(f"\t{age_365_days} IAM Roles not used within the past 365 days".expandtabs(8))
    print_fail(f"\t{age_never} IAM Roles never used".expandtabs(8))
   
    print_pass(f"\n\tThe following IAM Paths are being used".expandtabs(4))
    for path,count in path_counter.items():
      print_pass(f"\t{path} {count} times".expandtabs(8))
  
    if len(federated_roles)>0:
      print_pass(f"\n\tThe following IAM Roles are federated".expandtabs(4))
      for role in federated_roles:
        print_pass(f"\t{role}".expandtabs(8))

    if wildcard_resource_count==0:
      print_pass(f"\n\tThere are no IAM Roles that have wildcard Resource elements".expandtabs(4))
    else:
      print_fail(f"\n\tThere are {wildcard_resource_count} wildcard Resource elements used by the policies in the IAM Roles".expandtabs(4))

@iamcheck("userinfo",client_name="iam")
def get_users(iam_client):
    message="\nChecking for IAM Users"
    print_info(message)
    paginator=iam_client.get_paginator('list_users')
    user_count=0
    password_count=0
    access_keys_count=0
    active_access_keys_count=0
    age_90_days=0
    age_180_days=0
    age_365_days=0 
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for user in page["Users"]:
            user_count+=1
            user_arn=user['Arn']
            user_name=user['UserName']
            print_fail(f"\t{user_arn} found".expandtabs(8))

            if 'PasswordLastUsed' in user:
                password_count+=1
                password_last_user=user['PasswordLastUsed']
                print_fail(f"\t{password_last_user} password last used".expandtabs(12))

            access_keys_paginator = iam_client.get_paginator('list_access_keys')
            for access_keys_page in access_keys_paginator.paginate(UserName=user_name,PaginationConfig={'PageSize': PAGE_SIZE}):
                for access_key in access_keys_page['AccessKeyMetadata']:
                    access_keys_count+=1
                    if 'Active'==access_key['Status']:
                        active_access_keys_count+=1
                    create_date=access_key['CreateDate']
                    time_period=datetime.now(timezone.utc)-create_date
                    if time_period.days>=90:
                        age_90_days+=1
                    if time_period.days>=180:
                        age_180_days+=1
                    if time_period.days>=365:
                        age_365_days+=1

    if user_count==0:
        print_pass("\n\tNo IAM Users".expandtabs(8))
    else:
        print_fail(f"\n\t{user_count} IAM Users found".expandtabs(8)) 
        print_fail(f"\t{password_count} passwords active found".expandtabs(8)) 
        print_fail(f"\t{active_access_keys_count} active access keys out of {access_keys_count}".expandtabs(8))
        print_fail(f"\t{age_90_days} access keys not rotated within the past 90 days".expandtabs(8))
        print_fail(f"\t{age_180_days} access keys not rotated within the past 180 days".expandtabs(8))
        print_fail(f"\t{age_365_days} access keys not rotated within the past 365 days".expandtabs(8))
@iamcheck("accessanalyzer",True,"accessanalyzer","\nChecking for IAM Access Analyzer findings")
def get_access_analyzer(accessanalyzer_client):
  analyzers=accessanalyzer_client.list_analyzers()['analyzers']
  if len(analyzers)==0:
    print_fail(f"\tNo IAM Access Analyzers configured".expandtabs(8))
    return
  
  public_resource_count=0
  for analyzer in analyzers:
      findings=accessanalyzer_client.list_findings(analyzerArn=analyzer['arn'])
      for finding in findings['findings']:
          if finding and 'isPublic' in finding and finding['isPublic'] and 'status' in finding and finding['status']=='ACTIVE':
              public_resource_count+=1
              principal=finding['principal']
              resource=finding['resource']
              resource_type=finding['resourceType']
              print_fail(f"\t{resource} of type {resource_type} is Publicly Accessible.".expandtabs(8))
              continue
  if public_resource_count==0:
    print_pass(f"\tNo Public Resources found".expandtabs(8))
  else:
    print_fail(f"\n\t{public_resource_count} Public Resources found".expandtabs(8))

@iamcheck("samlinfo",client_name="iam")
def get_saml_providers(iam_client):
  message="\nChecking for SAML Providers"
  print_info(message)
  saml_providers=iam_client.list_saml_providers()['SAMLProviderList']
  if len(saml_providers)==0:
    print_pass(f"\tNo SAML Providers configured".expandtabs(4))

  print_pass("\tThe following SAML Providers are configured".expandtabs(4))
  for saml in saml_providers:
    arn=saml['Arn']
    create_date=saml['CreateDate']
    valid_until=saml['ValidUntil']
    print_pass(f"\t{arn} was created {create_date} and is vald until {valid_until}".expandtabs(8))

@iamcheck("iamroleattachevents",client_name="cloudtrail")
def get_recent_iam_role_attach_events_creators(cloudtrail_client):
  message="\nChecking for recent principals attaching IAM Roles to compute"
  print_info(message)

  iam_action="ec2:RunInstances"
  event_name="RunInstances"
  parameters={'indent':8,'iam_action':iam_action,'event_name':event_name}
  msg=f"\n\tChecking for principals recently invoking {iam_action}."
  print_info(msg)
  lookup_recent_iam_role_attach_events_creators(cloudtrail_client,iam_action,event_name)       
  #evaluate_regions('cloudtrail',lookup_recent_iam_role_attach_events_creators,msg,**parameters)


  iam_action="iam:AttachRolePolicy"
  event_name="AttachRolePolicy"
  parameters={'indent':8,'iam_action':iam_action,'event_name':event_name}
  msg=f"\n\tChecking for principals recently attaching a managed policy to an IAM Role invoking {iam_action}."
  print_info(msg)
  lookup_recent_iam_role_attach_events_creators(cloudtrail_client,iam_action,event_name)
  #evaluate_regions('cloudtrail',lookup_recent_iam_role_attach_events_creators,msg,**parameters)

  iam_action="iam:PutRolePolicy"
  event_name="PutRolePolicy"
  parameters={'indent':8,'iam_action':iam_action,'event_name':event_name}
  msg=f"\n\tChecking for principals recently attaching a inline policy to an IAM Role invoking {iam_action}."
  print_info(msg)
  lookup_recent_iam_role_attach_events_creators(cloudtrail_client,iam_action,event_name)
  #evaluate_regions('cloudtrail',lookup_recent_iam_role_attach_events_creators,msg,**parameters)

  iam_action="iam:CreateRole"
  event_name="CreateRole"
  parameters={'indent':8,'iam_action':iam_action,'event_name':event_name}
  msg=f"\n\tChecking for principals recently invoking {iam_action}."
  print_info(msg)
  lookup_recent_iam_role_attach_events_creators(cloudtrail_client,iam_action,event_name)
  #evaluate_regions('cloudtrail',lookup_recent_iam_role_attach_events_creators,msg,**parameters)

def lookup_recent_iam_role_attach_events_creators(cloudtrail_client,iam_action,event_name):
    principals=Counter()
    paginator=cloudtrail_client.get_paginator('lookup_events')
    lookup_event={'AttributeKey':'EventName','AttributeValue':event_name}
    parameters={'LookupAttributes':[lookup_event]}
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE},**parameters):
        for event in page["Events"]:
          principals[event['Username']]+=1

    if not principals:
        print_pass(f"\t0 Principals recently invoking {iam_action}. Please check in your centralized logging for historical usage.".expandtabs(16))
    else:
        print_fail(f"\t{len(principals)} unique principals have recently invoked {iam_action}".expandtabs(16))
        for principal,count in principals.items():
          print_fail(f"\t{principal} has recently invoked {iam_action} {count} times".expandtabs(20)) 

@functools.lru_cache(maxsize=256)
def get_regions():
    ec2=get_client("ec2",max_attempts=3) #boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    return regions

def evaluate_regions(client_name,method_name,message,indent=0,**parameters):
    regions=get_regions()
    print_info(message)
    for region in regions:
        client=get_client(client_name,region,max_attempts=3) #boto3.client(client_name,region)
        print_pass(f"\t{region}".expandtabs(4+indent))
        try:
            method_name(client,**parameters)
        except:
            logger.exception(f"Unable to invoke {method_name}")
            print_fail(f"\tCan't invoke {method_name} in {region}".expandtabs(8))

def run_check(identifier):
  import inspect
  import sys
  current_module = sys.modules[__name__]
  functions = inspect.getmembers(current_module, inspect.isfunction)
  for f in functions:
      if getattr(f[1],"identifier",None):
          if identifier==f[1].identifier:
            print(f[1].identifier)
            f[1]()

def main():
    iam_client=get_client("iam",max_attempts=3) #boto3.client('iam')
    cloudtrail_client=get_client("cloudtrail",max_attempts=3) #boto3.client('cloudtrail')

    #iam_event_system=iam_client.meta.events
    #iam_event_system.register('provide-client-params.iam.*',track_api_methods)


    get_iam_roles()
    get_users()
    get_saml_providers()
    get_recent_root_usage()
    get_recent_iam_role_attach_events_creators()

    get_vpc_endpoints()
    get_ec2_ssh_keypairs()
    get_ec2_ssh_keypairs_creators()
    get_ec2_instances_v2_metdata()
    get_access_analyzer()
    get_session_manager_instances()
    
    get_s3_bucket_replication()


if __name__ == "__main__":
  main()
  #run_check("vpcendpoints")
  #run_check("roleinfo")
