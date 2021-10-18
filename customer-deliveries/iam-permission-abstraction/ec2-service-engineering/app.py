#!/usr/bin/env python3

from aws_cdk import core

from ec2_service_engineering.ec2_service_engineering_stack import Ec2ServiceEngineeringStack


app = core.App()
Ec2ServiceEngineeringStack(app, "ec2-service-engineering")

app.synth()
