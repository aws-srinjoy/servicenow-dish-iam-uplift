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

from iam_client import get_client, print_iam_apis_used

iam_client = get_client("iam", max_attempts=25)
sso_client = get_client("sso-admin", max_attempts=25)
access_analyzer_client = get_client("accessanalyzer", max_attempts=25)


def get_all_permission_sets():
    sso_instances = sso_client.list_instances()
    for sso_instance in sso_instances["Instances"]:
        instance_arn = sso_instance["InstanceArn"]
        paginator = sso_client.get_paginator("list_permission_sets")
        for page in paginator.paginate(InstanceArn=instance_arn):
            for permission_set in page["PermissionSets"]:
                inline_policy = sso_client.get_inline_policy_for_permission_set(
                    InstanceArn=instance_arn, PermissionSetArn=permission_set
                )["InlinePolicy"]
                if not inline_policy:
                    continue
                describe_permission_set = sso_client.describe_permission_set(
                    InstanceArn=instance_arn, PermissionSetArn=permission_set
                )
                policy_name = describe_permission_set["PermissionSet"]["Name"]
                aa_paginator = access_analyzer_client.get_paginator("validate_policy")
                for aa_page in aa_paginator.paginate(
                    locale="EN",
                    policyDocument=inline_policy,
                    policyType="IDENTITY_POLICY",
                ):
                    findings = aa_page["findings"]
                    if findings:
                        logger.warning(
                            f"Policy name {policy_name} permission set arn {permission_set}"
                        )
                    for finding in findings:
                        if finding["findingType"] == "ERROR":
                            logger.error(finding)
                        else:
                            logger.warning(finding)
                    if findings:
                        logger.info("---" * 50)


if __name__ == "__main__":
    logger.info(
        f"Start access analyzer validate policy scan for AWS SSO permission sets"
    )
    start = timer()
    get_all_permission_sets()
    end = timer()
    duration = end - start
    logger.info(f"Total Time Taken was {duration}")
    logger.info("Access Analyzer Actions findings were written to standard out.")
    # print_iam_apis_used()
