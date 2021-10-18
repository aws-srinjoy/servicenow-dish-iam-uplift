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

import sys
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
import botocore

##############
# Parameters #
##############

# Define the default resource to report to Config Rules
DEFAULT_RESOURCE_TYPE = 'AWS::KMS::Key'

#############
# Main Code #
#############

CONFIG_CLIENT_MOCK = MagicMock()
STS_CLIENT_MOCK = MagicMock()
KMS_CLIENT_MOCK = MagicMock()
IAM_CLIENT_MOCK = MagicMock()

class Boto3Mock():
    @staticmethod
    def client(client_name, *args, **kwargs):
        if client_name == 'config':
            return CONFIG_CLIENT_MOCK
        if client_name == 'sts':
            return STS_CLIENT_MOCK
        if client_name == 'kms':
            return KMS_CLIENT_MOCK
        if client_name == 'iam':
            return IAM_CLIENT_MOCK
        raise Exception("Attempting to create an unknown client")

sys.modules['boto3'] = Boto3Mock()

RULE = __import__('IMPORTED_KEY_MATERIAL_NOT_DELETE_PERMISSION')

class ComplianceTest(unittest.TestCase):
    kms_key_list = {"Keys": [{"KeyId": "83de41d6-6530-49c1-9cb7-1de1560ce5tg"}]}

    def setUp(self):
        pass

    def test_invalid_parameter(self):
        rule_param = "{\"WhitelistedPrincipals\":\"arn:aws:iam::123456789123:role/KeyAdministratorRole\"}"
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        assert_customer_error_response(self, response, 'InvalidParameterValueException', customer_error_message='WhitelistedPrincipalArns not in rule parameters.')

    def test_no_keys(self):
        rule_param = {}
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('NOT_APPLICABLE', '123456789012', 'AWS::::Account'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_param_no_keys(self):
        rule_param = "{\"WhitelistedPrincipals\":[\"arn:aws:iam::123456789123:role/KeyAdministratorRole\", \"arn:aws:iam::123456789123:role/SecondKeyAdminRole\"]}"
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('NOT_APPLICABLE', '123456789012', 'AWS::::Account'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_no_imported_key_material(self):
        rule_param = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "AWS_KMS", "KeyManager": "CUSTOMER"}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('NOT_APPLICABLE', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_no_param(self):
        rule_param = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Deny",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:DeleteImportedKeyMaterial", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'explicitDeny', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_noncompliant(self):
        rule_param = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:DeleteImportedKeyMaterial", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:DeleteImportedKeyMaterial', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('NON_COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_param_compliant(self):
        rule_param = "{\"WhitelistedPrincipals\":[\"arn:aws:iam::123456789123:role/KeyAdministratorRole\", \"arn:aws:iam::123456789123:role/SecondKeyAdminRole\"]}"
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::123456789123:role/KeyAdministratorRole"    },    "Action" : [ "kms:DeleteImportedKeyMaterial", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:DeleteImportedKeyMaterial', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_param_noncompliant(self):
        rule_param = "{\"WhitelistedPrincipals\":[\"arn:aws:iam::123456789123:role/KeyAdministratorRole\", \"arn:aws:iam::123456789123:role/SecondKeyAdminRole\"]}"
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Enabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : ["arn:aws:iam::123456789123:role/KeyAdministratorRole", "arn:aws:iam::712617248813:root"]   },    "Action" : [ "kms:DeleteImportedKeyMaterial", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:DeleteImportedKeyMaterial', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('NONCOMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_disabled(self):
        rule_param = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "Disabled", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Deny",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:ScheduleKeyDeletion', 'EvalResourceName': '*', 'EvalDecision': 'implicitDeny', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_no_param_noncompliant_pending_del(self):
        rule_param = {}
        KMS_CLIENT_MOCK.list_keys = MagicMock(return_value=self.kms_key_list)
        KMS_CLIENT_MOCK.describe_key = MagicMock(return_value={"KeyMetadata": {"KeyState": "PendingDeletion", "Origin": "EXTERNAL", "KeyManager": "CUSTOMER"}})
        KMS_CLIENT_MOCK.get_key_policy = MagicMock(return_value={'Policy': '{  "Version" : "2012-10-17",  "Id" : "auto-s3-2",  "Statement" : [ {    "Sid" : "Allow access through S3 for all principals in the account that are authorized to use S3",    "Effect" : "Allow",    "Principal" : {      "AWS" : "*"    },    "Action" : [ "kms:DeleteImportedKeyMaterial", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey" ],    "Resource" : "*",    "Condition" : {      "StringEquals" : {        "kms:ViaService" : "s3.us-east-1.amazonaws.com",        "kms:CallerAccount" : "631273466110"      }    }  }, {    "Sid" : "Allow direct access to key metadata to the account",    "Effect" : "Allow",    "Principal" : {      "AWS" : "arn:aws:iam::631273466110:root"    },    "Action" : [ "kms:Describe*", "kms:Get*", "kms:List*" ],    "Resource" : "*"  } ]}', 'ResponseMetadata': {'RequestId': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0bc488c0-e54b-446b-bdb6-392214dc712b', 'cache-control': 'no-cache, no-store, must-revalidate, private', 'expires': '0', 'pragma': 'no-cache', 'date': 'Wed, 20 Nov 2019 12:34:53 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '914'}, 'RetryAttempts': 0}})
        IAM_CLIENT_MOCK.simulate_custom_policy = MagicMock(return_value={'EvaluationResults': [{'EvalActionName': 'kms:DeleteImportedKeyMaterial', 'EvalResourceName': '*', 'EvalDecision': 'allowed', 'MatchedStatements': [{'SourcePolicyId': 'PolicyInputList.1', 'StartPosition': {'Line': 1, 'Column': 41}, 'EndPosition': {'Line': 1, 'Column': 368}}], 'MissingContextValues': []}], 'IsTruncated': False, 'ResponseMetadata': {'RequestId': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '523969d9-f085-4bb2-929c-bd0037d3e8da', 'content-type': 'text/xml', 'content-length': '985', 'date': 'Wed, 20 Nov 2019 12:34:52 GMT'}, 'RetryAttempts': 0}})
        lambda_event = build_lambda_scheduled_event(rule_parameters=rule_param)
        response = RULE.lambda_handler(lambda_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response('NON_COMPLIANT', '83de41d6-6530-49c1-9cb7-1de1560ce5tg'))
        assert_successful_evaluation(self, response, resp_expected)

