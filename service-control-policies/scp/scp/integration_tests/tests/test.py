import boto3
import time
import uuid

from botocore.exceptions import ClientError
from pathlib import Path

from base_test import BaseTestCase
from cleanup import TestCleaner


# select the profile that contains the credentials for the environment in which to run the test
session = boto3.Session()
iam_client = session.client("iam")
sts_client = session.client("sts")

# this is the role/policy path assigned to all resources created in this test so that they can be cleaned up on each run
test_resource_path = "/automated-tests/abac-scps/"

cleaner = TestCleaner(iam_client, test_resource_path)
cleaner.clean_up_resources()

LEVEL_KEY = "scp-testing-level-key"
LEVEL0 = "level0"
LEVEL1 = "level1"
LEVEL2 = "level2"
LEVEL3 = "level3"

OTHER_TAG_KEY = "COSTCENTER"
OTHER_TAG_VALUE = "somevalue"

INVALID_LEVEL = "99"
INVALID_KEY = "invalidkey"


class WhenRoleHasLevelTwoPermission(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls.role_under_test = RoleUnderTest(level=LEVEL2)

    @classmethod
    def tearDownClass(cls):
        cleaner.clean_up_resources()

    def test_tagging_level_two_role(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_level_one_role(self):
        self.target_role = Role(level=LEVEL1)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_level_zero_role(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_other_keys(self):
        self.target_role = Role(level=LEVEL3)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role,
                    with_level=OTHER_TAG_VALUE,
                    with_key=OTHER_TAG_KEY,
                ),
            ]
        )

    def test_create_role_level_same_or_above(self):
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=LEVEL0),
                lambda: self.role_under_test.create_role(with_level=LEVEL1),
                lambda: self.role_under_test.create_role(with_level=LEVEL2),
            ]
        )

    def test_create_role_invalid_level(self):
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=INVALID_LEVEL),
            ]
        )

    def test_untag_level_key(self):
        self.target_role = Role(level=LEVEL3)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.untag(target=self.target_role),
            ]
        )


class WhenRoleHasLevelOnePermission(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls.role_under_test = RoleUnderTest(level=LEVEL1)

    @classmethod
    def tearDownClass(cls):
        cleaner.clean_up_resources()

    def test_tagging_level_invalid_level(self):
        self.target_role = Role(level=LEVEL1)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=INVALID_LEVEL
                ),
            ]
        )

    def test_tagging_level_two_role(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                )
            ]
        )
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_level_one_role(self):
        self.target_role = Role(level=LEVEL1)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_level_zero_role(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_other_keys(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role,
                    with_level=OTHER_TAG_VALUE,
                    with_key=OTHER_TAG_KEY,
                ),
            ]
        )

    def test_attach_policy_level_two_role(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.attach_policy_to(target=self.target_role)
            ]
        )

    def test_attach_policy_level_one_role(self):
        self.target_role = Role(level=LEVEL1)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.attach_policy_to(target=self.target_role)
            ]
        )

    def test_attach_policy_level_zero_role(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.attach_policy_to(target=self.target_role)
            ]
        )

    def test_create_role_level_same_or_above(self):
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=LEVEL0),
                lambda: self.role_under_test.create_role(with_level=LEVEL1),
            ]
        )

    def test_create_role_level_below(self):
        self.assert_access_allowed_for(
            actions=[lambda: self.role_under_test.create_role(with_level=LEVEL2)]
        )

    def test_create_role_invalid_level(self):
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=INVALID_LEVEL),
            ]
        )

    def test_untag_level_key(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.untag(target=self.target_role),
            ]
        )


class WhenRoleHasLevelZeroPermission(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls.role_under_test = RoleUnderTest(level=LEVEL0)

    @classmethod
    def tearDownClass(cls):
        cleaner.clean_up_resources()

    def test_tagging_level_invalid_level(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=INVALID_LEVEL
                ),
            ]
        )

    def test_tagging_level_two_role(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL3
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_level_one_role(self):
        self.target_role = Role(level=LEVEL1)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL3
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
            ]
        )

    def test_tagging_level_zero_role(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL0
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL1
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL2
                ),
                lambda: self.role_under_test.tag(
                    target=self.target_role, with_level=LEVEL3
                ),
            ]
        )

    def test_tagging_other_keys(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.tag(
                    target=self.target_role,
                    with_level=OTHER_TAG_VALUE,
                    with_key=OTHER_TAG_KEY,
                ),
            ]
        )

    def test_attach_policy_level_two_role(self):
        self.target_role = Role(level=LEVEL2)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.attach_policy_to(target=self.target_role)
            ]
        )

    def test_attach_policy_level_one_role(self):
        self.target_role = Role(level=LEVEL1)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.attach_policy_to(target=self.target_role)
            ]
        )

    def test_attach_policy_level_zero_role(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.attach_policy_to(target=self.target_role)
            ]
        )

    def test_create_role_level_same_or_above(self):
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=LEVEL0),
            ]
        )

    def test_create_role_level_below(self):
        self.assert_access_allowed_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=LEVEL1),
                lambda: self.role_under_test.create_role(with_level=LEVEL2),
                lambda: self.role_under_test.create_role(with_level=LEVEL3),
            ]
        )

    def test_create_role_invalid_level(self):
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.create_role(with_level=INVALID_LEVEL),
            ]
        )

    def test_create_role_invalid_tag_key(self):
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.create_role(
                    with_level=LEVEL1, tag_key=INVALID_KEY
                ),
                lambda: self.role_under_test.create_role(
                    with_level=LEVEL2, tag_key=INVALID_KEY
                ),
            ]
        )

    def test_untag_level_key(self):
        self.target_role = Role(level=LEVEL0)
        self.assert_access_denied_for(
            actions=[
                lambda: self.role_under_test.untag(target=self.target_role),
            ]
        )


