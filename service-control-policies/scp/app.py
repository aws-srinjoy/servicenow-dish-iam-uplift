#!/usr/bin/env python3
import os, sys

from aws_cdk import core

# from scp.scp_stack import ScpStack

from scp.pipeline_stack import PipelineStack

app = core.App()
# ScpStack(app, "service-control-policy-deny-self-update")

#from git import Repo
#repo=Repo(".",search_parent_directories=True)

props={}
branch_key=f"branch:primary-account={os.environ['CDK_DEFAULT_ACCOUNT']}"
props["BRANCH"]=app.node.try_get_context(branch_key)
#props["BRANCH"]=str(repo.active_branch)
test_account_number_key=f"test-account-number:primary-account={os.environ['CDK_DEFAULT_ACCOUNT']}"
props["TEST_ACCOUNT_NUMBER"]=app.node.try_get_context(test_account_number_key)

if not props["BRANCH"]:
    sys.exit(f"branch must be specified as context value {branch_key}")
    #sys.exit("unable to determine git branch")
if not props["TEST_ACCOUNT_NUMBER"]:
    sys.exit(f"test account must be specified as {test_account_number_key}")

PipelineStack(
    app,
    "scp-pipeline",
    props=props,
    env={"region": "us-east-1", "account": os.environ['CDK_DEFAULT_ACCOUNT']},
)

app.synth()
