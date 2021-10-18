# Copyright 2017-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may
# not use this file except in compliance with the License. A copy of the License is located at
#
#        http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import unittest
import rdklibtest
from mock import MagicMock, patch
from rdklib import Evaluation, ComplianceType

##############
# Parameters #
##############

# Define the default resource to report to Config Rules
DEFAULT_RESOURCE_TYPE = 'AWS::KMS::Key'

#############
# Main Code #
#############
MODULE = __import__('SCHEDULE_KEY_DELETION_ACCESS_RULE')
RULE = MODULE.SCHEDULE_KEY_DELETION_ACCESS_RULE()

CLIENT_FACTORY = MagicMock()
STS_CLIENT_MOCK = MagicMock()
KMS_CLIENT_MOCK = MagicMock()
IAM_CLIENT_MOCK = MagicMock()

def mock_get_client(client_name, *args, **kwargs):
    if client_name == 'sts':
        return STS_CLIENT_MOCK
    if client_name == 'kms':
        return KMS_CLIENT_MOCK
    if client_name == 'iam':
        return IAM_CLIENT_MOCK
    raise Exception("Attempting to create an unknown client")

@patch.object(CLIENT_FACTORY, 'build_client', MagicMock(side_effect=mock_get_client))
class ComplianceTest(unittest.TestCase):
    kms_key_list = {"Keys": [{"KeyId": "83de41d6-6530-49c1-9cb7-1de1560ce5tg"}]}
    event = rdklibtest.create_test_scheduled_event({})

    def test_invalid_parameter(self):
        invalid_rule_parameters = "{\"SomeOtherParameter\":\"arn:aws:iam::123456789123:role/KeyAdministratorRole\"}"
        with self.assertRaises(ValueError) as context:
            RULE.evaluate_parameters(invalid_rule_parameters)
        self.assertIn('InvalidParameterValueException', str(context.exception))

    def test_no_keys(self):
        rule_parameters = {}
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('NOT_APPLICABLE', '123456789012', 'AWS::::Account'))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_param_no_keys(self):
        rule_parameters = "{\"WhitelistedPrincipals\":[\"arn:aws:iam::123456789123:role/KeyAdministratorRole\", \"arn:aws:iam::123456789123:role/SecondKeyAdminRole\"]}"
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('NOT_APPLICABLE', '123456789012', 'AWS::::Account'))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_no_imported_key_material(self):
        rule_parameters = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "AWS_KMS", "KeyManager": "CUSTOMER"}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('NOT_APPLICABLE', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_no_param(self):
        rule_parameters = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Deny",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:ScheduleKeyDeletion", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'explicitDeny', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_noncompliant(self):
        rule_parameters = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:ScheduleKeyDeletion", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('NON_COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_param_compliant(self):
        rule_parameters = "{\"WhitelistedPrincipals\":[\"arn:aws:iam::123456789123:role/KeyAdministratorRole\", \"arn:aws:iam::123456789123:role/SecondKeyAdminRole\"]}"
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::123456789123:role/KeyAdministratorRole"    },    "Action" : [ "kms:ScheduleKeyDeletion", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_param_noncompliant(self):
        rule_parameters = "{\"WhitelistedPrincipals\":[\"arn:aws:iam::123456789123:role/KeyAdministratorRole\", \"arn:aws:iam::123456789123:role/SecondKeyAdminRole\"]}"
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : ["arn:aws:iam::123456789123:role/KeyAdministratorRole", "arn:aws:iam::712617248813:root"]   },    "Action" : [ "kms:ScheduleKeyDeletion", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('NONCOMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_disabled(self):
        rule_parameters = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Disabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Deny",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'implicitDeny', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_noncompliant_pending_del(self):
        rule_parameters = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "PendingDeletion", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:ScheduleKeyDeletion", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        event = rdklibtest.create_test_scheduled_event(rule_parameters)
        response = RULE.evaluate_periodic(event, CLIENT_FACTORY, rule_parameters)
        resp_expected = []
        resp_expected.append(Evaluation('NON_COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg', DEFAULT_RESOURCE_TYPE))
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)
