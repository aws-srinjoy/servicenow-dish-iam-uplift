## CDK Installation + Step by Step Installation

https://www.youtube.com/watch?v=AkybjHTmMtA

# Find unused IAM roles in your AWS Organization

This is an organizational config rule to find unused IAM roles in your AWS Organization. Roles unused for the specified period of time will appear as non-compliant in Config.

This can be deployed via the management account or another account that is delegated admin for stacksets and config.

## Resources deployment

* IAM execution role to management account and all member accounts. The member accounts are managed via a stack set.
* Lambda and corresponding IAM role to the management account or the delegated admin account. This IAM role will assume the IAM execution role in each account.
* Organization config rule deployed to the AWS organization.
* Email will be sent notifying all the respective application members containing their apps indicating the account the role was found in.

## Prerequisites

### Steps to be done on Bash/Iterm/Terminal/Cmd/Powershell

1. [Install Python3 ](https://www.python.org/downloads/)[and Pip (install venv)](https://pip.pypa.io/en/stable/installation/)

2. [Install Node](https://nodejs.org/en/download/)

3. [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

4. [Install CDK](https://docs.aws.amazon.com/cdk/latest/guide/cli.html)

5.  Configure AWS CLI with your Management account
>```aws configure```

### Steps to be done on Management Account Console
1. [Enable StackSet Trusted Access](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-enable-trusted-access.html)

2. [Enable Explorer](https://docs.aws.amazon.com/systems-manager/latest/userguide/Explorer-setup-delegated-administrator.html)

## Deployment steps

1. cd into the directory for deployment *Baxter IAM Uplift Solution*
>```cd Baxter IAM Uplift Solution```

2. create the virtual environment in the directory
>```python3 -m venv .venv```

3. After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.
>```source .venv/bin/activate```

4. If you are a _*Windows platform*_, you would activate the virtualenv like this:
>```.venv\Scripts\activate.bat```

5. Once the virtualenv is activated, you can install the required dependencies.
>```pip install -r requirements.txt```

6. Steps to be done on IDE/Notepad

    A. Update the file `\iam_role_last_used\iam_role_last_used_stack.py` reading the comments inside (NOTE: This is the main CDK Deployment python file.).

    B. Update the file `\functions\iam_role_last_used\app.py` reading the comments inside.

    C. Update the file `\iam-role.yaml` reading the comments inside.


7. The cdk synthesize command (almost always abbreviated synth ) synthesizes a stack defined in your app into a CloudFormation template.
>```cdk synth```

8. An environment needs to be bootstrapped before you can deploy stackset.(`Note`: this step is to be done only if CDK has not been used in the region of the stackset deployment.)   
>```cdk bootstrap aws://<account-id>/<region>```

9. You are now ready to deploy.
>```cdk deploy```

10. You can customize the maximum number of allowed days for unused IAM roles
>```cdk deploy --parameters MaxDaysForLastUsedRole=90```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `./test.sh`       Runs the config rule tests
  
## [Alternate Method] Deployment using a delegated admin account

1. [Enable StackSet Delegated Admin](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-delegated-admin.html)

2. [Register a delegated-admin for Explorer](https://docs.aws.amazon.com/systems-manager/latest/userguide/Explorer-setup-delegated-administrator.html)
