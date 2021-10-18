#!/usr/bin/env python3

from aws_cdk import core

from iam_best_practices.iam_best_practices_stack import IamBestPracticesStack
#from config_recorder_stack import ConfigRecorderStack
#from iam_config_setup_stack import IAMConfigSetupStack
#from config_setup_stack import ConfigSetupStack


app = core.App()
IamBestPracticesStack(app, "iam-best-practices")
#ConfigRecorderStack(app, "config-recorder-stack")
#IAMConfigSetupStack(app,"iam-config-setup-stack")
#ConfigSetupStack(app,"config-setup-stack")

app.synth()
