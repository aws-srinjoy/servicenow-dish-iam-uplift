import argparse

import json

import boto3


def get_scp_id(scp_name, organizations_client):
    paginator = organizations_client.get_paginator("list_policies")
    for page in paginator.paginate(Filter="SERVICE_CONTROL_POLICY"):
        for scp in page["Policies"]:
            if scp_name == scp["Name"]:
                return scp["Id"]


def print_scp_as_json(scp_id, organizations_client):
    policy = organizations_client.describe_policy(PolicyId=scp_id)["Policy"]
    content = policy["Content"]
    content_as_json = json.loads(content)
    print(json.dumps(content_as_json, indent=4))


def main(scp_name):
    organizations_client = boto3.client("organizations")
    scp_id = get_scp_id(scp_name, organizations_client)
    print_scp_as_json(scp_id, organizations_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scp_name", "-n", help="Service control policy name", required=True
    )
    args = parser.parse_args()
    main(args.scp_name)
