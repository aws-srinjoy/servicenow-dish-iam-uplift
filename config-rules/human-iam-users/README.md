This solution is to remediate human IAM users. It will filter for human IAM users by checking for '@' in the user name. Then, for any active access keys greater than the specified maxcredentialage days, it will deactivate those access keys.

This solution deploys
* boto3 Lambda layer
* Lambda that filters the IAM users and invokes an SSM document
* 2 IAM roles
* Cloudwatch event trigger that runs the Lambda every 24 hours

To deploy
```
cdk bootstrap

cdk deploy --parameters maxcredentialage=MAX_CREDENTIAL_AGE_HERE
```
