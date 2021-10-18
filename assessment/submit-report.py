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

import argparse

import boto3

s3_client = boto3.client("s3")
sts_client = boto3.client("sts")
accountid = sts_client.get_caller_identity()["Account"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--timestamp", "-ts", help="Timestamp of results files", required=True
    )

    # read arguments from the command line
    args = parser.parse_args()
    ts = args.timestamp

    S3_BUCKET = os.getenv("S3_BUCKET", None)
    if not S3_BUCKET:
        logger.info(
            "Not uploading IAM assessment results as S3_BUCKET was not passed in as an environment variable."
        )
    else:
        files = [
            f"assessment.{ts}.txt",
            f"services-last-used.{ts}.txt",
            f"iam-role-metrics.{ts}.txt",
            f"check-guardrails.{ts}.txt",
            f"policy-validator.{ts}.txt",
        ]
        # files=[f"services-last-used.{ts}.txt"]
        for f in files:
            s3_client.upload_file(f"results/{f}", S3_BUCKET, f"{accountid}/{ts}/{f}")

    NOTIFICATION_EMAIL_ADDRESS = os.getenv("NOTIFICATION_EMAIL_ADDRESS", None)
    if not NOTIFICATION_EMAIL_ADDRESS:
        logger.info(
            "Not sending completion notification email as NOTIFICATION_EMAIL_ADDRESS was not passed in as an environemtn variable"
        )
    else:
        ses_client = boto3.client("ses")
        # https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html
        SUBJECT = "AWS IAM Assessment completed"
        BODY_TEXT = "AWS IAM Assessment has completed and results to view.\r\n"
        CHARSET = "UTF-8"
        SENDER = NOTIFICATION_EMAIL_ADDRESS
        RECIPIENT = NOTIFICATION_EMAIL_ADDRESS
        ses_client.send_email(
            Destination={"ToAddresses": [RECIPIENT]},
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
