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

from datetime import datetime,timezone

import functools

import time

import boto3, botocore

from iam_client import get_client, print_iam_apis_used

IS_COLORAMA_INSTALLED=False
try:
  import colorama
  from colorama import Fore
  colorama.init()
  IS_COLORAMA_INSTALLED=True
except:
  IS_COLORAMA_INSTALLED=False

MAX_CONNECTIONS=100
MAX_ATTEMPTS=25

config=botocore.client.Config(max_pool_connections=MAX_CONNECTIONS,retries=dict(max_attempts=MAX_ATTEMPTS))

PAGE_SIZE=50

def print_fail(message):
  print(Fore.RED + message) if IS_COLORAMA_INSTALLED else print(message)

def print_pass(message):
  print(Fore.BLACK + message) if IS_COLORAMA_INSTALLED else print(message)

def get_iam_roles(iam_client):
    message="\nChecking IAM Roles, IAM Users Services Last Used"
    print(Fore.BLUE+message)
    role_count=0
    users_count=0
    service_count=0
    age_90_days=0
    age_180_days=0
    age_365_days=0
    age_never=0
    job_ids=[]
    paginator=iam_client.get_paginator('list_roles')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for role in page['Roles']:
            role_count+=1
            role_name=role['RoleName']
            role_arn=role['Arn']
            job_id=iam_client.generate_service_last_accessed_details(Arn=role_arn)['JobId']
            job_ids.append(job_id)

    paginator=iam_client.get_paginator('list_users')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for user in page['Users']:
            users_count+=1
            user_name=user['UserName']
            user_arn=user['Arn']
            job_id=iam_client.generate_service_last_accessed_details(Arn=role_arn)['JobId']
            job_ids.append(job_id)

    while job_ids:
        for job_id in job_ids[:]:
            service_last_access_details=iam_client.get_service_last_accessed_details(JobId=job_id)
            job_status=service_last_access_details['JobStatus']
            if 'FAILED' == job_status:
                logger.error("A job failed to generate service last accessed details")
                job_ids.remove(job_id)
            if 'COMPLETED' == job_status:
                #process
                job_ids.remove(job_id)
                services_last_access=service_last_access_details['ServicesLastAccessed']
                for service in services_last_access:
                    service_count+=1
                    service_name=service['ServiceName']
                    if 'LastAuthenticated' in service:
                        last_authenticated_date=service['LastAuthenticated']
                        time_period=datetime.now(timezone.utc)-last_authenticated_date
                        if time_period.days>=90:
                            age_90_days+=1
                        if time_period.days>=180:
                            age_180_days+=1
                        if time_period.days>=365:
                            age_365_days+=1
                    else:
                        age_never+=1
        if job_ids:
            print("Waiting 60 seconds")
            time.sleep(60)

    print_pass(f"\n\t{users_count} IAM Users found".expandtabs(8))
    print_pass(f"\t{role_count} IAM Roles found".expandtabs(8))
    print_fail(f"\t{service_count} times AWS Services granted access".expandtabs(8))
    print_fail(f"\t{age_90_days} times IAM Roles have granted access to AWS Services and not used the granted AWS Service within the past 90 days".expandtabs(8))
    print_fail(f"\t{age_180_days} times IAM Roles have granted access to AWS Services and not used the granted AWS Service within the past 180 days".expandtabs(8))
    print_fail(f"\t{age_365_days} times IAM Roles have granted access to AWS Services and not used the granted AWS Service within the past 365 days".expandtabs(8))
    print_fail(f"\t{age_never} times IAM Roles have granted access to AWS Services and never used the granted AWS Services".expandtabs(8))

if __name__ == "__main__":
    iam_client=get_client("iam") #boto3.client('iam')
    get_iam_roles(iam_client)
    print_pass("")
    print_iam_apis_used()