class Role:
    def __init__(self, level):
        self.level = level

        level_tag_value = self._build_level_tag_value(level)
        self.name = f"abac-test-{level_tag_value}-{uuid.uuid4()}"

        print(f"Creating role {self.name} at level {level}..")
        role = iam_client.create_role(
            Path=test_resource_path,
            RoleName=self.name,
            AssumeRolePolicyDocument=self._build_assume_role_policy_document(),
            Tags=[{"Key": LEVEL_KEY, "Value": level_tag_value}],
        )

        self.arn = role["Role"]["Arn"]
        self.assumed_iam_client = None

    @staticmethod
    def _build_level_tag_value(level):
        # return f"level{level}" if str(level).isdigit() else level
        return level

    @staticmethod
    def _build_assume_role_policy_document():
        assume_role_policy_document = Path("assume_role_policy_doc.json").read_text()
        account_id = sts_client.get_caller_identity()["Account"]
        print(f"Using account {account_id} for the trust policy")
        return assume_role_policy_document.replace("{AccountId}", account_id)

    def delete(self):
        iam_client.delete_role(RoleName=self.name)


class RoleUnderTest(Role):
    def __init__(self, level):
        super().__init__(level)
        policy_document = Path("policy.json").read_text()
        policy = iam_client.create_policy(
            Path=test_resource_path,
            PolicyName=str(uuid.uuid4()),
            PolicyDocument=policy_document,
        )
        self.policy_arn = policy["Policy"]["Arn"]
        iam_client.attach_role_policy(RoleName=self.name, PolicyArn=self.policy_arn)

    def create_role(self, with_level, tag_key=LEVEL_KEY):
        assumed_iam_client = self.__assume_this_role()

        level_tag_value = self._build_level_tag_value(with_level)
        name = f"abac-tests-{tag_key}-{level_tag_value}-{uuid.uuid4()}"
        name = name[:64]
        print(
            f"Attempting to create role {tag_key},{level_tag_value} as level {self.level}.."
        )
        assumed_iam_client.create_role(
            Path=test_resource_path,
            RoleName=name,
            AssumeRolePolicyDocument=self._build_assume_role_policy_document(),
            Tags=[{"Key": tag_key, "Value": level_tag_value}],
        )

    def attach_policy_to(self, target):
        print(f"Attaching policy to level {target.level} as level {self.level}")
        assumed_iam_client = self.__assume_this_role()

        assumed_iam_client.attach_role_policy(
            RoleName=target.name,
            PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",
        )

    def tag(self, target, with_level, with_key=LEVEL_KEY):
        level_tag_value = self._build_level_tag_value(with_level)

        print(
            f"Tagging role {target.name} that is level {target.level} with {with_key},{with_level} as role {self.name} with level {self.level}"
        )
        assumed_iam_client = self.__assume_this_role()
        assumed_iam_client.tag_role(
            RoleName=target.name, Tags=[{"Key": with_key, "Value": level_tag_value}]
        )

        # revert back to the original level for subsequent tests if the above is successful
        assumed_iam_client.tag_role(
            RoleName=target.name, Tags=[{"Key": with_key, "Value": target.level}]
        )

    def untag(self, target, with_key=LEVEL_KEY):
        assumed_iam_client = self.__assume_this_role()
        assumed_iam_client.untag_role(RoleName=target.name, TagKeys=[with_key])

    def __assume_this_role(self):
        """
        The role may not be assumable immediately after it's created due to eventual consistency.
        We'll retry until we're able to successfully assume the role.
        """

        if self.assumed_iam_client is not None:
            return self.assumed_iam_client

        awaiting_role_creation = True
        max_retry_attempts = 10
        attempts = 0
        while awaiting_role_creation and attempts < max_retry_attempts:
            try:
                response = sts_client.assume_role(
                    RoleArn=self.arn, RoleSessionName=str(uuid.uuid4())
                )
                awaiting_role_creation = False
                print("Assuming role..")
            except ClientError as e:
                print(e)
                if e.response["Error"]["Code"] != "AccessDenied":
                    raise e
                else:
                    print(f"Waiting for level {self.level} role to be assumable..")
                    time.sleep(2)
            attempts += 1

        if attempts == max_retry_attempts:
            self.fail("Unable to assume role.")

        self.assumed_iam_client = boto3.client(
            "iam",
            aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
            aws_session_token=response["Credentials"]["SessionToken"],
        )
        return self.assumed_iam_client
