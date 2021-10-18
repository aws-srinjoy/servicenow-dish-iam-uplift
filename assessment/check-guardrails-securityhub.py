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

import os

import glob

import textwrap

from collections import defaultdict

import json

def search_iam_action(iam_action):
  results="results.json"
  json_data=None
  with open(results) as json_file:
    json_data=json.load(json_file)

  action_roles=set()
  for role_arn,role_data in json_data.items():
    for access_level,found_iam_actions in role_data.items():
      if iam_action in found_iam_actions:
        action_roles.add(role_arn)

  return action_roles

def check_rule(filename):
  data=None
  with open(filename) as f:
    data=json.load(f)
  identifier=data['Identifier']
  guardrail=data['Guardrail']
  rationale=data['Rationale']
  remediation=data['Remediation']
  references=data['References']
  iam_actions=data['IAM Actions']

  if type(iam_actions) is not list:
    iam_actions=[iam_actions]

  roles_to_actions=defaultdict(set)
  for iam_action in iam_actions:
    iam_action=iam_action.strip()
    found_roles=search_iam_action(iam_action)      
    for role in found_roles:
      roles_to_actions[role].add(iam_action)

  if not roles_to_actions:
    return

  logger.info("---"*10)
  logger.info(f"{identifier}\n{guardrail}\n\nRationale\n{rationale}\n\nReferences\n{references}\n\nRemediation\n{remediation}\n\n")
  logger.info(f"There were {len(roles_to_actions)} IAM Users and Roles found\n")
  findings=[]
  for role,role_iam_actions in roles_to_actions.items():
    logger.info(f"\t{role}".expandtabs(4))
    for iam_action in role_iam_actions:
      logger.info(f"\t{iam_action}".expandtabs(8))

    finding={
      'iam_role_arn':role,
      'iam_role_name': role.split('/')[-1],
      'title':f"{identifier} {guardrail}",
      'description':f"{rationale}",
      'remediation':f"{remediation}"
    }
    findings.append(finding)

if __name__ == "__main__":
  p="../guardrails"
  #files = [f for f in glob.glob(p+"**/*.json",recursive=True)]
  for root,dirs,files in os.walk(p):
      dirs.sort()
      files.sort()
      for filename in files:
        if ".json" in filename:
          check_rule(f"{root.strip()}/{filename}")
