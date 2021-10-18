
# Find unused IAM roles in your AWS Organization

This is an organizational config rule to find unused IAM roles in your AWS Organization. Roles unused for the specified period of time will appear as non-compliant in Config.

This can be deployed via the management account or another account that is delegated admin for stacksets and config.

## Resources deployment

* IAM execution role to management account and all member accounts. The member accounts are managed via a stack set.
* Lambda and corresponding IAM role to the management account or the delegated admin account. This IAM role will assume the IAM execution role in each account.
* Organization config rule deployed to the AWS organization.

# Deployment

# Virtual environment background

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

## Prerequisites

To manually create a virtualenv on MacOS and Linux:

```
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
.venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
pip install -r requirements.txt
```

## Steps to deploy

At this point you can now synthesize the CloudFormation template for this code.

```
cdk synth
```

You are now ready to deploy.
```
cdk deploy
```

You can customize the maximum number of allowed days for unused IAM roles
```
cdk deploy --parameters MaxDaysForLastUsedRole=90
```

## Vending new accounts

For new accounts vended, the Lambda resource policy permissions must be updated to allow Config in the new account to invoke the Lambda.

```
aws lambda add-permission 
  --function-name <function-name> 
  --region <region> 
  --statement-id <config-invoke-by-{member-account-id}> 
  --action "lambda:InvokeFunction" 
  --principal config.amazonaws.com 
  --source-account <member-account-id>
```

Separately, the stackset will take care of deploying the execution role in the new account. The organization config rule will take care of creating the config rule in the new account.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `./test.sh`       Runs the config rule tests

Enjoy!
