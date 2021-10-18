class TestCleaner:
    def __init__(self, iam_client, test_resource_path):
        self.iam_client = iam_client
        self.test_resource_path = test_resource_path

    def clean_up_resources(self):
        self.__clean_up_roles()

    def __clean_up_roles(self):
        paginator = self.iam_client.get_paginator("list_roles")
        for page in paginator.paginate(PathPrefix=self.test_resource_path):
            for role in page["Roles"]:
                role_name = role["RoleName"]
                self.__clean_up_policies_attached_to(role_name)

                print(f"Cleaning up role {role_name}..")
                self.iam_client.delete_role(RoleName=role_name)

    def __clean_up_policies_attached_to(self, role_name):
        paginator = self.iam_client.get_paginator("list_attached_role_policies")
        for page in paginator.paginate(RoleName=role_name):
            for attached_policy in page["AttachedPolicies"]:
                policy_arn = attached_policy["PolicyArn"]

                print(f"Detaching policy {policy_arn} from role {role_name}..")
                self.iam_client.detach_role_policy(
                    RoleName=role_name, PolicyArn=attached_policy["PolicyArn"]
                )

                # only delete policies that we created
                if self.test_resource_path in policy_arn:
                    print(f"Cleaning up policy {policy_arn}..")
                    self.iam_client.delete_policy(PolicyArn=policy_arn)
