# IAM Blacklist Monitor

The following code is written in CloudFormation to detect if certain blacklisted IAM actions have occured in the AWS account. The blacklisted actions should be passed into the `BlacklistedActions` parameter of the CFN template as comma-separated values.
For example, `ListRoles, StopInstances, PutRole` would be a valid list. 

The code sets up the following AWS resources:
1. AWS::Event::Rule
2. AWS::Lambda::Function 
3. AWS::Lambda::Permission
4. AWS::IAM::Role (for the Lambda function)

Once the Cloudwatch Event rule sees a particular API call has been found in CloudTrail, it will notify an existing SNS topic which is defined by the `SNSTopic` parameter. 

## Deployment checklist
1. CloudTrail is enabled
2. Deploy stack in *us-east-1* or *us-gov-west-1* since these two regions currently support IAM events.
3. Input the appropriate blacklisted actions in the `BlacklistedActions` parameter of the stack
4. Input the SNS topic you would want to notify in case of any blacklisted actions happening `SNSTopic`
5. Put the `blacklist.zip` file in the desired bucket path , as determined by the `LambdaBucket` parameter
