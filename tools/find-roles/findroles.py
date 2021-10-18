"""
Amazon Web Services makes no warranties, express or implied, in this document.
Amazon Web Services (AWS) may have patents, patent applications, trademarks, copyrights, or other intellectual property rights covering subject matter in this document.  Except as expressly provided in any written license agreement from AWS, our provision of this document does not give you any license to these patents, trademarks, copyrights, or other intellectual property.
The descriptions of other companies’ products in this document, if any, are provided only as a convenience to you.  Any such references should not be considered an endorsement or support by AWS.  AWS cannot guarantee their accuracy, and the products may change over time. Also, the descriptions are intended as brief highlights to aid understanding, rather than as thorough coverage. For authoritative descriptions of these products, please consult their respective manufacturers.
Copyright © 2020 Amazon Web Services, Inc. and/or its affiliates. All rights reserved.
The following are trademarks of Amazon Web Services, Inc.: Amazon, Amazon Web Services Design, AWS, Amazon CloudFront, Cloudfront, Amazon DevPay, DynamoDB, ElastiCache, Amazon EC2, Amazon Elastic Compute Cloud, Amazon Glacier, Kindle, Kindle Fire, AWS Marketplace Design, Mechanical Turk, Amazon Redshift, Amazon Route 53, Amazon S3, Amazon VPC. In addition, Amazon.com graphics, logos, page headers, button icons, scripts, and service names are trademarks, or trade dress of Amazon in the U.S. and/or other countries. Amazon's trademarks and trade dress may not be used in connection with any product or service that is not Amazon's, in any manner that is likely to cause confusion among customers, or in any manner that disparages or discredits Amazon.
All other trademarks not owned by Amazon are the property of their respective owners, who may or may not be affiliated with, connected to, or sponsored by Amazon.
"""
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from timeit import default_timer as timer

import boto3, botocore

import json

from collections import defaultdict

import pprint

import concurrent.futures

from policyuniverse.expander_minimizer import expand_policy

import functools

MAX_CONNECTIONS=100
MAX_ATTEMPTS=25

PAGE_SIZE=1000

config=botocore.client.Config(max_pool_connections=MAX_CONNECTIONS,retries=dict(max_attempts=MAX_ATTEMPTS))

iam = boto3.client('iam',config=config)

def get_sensitive_permission_list():
    filename='sensitive-permissions-list.txt'
    with open(filename) as file:
        return [line.strip() for line in file]

def get_constructive_prefixes():
    filename='constructive.txt'
    with open(filename) as file:
        return [line.strip() for line in file]

def get_destructive_prefixes():
    filename='destructive.txt'
    with open(filename) as file:
        return [line.strip() for line in file]

def find_permission_roles(permission_list,filename):
    users=defaultdict(set)
    roles=defaultdict(set)
    futures=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONNECTIONS) as executor:
        for permission in permission_list:
            future=executor.submit(query_iam_simulator,permission)
            futures.append(future)

    logger.debug('waiting for futures')

    for future in futures:
        #found_roles=query_iam_simulator(permission)
        permission,found_roles,found_users=future.result()
        for role in found_roles:
            roles[role].add(permission)
        for user in found_users:
            users[user].add(permission)
        logger.debug("*"*100)
        logger.debug(permission)
        logger.debug(found_roles)
        logger.debug(found_users)
    with open(filename, 'wt') as out:
        pp = pprint.PrettyPrinter(indent=4,stream=out)
        pp.pprint(dict(roles))
        pp.pprint(dict(users))

def find_sensitive_permission_roles(accountid):
    sensitive_permission_list=get_sensitive_permission_list()
    filename='%s_sensitive-permissions.json' % (accountid)
    start=timer()
    find_permission_roles(sensitive_permission_list,filename)
    end=timer()
    duration=end-start
    logger.info("IAM Roles that can assume the listed sensitive permission are in %s" % (filename))
    logger.info(f"Time Taken was {duration}")

@functools.lru_cache(maxsize=48)
def get_all_iam_users():
    found_users={}
    paginator=iam.get_paginator('list_users')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for user in page['Users']:
            user_name=user['UserName']
            user_arn=user['Arn']
            found_users[user_name]=user_arn
    return found_users 

@functools.lru_cache(maxsize=4096)
def get_all_iam_role_policy():
    found_roles={}
    paginator=iam.get_paginator('list_roles')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for role in page["Roles"]:
            #print(role['RoleName'],role['Arn'])
            role_name=role['RoleName']
            role_arn=role['Arn']
            found_roles[role_name]=role_arn
    return found_roles

