import unittest
import botocore
from unittest.mock import patch, MagicMock
from rdklib import Evaluation, ComplianceType
import rdklibtest

import datetime

RESOURCE_TYPE = "AWS::IAM::Role"

from iam_role_last_used import app

RULE = app.FindUnusedIamRoles()

CLIENT_FACTORY = MagicMock()
IAM_CLIENT_MOCK = MagicMock()
IAM_PAGINATOR_MOCK = MagicMock()

UNUSED_DAYS = 61


def mock_get_client(client_name, *args, **kwargs):
    if client_name == "iam":
        return IAM_CLIENT_MOCK
    raise Exception("Attempting to create an unknown client")


@patch.object(CLIENT_FACTORY, "build_client", MagicMock(side_effect=mock_get_client))
class ComplianceTest(unittest.TestCase):
    def test_0_days(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now(),
                        "RoleLastUsed": "rolelastused",
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic({}, CLIENT_FACTORY, {})
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.COMPLIANT, "roleid", RESOURCE_TYPE, "Role age is 0 days"
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_create_date_60_days(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now() - datetime.timedelta(60),
                        "RoleLastUsed": None,
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic({}, CLIENT_FACTORY, {})
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.COMPLIANT, "roleid", RESOURCE_TYPE, "Role age is 60 days"
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_not_used(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now()
                        - datetime.timedelta(UNUSED_DAYS),
                        "RoleLastUsed": {"LastUsedDate": None, "Region": None},
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic({}, CLIENT_FACTORY, {})
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.NON_COMPLIANT,
                "roleid",
                RESOURCE_TYPE,
                "No record of usage",
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_last_used_61_days(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now()
                        - datetime.timedelta(UNUSED_DAYS),
                        "RoleLastUsed": {
                            "LastUsedDate": datetime.datetime.now()
                            - datetime.timedelta(UNUSED_DAYS),
                            "Region": "us-east-1",
                        },
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic({}, CLIENT_FACTORY, {})
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.NON_COMPLIANT,
                "roleid",
                RESOURCE_TYPE,
                f"Was used {UNUSED_DAYS} days ago in us-east-1 and not within 60",
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_last_used_5_days(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now()
                        - datetime.timedelta(UNUSED_DAYS),
                        "RoleLastUsed": {
                            "LastUsedDate": datetime.datetime.now()
                            - datetime.timedelta(5),
                            "Region": "us-east-1",
                        },
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic({}, CLIENT_FACTORY, {})
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.COMPLIANT,
                "roleid",
                RESOURCE_TYPE,
                "Was used 5 days ago in us-east-1 within 60",
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_authorized_list(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now()
                        - datetime.timedelta(UNUSED_DAYS),
                        "RoleLastUsed": {
                            "LastUsedDate": datetime.datetime.now()
                            - datetime.timedelta(UNUSED_DAYS),
                            "Region": "us-east-1",
                        },
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic(
            {}, CLIENT_FACTORY, {"role_authorized_list": "path/rolename"}
        )
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.COMPLIANT,
                "roleid",
                RESOURCE_TYPE,
                "Role is in authorized list",
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_max_unused_days(self):
        IAM_CLIENT_MOCK.get_paginator.return_value = IAM_PAGINATOR_MOCK
        IAM_PAGINATOR_MOCK.paginate.return_value = [
            {
                "RoleDetailList": [
                    {
                        "RoleId": "roleid",
                        "RoleName": "rolename",
                        "Path": "path",
                        "CreateDate": datetime.datetime.now() - datetime.timedelta(10),
                        "RoleLastUsed": {
                            "LastUsedDate": datetime.datetime.now()
                            - datetime.timedelta(10),
                            "Region": "us-east-1",
                        },
                    }
                ]
            }
        ]
        response = RULE.evaluate_periodic(
            {}, CLIENT_FACTORY, {"max_days_for_last_used": "5"}
        )
        print(response[0].get_json())
        resp_expected = [
            Evaluation(
                ComplianceType.NON_COMPLIANT,
                "roleid",
                RESOURCE_TYPE,
                "Was used 10 days ago in us-east-1 and not within 5",
            )
        ]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)
