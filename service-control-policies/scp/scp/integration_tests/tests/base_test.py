import time
import unittest

from botocore.exceptions import ClientError


class BaseTestCase(unittest.TestCase):
    max_retry_attempts = 10

    def assert_access_denied_for(self, actions):
        """
        Assert that the provided action does receive an access denied error.
        We retry a certain number of attempts due to eventually consistent resources on the AWS side.
        """

        for action in actions:
            attempts = 0
            while attempts < self.max_retry_attempts:
                try:
                    action()
                except ClientError as e:
                    if e.response["Error"]["Code"] == "AccessDenied":
                        break
                    """
                    Might be other errors to log and need to fix, such as ValidationError
                    """
                    print(e)

                print(
                    "Expected access denied, but found access was allowed.  Retrying.."
                )
                attempts += 1
                time.sleep(1)

            if attempts == self.max_retry_attempts:
                self.fail("Expected access denied, but access was allowed.")

    def assert_access_allowed_for(self, actions):
        """
        Assert that the provided action does not receive an access denied error.
        We retry a certain number of attempts due to eventually consistent resources on the AWS side.
        """

        for action in actions:
            attempts = 0
            while attempts < self.max_retry_attempts:
                try:
                    action()
                    return
                except ClientError as e:
                    if e.response["Error"]["Code"] == "AccessDenied":
                        print(
                            "Expected access allowed, but found access was denied.  Retrying.."
                        )
                        attempts += 1
                        time.sleep(1)
                    print(e)

            if attempts == self.max_retry_attempts:
                self.fail("Expected access allowed, but access was denied.")
