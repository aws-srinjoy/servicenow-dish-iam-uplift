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

import argparse

from timeit import default_timer as timer

import boto3, botocore

import json

from timeit import default_timer as timer

from itertools import zip_longest

from collections import defaultdict

import pprint

import concurrent.futures

import functools

import pkgutil

from iam_client import get_client, print_iam_apis_used

#MAX_CONNECTIONS=100
#MAX_ATTEMPTS=25
#import multiprocessing
#MAX_PROCESSORS=multiprocessing.cpu_count()-2
MAX_PROCESSORS=1
PAGE_SIZE=1000

#config=botocore.client.Config(max_pool_connections=MAX_CONNECTIONS,retries=dict(max_attempts=MAX_ATTEMPTS))

#iam = boto3.client('iam',config=config)
iam=get_client("iam",max_attempts=25)

def set_json(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def get_all_iam_users():
    found_users={}
    paginator=iam.get_paginator('list_users')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for user in page['Users']:
            user_name=user['UserName']
            user_arn=user['Arn']
            found_users[user_name]=user_arn
    logger.info(f"Found Users {len(found_users)}")
    return found_users

def get_all_iam_roles():
    found_roles={}
    paginator=iam.get_paginator('list_roles')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE}):
        for role in page["Roles"]:
            #print(role['RoleName'],role['Arn'])
            role_name=role['RoleName']
            role_arn=role['Arn']
            found_roles[role_name]=role_arn
    logger.info(f"Found Roles {len(found_roles)}")
    return found_roles

def get_permissions():
    access_level_to_actions=defaultdict(set)
    data = pkgutil.get_data("parliament", "iam_definition.json")
    json_data=json.loads(data)
    for service in json_data:
        prefix=service["prefix"]
        for privilege in service["privileges"]:
            action=privilege["privilege"]
            access_level=privilege["access_level"]
            service_action=f"{prefix}:{action}"
            access_level_to_actions[access_level].add(service_action)
    logger.info("Total number of possible IAM Actions by access level")
    for key,value in access_level_to_actions.items():
        logger.info(f"{key} {len(value)}")
    return access_level_to_actions

