from typing import List

import json
import uuid
import re
import sys

from pathlib import Path

from aws_cdk import core, custom_resources as cr, aws_iam as iam


class RoleHierarchy(core.Construct):
    # ways a role can be tagged on creation
    ON_CREATE_ACTIONS = ["iam:CreateRole"]
    # ways a role can be tagged either on creation or after creation
    TAGGING_ACTIONS = ["iam:CreateRole", "iam:TagRole"]
    # ways an existing role tags can be modified
    ROLE_TAG_MODIFICATION_ACTIONS = ["iam:TagRole", "iam:UntagRole"]
    # ways an existing role tag can be updated
    ROLE_TAG_UPDATE_ACTIONS = ["iam:TagRole"]
    # ways an existing role tag can be removed
    ROLE_TAG_REMOVAL_ACTIONS = ["iam:UntagRole"]
    # ways a role can be modified
    ROLE_MODIFICATION_ACTIONS = [
        "iam:AttachRolePolicy",
        "iam:DeleteRole",
        "iam:DeleteRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:UpdateAssumeRolePolicy",
        "iam:UpdateRole",
        "iam:UpdateRoleDescription",
    ]
    ROLE_ASSUME_PASS_ACTIONS = ["iam:PassRole", "sts:AssumeRole"]

    def __init__(self, scope: core.Construct, id: str, props):
        super().__init__(scope, id)

        self.LEVEL_KEY = props.get("LEVEL_KEY", "level")
        self.LEVEL0 = props.get("LEVEL0", "level0")
        self.LEVEL1 = props.get("LEVEL1", "level1")
        self.LEVEL2 = props.get("LEVEL2", "level2")
        self.LEVEL3 = props.get("LEVEL3", "level3")
        self.ALL_LEVELS = [self.LEVEL0, self.LEVEL1, self.LEVEL2, self.LEVEL3]

        scp_for_level0 = self.create_scp_for_level0()
        scp_for_level1 = self.create_scp_for_middle(
            level=self.LEVEL1, higher_levels=[self.LEVEL0]
        )
        scp_for_level2 = self.create_scp_for_middle(
            level=self.LEVEL2, higher_levels=[self.LEVEL0, self.LEVEL1]
        )
        scp_for_level3 = self.create_scp_for_leaf()
        specify_level_key = iam.PolicyDocument.from_json(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "MustPassLevelRequestTag",
                        "Effect": "Deny",
                        "Action": self.ON_CREATE_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "Null": {f"aws:RequestTag/{self.LEVEL_KEY}": "true"}
                        },
                    },
                    {
                        "Sid": "PreventTagRemoval",
                        "Effect": "Deny",
                        "Action": self.ROLE_TAG_REMOVAL_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "ForAnyValue:StringEquals": {
                                "aws:TagKeys": [f"{self.LEVEL_KEY}"]
                            }
                        },
                    },
                    {
                        "Sid": "ActingRoleMustHaveLevelPrincipalTag",
                        "Effect": "Deny",
                        "Action": self.TAGGING_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "Null": {f"aws:PrincipalTag/{self.LEVEL_KEY}": "true"}
                        },
                    },
                ],
            }
        )
        specify_level_key.validate_for_any_policy()

        # https://aws.amazon.com/premiumsupport/knowledge-center/iam-policy-tags-restrict/
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/access_tags.html#access_tags_control-requests
        restrict_level_keys = iam.PolicyDocument.from_json(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "RoleMustHaveTheseTagValuesForLevelTag",
                        "Effect": "Deny",
                        "Action": self.ROLE_TAG_UPDATE_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "ForAnyValue:StringNotEquals": {
                                f"aws:RequestTag/{self.LEVEL_KEY}": self.ALL_LEVELS
                            }
                        },
                    },
                    {
                        "Sid": "RoleMustHaveTheseTagKeys",
                        "Effect": "Deny",
                        "Action": self.ON_CREATE_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "StringNotEquals": {
                                f"aws:RequestTag/{self.LEVEL_KEY}": self.ALL_LEVELS
                            },
                            "ForAnyValue:StringNotEquals": {
                                "aws:TagKeys": [self.LEVEL_KEY]
                            },
                        },
                    },
                ],
            }
        )
        restrict_level_keys.validate_for_any_policy()

        statements_list = [
            specify_level_key,
            restrict_level_keys,
            scp_for_level0,
            scp_for_level1,
            scp_for_level2,
            scp_for_level3,
        ]
        service_control_policy_statements = {"Version": "2012-10-17", "Statement": []}
        for statement in statements_list:
            service_control_policy_statements["Statement"].extend(
                statement.to_json()["Statement"]
            )

        self.service_control_policy_string = json.dumps(
            service_control_policy_statements
        )

    def create_scp_for_level0(
        self,
    ):
        scp_for_level0 = iam.PolicyDocument.from_json(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": f"GuardTagUpdateOn{self.LEVEL0}",
                        "Effect": "Deny",
                        "Action": self.ROLE_TAG_UPDATE_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                f"iam:ResourceTag/{self.LEVEL_KEY}": [self.LEVEL0]
                            },
                            "StringNotEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": [self.LEVEL0]
                            },
                        },
                    },
                    {
                        "Sid": f"GuardCreateRoleOn{self.LEVEL0}",
                        "Effect": "Deny",
                        "Action": self.TAGGING_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                f"aws:RequestTag/{self.LEVEL_KEY}": self.LEVEL0
                            },
                            "StringNotEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": [self.LEVEL0]
                            },
                        },
                    },
                    {
                        "Sid": f"GuardRolesOnLevel{self.LEVEL0}",
                        "Effect": "Deny",
                        "Action": self.ROLE_MODIFICATION_ACTIONS
                        + self.ROLE_ASSUME_PASS_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                f"iam:ResourceTag/{self.LEVEL_KEY}": self.LEVEL0
                            },
                            "StringNotEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": [self.LEVEL0]
                            },
                        },
                    },
                ],
            }
        )
        scp_for_level0.validate_for_any_policy()
        return scp_for_level0

    def create_scp_for_leaf(self):
        scp_for_leaf = iam.PolicyDocument.from_json(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": f"TerminateTagPermissionAt{self.LEVEL3}",
                        "Effect": "Deny",
                        "Action": ["iam:TagRole"],
                        "Condition": {
                            "StringEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": [self.LEVEL3]
                            }
                        },
                        "Resource": "*",
                    },
                    {
                        "Sid": f"TerminateRoleManagementAt{self.LEVEL3}",
                        "Effect": "Deny",
                        "Action": self.ROLE_MODIFICATION_ACTIONS
                        + self.ROLE_TAG_MODIFICATION_ACTIONS
                        + self.ROLE_ASSUME_PASS_ACTIONS
                        + ["iam:CreateRole"],
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": [self.LEVEL3]
                            }
                        },
                    },
                ],
            }
        )
        scp_for_leaf.validate_for_any_policy()
        return scp_for_leaf

    def create_scp_for_middle(self, level: str, higher_levels: List[str]):
        scp_for_middle = iam.PolicyDocument.from_json(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": f"GuardTags{level}",
                        "Effect": "Deny",
                        "Action": self.ROLE_TAG_UPDATE_ACTIONS,
                        "Condition": {
                            "StringEquals": {
                                f"iam:ResourceTag/{self.LEVEL_KEY}": [level]
                            },
                            "StringNotEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": higher_levels
                            },
                        },
                        "Resource": "*",
                    },
                    {
                        "Sid": f"Restrict{level}",
                        "Effect": "Deny",
                        "Action": self.ROLE_TAG_UPDATE_ACTIONS,
                        "Condition": {
                            "StringEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": [level],
                                f"aws:RequestTag/{self.LEVEL_KEY}": higher_levels
                                + [level],
                            }
                        },
                        "Resource": "*",
                    },
                    {
                        "Sid": f"GuardTagRoleOn{level}",
                        "Effect": "Deny",
                        "Action": self.TAGGING_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                f"aws:RequestTag/{self.LEVEL_KEY}": [level]
                            },
                            "StringNotEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": higher_levels
                            },
                        },
                    },
                    {
                        "Sid": f"GuardRolesOn{level}",
                        "Effect": "Deny",
                        "Action": self.ROLE_MODIFICATION_ACTIONS
                        + self.ROLE_ASSUME_PASS_ACTIONS,
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                f"iam:ResourceTag/{self.LEVEL_KEY}": level
                            },
                            "StringNotEquals": {
                                f"aws:PrincipalTag/{self.LEVEL_KEY}": higher_levels
                            },
                        },
                    },
                ],
            }
        )
        scp_for_middle.validate_for_any_policy()
        return scp_for_middle