####################
# Helper Functions #
####################

def build_lambda_configurationchange_event(invoking_event, rule_parameters=None):
    event_to_return = {
        'configRuleName':'myrule',
        'executionRoleArn':'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken':'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return

def build_lambda_scheduled_event(rule_parameters=None):
    invoking_event = '{"messageType":"ScheduledNotification","notificationCreationTime":"2017-12-23T22:11:18.158Z"}'
    event_to_return = {
        'configRuleName':'myrule',
        'executionRoleArn':'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken':'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return

def build_expected_response(compliance_type, compliance_resource_id, compliance_resource_type=DEFAULT_RESOURCE_TYPE, annotation=None):
    if not annotation:
        return {
            'ComplianceType': compliance_type,
            'ComplianceResourceId': compliance_resource_id,
            'ComplianceResourceType': compliance_resource_type
            }
    return {
        'ComplianceType': compliance_type,
        'ComplianceResourceId': compliance_resource_id,
        'ComplianceResourceType': compliance_resource_type,
        'Annotation': annotation
        }

def assert_successful_evaluation(test_class, response, resp_expected, evaluations_count=1):
    if isinstance(response, dict):
        test_class.assertEquals(resp_expected['ComplianceResourceType'], response['ComplianceResourceType'])
        test_class.assertEquals(resp_expected['ComplianceResourceId'], response['ComplianceResourceId'])
        test_class.assertEquals(resp_expected['ComplianceType'], response['ComplianceType'])
        test_class.assertTrue(response['OrderingTimestamp'])
        if 'Annotation' in resp_expected or 'Annotation' in response:
            test_class.assertEquals(resp_expected['Annotation'], response['Annotation'])
    elif isinstance(response, list):
        test_class.assertEquals(evaluations_count, len(response))
        for i, response_expected in enumerate(resp_expected):
            test_class.assertEquals(response_expected['ComplianceResourceType'], response[i]['ComplianceResourceType'])
            test_class.assertEquals(response_expected['ComplianceResourceId'], response[i]['ComplianceResourceId'])
            test_class.assertEquals(response_expected['ComplianceType'], response[i]['ComplianceType'])
            test_class.assertTrue(response[i]['OrderingTimestamp'])
            if 'Annotation' in response_expected or 'Annotation' in response[i]:
                test_class.assertEquals(response_expected['Annotation'], response[i]['Annotation'])

def assert_customer_error_response(test_class, response, customer_error_code=None, customer_error_message=None):
    if customer_error_code:
        test_class.assertEqual(customer_error_code, response['customerErrorCode'])
    if customer_error_message:
        test_class.assertEqual(customer_error_message, response['customerErrorMessage'])
    test_class.assertTrue(response['customerErrorCode'])
    test_class.assertTrue(response['customerErrorMessage'])
    if "internalErrorMessage" in response:
        test_class.assertTrue(response['internalErrorMessage'])
    if "internalErrorDetails" in response:
        test_class.assertTrue(response['internalErrorDetails'])

def sts_mock():
    assume_role_response = {
        "Credentials": {
            "AccessKeyId": "string",
            "SecretAccessKey": "string",
            "SessionToken": "string"}}
    STS_CLIENT_MOCK.reset_mock(return_value=True)
    STS_CLIENT_MOCK.assume_role = MagicMock(return_value=assume_role_response)

##################
# Common Testing #
##################

class TestStsErrors(unittest.TestCase):

    def test_sts_unknown_error(self):
        RULE.ASSUME_ROLE_MODE = True
        RULE.evaluate_parameters = MagicMock(return_value=True)
        STS_CLIENT_MOCK.assume_role = MagicMock(side_effect=botocore.exceptions.ClientError(
            {'Error': {'Code': 'unknown-code', 'Message': 'unknown-message'}}, 'operation'))
        response = RULE.lambda_handler(build_lambda_configurationchange_event('{}'), {})
        assert_customer_error_response(
            self, response, 'InternalError', 'InternalError')

    def test_sts_access_denied(self):
        RULE.ASSUME_ROLE_MODE = True
        RULE.evaluate_parameters = MagicMock(return_value=True)
        STS_CLIENT_MOCK.assume_role = MagicMock(side_effect=botocore.exceptions.ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'access-denied'}}, 'operation'))
        response = RULE.lambda_handler(build_lambda_configurationchange_event('{}'), {})
        assert_customer_error_response(
            self, response, 'AccessDenied', 'AWS Config does not have permission to assume the IAM role.')