def evaluate_principals():
    access_level_to_actions=get_permissions()
    principals=defaultdict(set)

    """
    permissions_management_count=0
    tagging_count=0
    list_count=0
    read_count=0
    write_count=0
    """
    counter=0

    permissions_management_actions_roles=set()
    tagging_actions_roles=set()
    list_actions_roles=set()
    read_actions_roles=set()
    write_actions_roles=set()

    start=timer()

    roles=get_all_iam_roles()
    total_roles=len(roles)
    for role_name,role_arn in roles.items():
      try:
          principal,actions=run_queries(role_arn,access_level_to_actions)
          principals[principal]=actions
          permissions_management_actions_roles.update(actions["Permissions management"])
          tagging_actions_roles.update(actions["Tagging"])
          list_actions_roles.update(actions["List"])
          read_actions_roles.update(actions["Read"])
          write_actions_roles.update(actions["Write"])
          counter+=1
          if counter%10==0:
              logger.info(f"Completed {counter} roles out of {total_roles}")
              end=timer()
              duration=end-start
              logger.info(f"Time Taken was {duration}")
              start=timer()
      except:
        logger.exception(f"Error running queries for {role_name} {role_arn}")
    counter=0
  
    permissions_management_actions_users=set()
    tagging_actions_users=set()
    list_actions_users=set()
    read_actions_users=set()
    write_actions_users=set()

    users=get_all_iam_users()
    total_users=len(users)
    for user_name,user_arn in users.items():
      try: 
          principal,actions=run_queries(user_arn,access_level_to_actions)
          principals[principal]=actions
          permissions_management_actions_users.update(actions["Permissions management"])
          tagging_actions_users.update(actions["Tagging"])
          list_actions_users.update(actions["List"])
          read_actions_users.update(actions["Read"])
          write_actions_users.update(actions["Write"])
          counter+=1
          if counter%2==0:
              logger.info(f"Completed {counter} users out of {total_users}")
              end=timer()
              duration=end-start
              logger.debug(f"Time Taken was {duration}")
              start=timer()
      except:
        logger.exception(f"Error running queries for {user_name} {user_arn}")

    with open("results.json", 'wt') as out:
        json.dump(principals,out,default=set_json)

    permissions_management=list(access_level_to_actions["Permissions management"])
    permissions_tagging=list(access_level_to_actions["Tagging"])
    permissions_list=list(access_level_to_actions["List"])
    permissions_read=list(access_level_to_actions["Read"])
    permissions_write=list(access_level_to_actions["Write"])

    logger.info(f"Total Users {total_users}")
    logger.info(f"Total Roles {total_roles}")
    logger.info("Total IAM Actions Allowed By Access Level")
    logger.info(f"Permissions management IAM Actions Used by IAM Roles {len(permissions_management_actions_roles)} out of {len(permissions_management)}")
    logger.info(f"Tagging IAM Actions Used by IAM Roles {len(tagging_actions_roles)} out of {len(permissions_tagging)}")
    logger.info(f"List IAM Actions Used by IAM Roles {len(list_actions_roles)} out of {len(permissions_list)}")
    logger.info(f"Read IAM Actions Used by IAM Roles {len(read_actions_roles)} out of {len(permissions_read)}")
    logger.info(f"Write IAM Actions Used by IAM Roles {len(write_actions_roles)} out of {len(permissions_write)}")

    logger.info(f"Permissions management IAM Actions Used by IAM Users {len(permissions_management_actions_users)} out of {len(permissions_management)}")
    logger.info(f"Tagging IAM Actions Used by IAM Users {len(tagging_actions_users)} out of {len(permissions_tagging)}")
    logger.info(f"List IAM Actions Used by IAM Users {len(list_actions_users)} out of {len(permissions_list)}")
    logger.info(f"Read IAM Actions Used by IAM Users {len(read_actions_users)} out of {len(permissions_read)}")
    logger.info(f"Write IAM Actions Used by IAM Users {len(write_actions_users)} out of {len(permissions_write)}")


def evaluate_principals_concurrent():
    access_level_to_actions=get_permissions()
    principals=defaultdict(set)
    futures=[]

    roles=get_all_iam_roles()
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCESSORS) as executor:
        for role_name,role_arn in roles.items():
            future=executor.submit(run_queries,role_arn,access_level_to_actions)
            futures.append(future)

    users=get_all_iam_users()
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCESSORS) as executor:
        for user_name,user_arn in users.items():
            future=executor.submit(run_queries,user_arn,access_level_to_actions)
            futures.append(future)

    total_users=len(users)
    total_roles=len(roles)

    permissions_management_count=0
    tagging_count=0
    list_count=0
    read_count=0
    write_count=0
    counter=0
    start=timer()
    for future in futures:
        principal,actions=future.result()
        principals[principal]=actions
        permissions_management_count+=len(actions["Permissions management"])
        tagging_count+=len(actions["Tagging"])
        list_count+=len(actions["List"])
        read_count+=len(actions["Read"])
        write_count+=len(actions["Write"])
        counter+=1
        if counter%2==0:
            logger.info(f"Completed counter principals out of {total_users+total_roles}")
            end=timer()
            duration=end-start
            logger.debug(f"Time Taken was {duration}")
            start=timer()


    with open("results.json", 'wt') as out:
        json.dump(principals,out)

    logger.info(f"Total Users {total_users}")
    logger.info(f"Total Roles {total_roles}")
    logger.info("Total Actions Allowed By Access Level")
    logger.info(f"Permissions management {permissions_management_count}")
    logger.info(f"Tagging {tagging_count}")
    logger.info(f"List {list_count}")
    logger.info(f"Read {read_count}")
    logger.info(f"Write {write_count}")
        
