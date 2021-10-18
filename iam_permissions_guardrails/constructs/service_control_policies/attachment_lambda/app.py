import boto3
import json
import os
import uuid

def on_event(event, context):
    print(event)
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create(event)
    if request_type == "Update":
        return on_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception("Invalid request type: %s" % request_type)


def on_create(event):
    props = event["ResourceProperties"]
    print("create new resource with props %s" % props)

    policy_id = props["PolicyId"]
    account_targets = props["AccountTargets"]
    organization_unit_targets = props["OrganizationUnitTargets"]

    organizations_client = boto3.client("organizations")
    for account in account_targets:
        organizations_client.attach_policy(PolicyId=policy_id, TargetId=account)

    for organization_unit in organization_unit_targets:
        organizations_client.attach_policy(
            PolicyId=policy_id, TargetId=organization_unit
        )

    physical_resource_id = str(uuid.uuid4())
    return {"PhysicalResourceId": physical_resource_id}


def on_update(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    old_props = event["OldResourceProperties"]
    print(
        "update resource %s with props %s old props %s"
        % (physical_id, props, old_props)
    )

    policy_id = props["PolicyId"]
    account_targets = set(props["AccountTargets"])
    organization_unit_targets = set(props["OrganizationUnitTargets"])

    old_account_targets = set(old_props["AccountTargets"])
    old_organization_unit_targets = set(old_props["OrganizationUnitTargets"])

    account_intersection = old_account_targets.intersection(account_targets)
    to_detach_account_targets = old_account_targets - account_intersection
    to_attach_account_targets = account_targets - account_intersection

    organization_unit_intersection = old_organization_unit_targets.intersection(
        organization_unit_targets
    )
    to_detach_organization_targets = (
        old_organization_unit_targets - organization_unit_intersection
    )
    to_attach_organization_unit_targets = (
        organization_unit_targets - organization_unit_intersection
    )

    organizations_client = boto3.client("organizations")
    for account in to_detach_account_targets:
        organizations_client.detach_policy(PolicyId=policy_id, TargetId=account)

    for organization_unit in to_detach_organization_targets:
        organizations_client.detach_policy(
            PolicyId=policy_id, TargetId=organization_unit
        )

    for account in to_attach_account_targets:
        organizations_client.attach_policy(PolicyId=policy_id, TargetId=account)

    for organization_unit in to_attach_organization_unit_targets:
        organizations_client.attach_policy(
            PolicyId=policy_id, TargetId=organization_unit
        )


def on_delete(event):
    physical_id = event["PhysicalResourceId"]
    print("delete resource %s" % physical_id)
    props = event["ResourceProperties"]
    print("delete resource with props %s" % props)

    policy_id = props["PolicyId"]
    account_targets = props["AccountTargets"]
    organization_unit_targets = props["OrganizationUnitTargets"]

    organizations_client = boto3.client("organizations")
    for account in account_targets:
        organizations_client.detach_policy(PolicyId=policy_id, TargetId=account)

    for organization_unit in organization_unit_targets:
        organizations_client.detach_policy(
            PolicyId=policy_id, TargetId=organization_unit
        )

