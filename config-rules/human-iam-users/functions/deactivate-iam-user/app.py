import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import boto3
from datetime import datetime, timedelta

iam_client = boto3.client("iam")


def list_access_keys(user_name):
    return iam_client.list_access_keys(UserName=user_name).get("AccessKeyMetadata")


def deactivate_key(user_name, access_key, responses):
    responses["DeactivateUnusedKeysResponse"].append(
        {
            "AccessKeyId": access_key,
            "Response": iam_client.update_access_key(
                UserName=user_name, AccessKeyId=access_key, Status="Inactive"
            ),
        }
    )


def deactivate_unused_keys(access_keys, max_credential_usage_age, user_name, responses):
    for key in access_keys:
        create_date = key.get("CreateDate").replace(tzinfo=None)
        days_since_creation = (datetime.now() - create_date).days
        if days_since_creation >= max_credential_usage_age:
            deactivate_key(user_name, key.get("AccessKeyId"), responses)


def user_has_login_profile(user_name):
    try:
        iam_client.get_login_profile(UserName=user_name)
    except Exception:
        logger.exception("error getting logging profile")
        return False

    return True


def delete_unused_password(user_name, max_credential_usage_age, responses):
    user = iam_client.get_user(UserName=user_name).get("User")
    if user_has_login_profile(user_name) and user.get("PasswordLastUsed"):
        password_last_used = user.get("PasswordLastUsed").replace(tzinfo=None)
        password_last_used_days = (datetime.now() - password_last_used).days
        if password_last_used_days >= max_credential_usage_age:
            responses["DeleteUnusedPasswordResponse"] = iam_client.delete_login_profile(
                UserName=user_name
            )


def verify_expired_credentials_revoked(responses, user_name):
    if responses.get("DeactivateUnusedKeysResponse"):
        for key in responses.get("DeactivateUnusedKeysResponse"):
            key_data = next(
                filter(
                    lambda x: x.get("AccessKeyId") == key.get("AccessKeyId"),
                    list_access_keys(user_name),
                )
            )
            if key_data.get("Status") != "Inactive":
                error_message = (
                    "VERIFICATION FAILED. ACCESS KEY {} NOT DEACTIVATED".format(
                        key_data.get("AccessKeyId")
                    )
                )
                raise Exception(error_message)
    if responses.get("DeleteUnusedPasswordResponse"):
        try:
            iam_client.get_login_profile(UserName=user_name)
            error_message = (
                "VERIFICATION FAILED. IAM USER {} LOGIN PROFILE NOT DELETED".format(
                    user_name
                )
            )
            raise Exception(error_message)
        except iam_client.exceptions.NoSuchEntityException:
            logger.exception(f"not found {user_name}")
            pass
    return {
        "output": "Verification of unused IAM User credentials is successful.",
        "http_responses": responses,
    }


def handler(event, context):
    username = event.get("UserName")
    max_age = int(event.get("MaxCredentialUsageAge"))

    logger.info(f"{username} {max_age}")

    responses = {"DeactivateUnusedKeysResponse": []}

    access_keys = list_access_keys(username)
    deactivate_unused_keys(access_keys, max_age, username, responses)

    delete_unused_password(username, max_age, responses)

    result = verify_expired_credentials_revoked(responses, username)
    logger.info(f"result {result}")
    return result