def run_queries(principal,access_level_to_actions):
    found_actions=defaultdict(set)

    permissions_management=list(access_level_to_actions["Permissions management"])
    logger.debug("---"*50)
    logger.debug(f"Permissions management {len(permissions_management)}")
    actions=run_query(principal,permissions_management)
    found_actions["Permissions management"]=actions
 
    permissions_tagging=list(access_level_to_actions["Tagging"])
    logger.debug("---"*50) 
    logger.debug(f"Tagging {len(permissions_tagging)}")
    actions=run_query(principal,permissions_tagging)
    found_actions["Tagging"]=actions

    permissions_list=list(access_level_to_actions["List"])
    logger.debug("---"*50)
    logger.debug(f"List {len(permissions_list)}")
    actions=run_query(principal,permissions_list)
    found_actions["List"]=actions

    permissions_read=list(access_level_to_actions["Read"])
    logger.debug("---"*50)
    logger.debug(f"Read {len(permissions_read)}")
    actions=run_query(principal,permissions_read)
    found_actions["Read"]=actions

    permissions_write=list(access_level_to_actions["Write"])
    logger.debug("---"*50)
    logger.debug(f"Write {len(permissions_write)}")
    actions=run_query(principal,permissions_write)
    found_actions["Write"]=actions

    return principal,found_actions

def run_query(principal,permissions_list):
    found_actions=set()
    start=timer()
    chunk_size=125
    for i in range(0,len(permissions_list),chunk_size):
        permissions=permissions_list[i:i+chunk_size]
        end=min(i+chunk_size-1,len(permissions_list))
        logger.debug(f"{i+1}-{end}")
        actions=query_iam_simulator(principal,permissions)
        found_actions.update(actions)
    end=timer()
    duration=end-start
    logger.debug(f"Time Taken was {duration}")
    return found_actions

def query_iam_simulator(principal,permissions):
    found_actions=set()

    #conditions={'ContextKeyName':'aws:SourceVpc','ContextKeyValues':[''],'ContextKeyType':'stringList'}
    conditions={}
    parameters={'PolicySourceArn':principal,'ActionNames':permissions}
    parameters['ContextEntries']=[conditions]
    paginator=iam.get_paginator('simulate_principal_policy')
    for page in paginator.paginate(PaginationConfig={'PageSize': PAGE_SIZE},**parameters):
        for iam_evaluation_result in page['EvaluationResults']:
            evaldecision=iam_evaluation_result['EvalDecision']
            if "allowed"==evaldecision:
                evalactionname=iam_evaluation_result['EvalActionName']
                resourcename=iam_evaluation_result['EvalResourceName']
                found_actions.add(evalactionname)

    return found_actions

def test():
  access_level_to_actions=get_permissions()
  permissions_management=list(access_level_to_actions["Permissions management"])
  principal=""
  found_actions=query_iam_simulator(principal,permissions_management)
  print(found_actions)
  
if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--region", "-r", help="AWS Region that this is running in",required=False)

    # read arguments from the command line
    args = parser.parse_args()
    region=args.region
    """

    logger.info(f"Start iam-role-metrics")# in AWS region {region}")
    #endpoint_url=f"https://sts.{region}.amazonaws.com/"
    #accountid=boto3.client('sts',region_name=region,endpoint_url=endpoint_url).get_caller_identity()['Account']
    sts_client=get_client("sts")
    accountid=sts_client.get_caller_identity()['Account']
    start=timer()
    logger.info("Analyzing IAM Roles for account %s",accountid)
    #run_queries()
    evaluate_principals()
    #test()
    end=timer()
    duration=end-start
    logger.info(f"Total Time Taken was {duration}")
    logger.info("IAM Actions findings were written to results.json. Run check-guardrails.py in order to evaluate against the IAM Permissions Guardrails.")
    print_iam_apis_used()
