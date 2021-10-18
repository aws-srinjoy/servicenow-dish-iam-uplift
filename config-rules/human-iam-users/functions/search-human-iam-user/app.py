import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from email.utils import parseaddr

import os, datetime

import json

import boto3


def handler(event, context):
    # ssm_role = os.environ["SSM_ROLE"]
    deactivate_function_name = os.environ["DEACTIVATE_FUNCTION_NAME"]
    max_credential_age = int(os.environ["MAX_CREDENTIAL_AGE"])
    logger.info(f"{deactivate_function_name} {max_credential_age}")
    logger.info(event)
    logger.info(context)

    session = boto3.Session()
    iam_client = session.client("iam")
    lambda_client = session.client("lambda")

    todays_date_time = datetime.datetime.now(datetime.timezone.utc)

    list_users_paginator = iam_client.get_paginator("list_users")
    for user_page in list_users_paginator.paginate():
        for user in user_page["Users"]:
            user_name = user["UserName"]
            user_id = user["UserId"]
            if not is_human_user(user_name):
                logger.info(f"{user_name} is not identified as human user")
                continue
            access_keys_paginator = iam_client.get_paginator("list_access_keys")
            for access_key_page in access_keys_paginator.paginate(UserName=user_name):
                for key_metadata in access_key_page["AccessKeyMetadata"]:
                    status = key_metadata["Status"]
                    if status == "Active":
                        check_and_deactivate_key(
                            user_name,
                            user_id,
                            key_metadata,
                            max_credential_age,
                            todays_date_time,
                            lambda_client,
                            deactivate_function_name,
                        )

    return "done"


def check_and_deactivate_key(
    user_name,
    user_id,
    key_metadata,
    max_credential_age,
    todays_date_time,
    lambda_client,
    deactivate_function_name,
):
    access_key_id = key_metadata["AccessKeyId"]
    create_date = key_metadata["CreateDate"]
    key_age_finder = todays_date_time - create_date
    if key_age_finder <= datetime.timedelta(days=max_credential_age):
        logger.info(f"Access key: {access_key_id} for {user_name}is compliant")
    else:
        logger.info(
            f"Access key: {access_key_id} for {user_name} over {max_credential_age} days old found!"
        )

        payload = {"UserName": user_name, "MaxCredentialUsageAge": max_credential_age}

        invocation_result = lambda_client.invoke(
            FunctionName=deactivate_function_name,
            InvocationType="Event",
            LogType="Tail",
            Payload=json.dumps(payload),
        )

        logger.info(
            f"Started lambda {deactivate_function_name} with result {invocation_result}"
        )


def is_human_user(username):
    return "@" in parseaddr(username)[1]
