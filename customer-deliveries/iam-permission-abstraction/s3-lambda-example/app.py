#!/usr/bin/env python3

from aws_cdk import core

from s3_lambda_example.s3_lambda_example_stack import S3LambdaExampleStack


app = core.App()
S3LambdaExampleStack(app, "s3-lambda-example")

app.synth()