def query_iam_simulator(permission):
    try:
        found_roles=list()
        all_role_policy=get_all_iam_role_policy()
        for role_name,role_arn in all_role_policy.items():
            #print(rolename,role_policy_documents,permission)
            iam_evaluation_results=iam.simulate_principal_policy(
                PolicySourceArn=role_arn,
                ActionNames=[permission],
                ResourceArns=['*']
            )
            #print(iam_evaluation_results)
            for iam_evaluation_result in iam_evaluation_results['EvaluationResults']:
                evaldecision=iam_evaluation_result['EvalDecision']
                if "allowed"==evaldecision:
                    evalactionname=iam_evaluation_result['EvalActionName']
                    resourcename=iam_evaluation_result['EvalResourceName']
                    #print("ActionName={0}, ResourceName={1}".format(evalactionname,resourcename))
                    found_roles.append(role_name)
                    break

        found_users=list()
        all_users=get_all_iam_users()
        for user_name,user_arn in all_users.items():
            iam_evaluation_results=iam.simulate_principal_policy(
                PolicySourceArn=user_arn,
                ActionNames=[permission],
                ResourceArns=['*']
            )
            #print(iam_evaluation_results)
            for iam_evaluation_result in iam_evaluation_results['EvaluationResults']:
                evaldecision=iam_evaluation_result['EvalDecision']
                if "allowed"==evaldecision:
                    evalactionname=iam_evaluation_result['EvalActionName']
                    resourcename=iam_evaluation_result['EvalResourceName']
                    #print("ActionName={0}, ResourceName={1}".format(evalactionname,resourcename))
                    found_users.append(user_name)
                    break
        logger.debug(found_roles)
        return permission,found_roles,found_users
    except:
        logger.exception("error making request to iam simulator")
        return None,None,None

def get_aws_services():
    try:
        session=boto3.Session(region_name='us_east-1')
        aws_service_list=session.get_available_services()
        #aws_service_list=['s3','kms','ec2','iam']
        return(aws_service_list)
    except:
        logger.exception("error getting aws services")
        return None

def get_create_permissions():
    aws_service_list=get_aws_services()

    create_permissions=[]
    permissions=get_constructive_prefixes()
    for service in aws_service_list:
        actions=[service+":"+permission+"*" for permission in permissions]
        template_policy = dict(
                        Version='2010-08-14',
                        Statement=[
                            dict(
                                Effect='Allow',
                                #Action=[service+":Create*",service+":Update*",service+":Put*",service+":Add*",service+":Set*",service+":Attach*",service+":Upload*",service+":Enable*",service+":Publish*"],
                                Action=actions,
                                Resource='*',
                            )
                        ]
                    )
        logger.debug(template_policy["Statement"][0]["Action"])
        expanded_policy = expand_policy(policy=template_policy)
        actions=expanded_policy["Statement"][0]["Action"]
        create_permissions=create_permissions+actions

    logger.debug(create_permissions)
    return(create_permissions)

def find_create_roles(accountid):
    create_permissions=get_create_permissions()
    filename='%s_create-permissions.json' % (accountid)
    find_permission_roles(create_permissions,filename)
    logger.info("IAM Roles that can assume the constructive permissions are in %s" % (filename))

def get_destructive_permissions():
    aws_service_list=get_aws_services()

    destructive_permissions=[]
    permissions=get_destructive_prefixes()
    for service in aws_service_list:
        actions=[service+":"+permission+"*" for permission in permissions]
        template_policy = dict(
                        Version='2010-08-14',
                        Statement=[
                            dict(
                                Effect='Allow',
                                #Action=[service+":Delete*",service+":Remove*",service+":Deactivate*",service+":Detach*",service+":Disable*"],
                                Action=actions,
                                Resource='*',
                            )
                        ]
                    )
        logger.debug(template_policy["Statement"][0]["Action"])
        expanded_policy = expand_policy(policy=template_policy)
        actions=expanded_policy["Statement"][0]["Action"]
        destructive_permissions=destructive_permissions+actions
    logger.debug(destructive_permissions)
    return(destructive_permissions)

def find_destructive_roles(accountid):
    destructive_permissions=get_destructive_permissions()
    filename='%s_destructive-permissions.json' % (accountid)
    find_permission_roles(destructive_permissions,filename)
    logger.info("IAM Roles that can assume the destructive permissions are in %s" % (filename))
    

if __name__ == "__main__":
    accountid=boto3.client('sts').get_caller_identity()['Account']
    logger.info("Analyzing IAM Roles for account %s",accountid)
    find_sensitive_permission_roles(accountid)
    find_create_roles(accountid)
    find_destructive_roles(accountid)
    print(get_all_iam_role_policy.cache_info())
