import json
import uuid
import re
import sys

from pathlib import Path


from aws_cdk import core, custom_resources as cr, aws_iam as iam

from iam_permissions_guardrails.constructs.service_control_policies import (
    ScpPolicyResource,
    ScpAttachmentResource,
)

from .role_hierarchy import RoleHierarchy


class ScpStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role_hierarchy = RoleHierarchy(self, "role-hierarchy", props)

        self.deploy_scp(
            role_hierarchy.service_control_policy_string,
            props["scp_name"],
            "Role permissions hierarchy",
            account_targets=[props["TEST_ACCOUNT_NUMBER"]],
        )

    def deploy_scp(
        self,
        service_control_policy_string,
        name,
        description,
        account_targets=[],
        organization_unit_targets=[],
    ):
        scp_file = Path("scp.json")
        scp_file.write_text(service_control_policy_string)

        trimmed_json = re.sub("\s+", "", service_control_policy_string)

        scp_size_before = sys.getsizeof(service_control_policy_string)
        scp_size_trimmed = sys.getsizeof(trimmed_json)

        if scp_size_trimmed > 5120:
            print(f"ERROR: SCP [{scp_size_trimmed} bytes] exceeds 5120 byte limit.")
            sys.exit(1)

        print(
            f"INFO: SCP size: {scp_size_trimmed} bytes, before was {scp_size_before} bytes"
        )

        scp_policy_resource = ScpPolicyResource(
            self,
            "test-scp-policy-resource",
            service_control_policy_string=trimmed_json,
            description=description,
            name=name,
        )

        ScpAttachmentResource(
            self,
            "test-attachment",
            policy_id=scp_policy_resource.policy_id,
            account_targets=account_targets,
            organization_unit_targets=organization_unit_targets,
        )

        """"
        physical_resource_id = cr.PhysicalResourceId.of(str(uuid.uuid4()))
        on_attach_policy = cr.AwsSdkCall(
            action="attachPolicy",
            service="Organizations",
            physical_resource_id=physical_resource_id,
            parameters={
                "PolicyId": policy_id,
                "TargetId": target_id,
            },
        )

        on_detach_policy = cr.AwsSdkCall(
            action="detachPolicy",
            service="Organizations",
            parameters={
                "PolicyId": policy_id,
                "TargetId": target_id,
            },
        )

        scp_attach_detach = cr.AwsCustomResource(
            self,
            "ServiceControlPolicyAttach",
            install_latest_aws_sdk=True,
            policy=policy,
            on_create=on_attach_policy,
            on_update=on_attach_policy,
            on_delete=on_detach_policy,
            resource_type="Custom::ServiceControlPolicyAttachDetach",
        )

        scp_attach_detach.node.add_dependency(scp_create)
        """
