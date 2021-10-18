#!/bin/bash
set -Eeuox pipefail

MasterAccountLambdaFunctionRoleArn="arn:aws:iam::913733971067:role/rdk/RDK-Config-Rule-Functions-rdkLambdaRole-13AZOQA6HVYBR"
Partition="aws"
AccountId="913733971067"

aws cloudformation create-stack-set \
    --stack-set-name 'KeyEvaluationExecutionRole' \
    --description 'Deploy key evaluation iam role to member accounts' \
    --template-body 'file://key_evaluation_execution_role.yaml' \
    --parameters ParameterKey=MasterAccountLambdaFunctionRoleArn,ParameterValue=${MasterAccountLambdaFunctionRoleArn} \
    --capabilities CAPABILITY_IAM \
    --administration-role-arn 'arn:${Partition}:iam::${AccountId}:role/AWSCloudFormationStackSetAdministrationRole' \
    --execution-role-name 'AWSCloudFormationStackSetExecutionRole'
