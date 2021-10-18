from aws_cdk import (
    core,
    aws_iam as iam
)


class CreateTestIamRolesStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        for number in range(25):
            self.create_roles(number)

    def create_roles(self,number):
        #https://github.com/ohmer/cdk-cloudhealth-role/blob/d5419407abac8fa0d068e70e8090407dce3568af/cloudhealth/iam.py
        inline_policies={}
        inline_policies['ReadOnly'] = iam.PolicyDocument(statements=[iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            actions = [
                "aws-portal:ViewBilling",
                "aws-portal:ViewUsage",
                "autoscaling:Describe*",
                "cloudformation:ListStacks",
                "cloudformation:ListStackResources",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
                "cloudformation:DescribeStackResources",
                "cloudformation:GetTemplate",
                "cloudfront:Get*",
                "cloudfront:List*",
                "cloudtrail:Get*",
                "cloudtrail:DescribeTrails",
                "cloudtrail:ListTags",
                "cloudwatch:Describe*",
                "cloudwatch:Get*",
                "cloudwatch:List*",
                "config:Get*",
                "config:Describe*",
                "config:Deliver*",
                "config:List*",
                "cur:Describe*",
                "cur:PutReportDefinition",
                "dms:Describe*",
                "dynamodb:DescribeTable",
                "dynamodb:List*",
                "ec2:Describe*",
                "ec2:GetReservedInstancesExchangeQuote",
                "ecs:Describe*",
                "ecs:List*",
                "elasticache:Describe*",
                "elasticache:ListTagsForResource",
                "elasticbeanstalk:Check*",
                "elasticbeanstalk:Describe*",
                "elasticbeanstalk:List*",
                "elasticbeanstalk:RequestEnvironmentInfo",
                "elasticbeanstalk:RetrieveEnvironmentInfo",
                "elasticloadbalancing:Describe*",
                "elasticmapreduce:Describe*",
                "elasticmapreduce:List*",
                "elasticfilesystem:DescribeFileSystems",
                "elasticfilesystem:DescribeTags",
                "es:Describe*",
                "es:List*",
                "firehose:ListDeliveryStreams",
                "firehose:DescribeDeliveryStream",
                "iam:List*",
                "iam:Get*",
                "iam:GenerateCredentialReport",
                "kms:DescribeKey",
                "kms:GetKeyRotationStatus",
                "kms:ListKeys",
                "lambda:List*",
                "logs:Describe*",
                "redshift:Describe*",
                "route53:Get*",
                "route53:List*",
                "rds:Describe*",
                "rds:ListTagsForResource",
                "s3:List*",
                "s3:GetBucketAcl",
                "s3:GetBucketPolicy",
                "s3:GetBucketTagging",
                "s3:GetBucketLocation",
                "s3:GetBucketLogging",
                "s3:GetBucketVersioning",
                "s3:GetBucketWebsite",
                "sagemaker:Describe*",
                "sagemaker:List*",
                "sdb:GetAttributes",
                "sdb:List*",
                "ses:Get*",
                "ses:List*",
                "sns:Get*",
                "sns:List*",
                "sqs:GetQueueAttributes",
                "sqs:ListQueues",
                "storagegateway:List*",
                "storagegateway:Describe*",
                "workspaces:Describe*",
                "kinesis:Describe*",
                "kinesis:List*"
            ],
            resources = ["*"]
        )])
        inline_policies['AutomatedActions'] = iam.PolicyDocument(statements=[iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            actions = [
                "ec2:DeleteSnapshot",
                "ec2:DeleteVolume",
                "ec2:TerminateInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:RebootInstances",
                "lambda:InvokeFunction",
                "ec2:ReleaseAddress"
            ],
            resources = ["*"]
        )])
        test_bucket="asfdas"
        inline_policies['DBRAccess'] = iam.PolicyDocument(statements=[iam.PolicyStatement(
            effect = iam.Effect.DENY,
            actions = [
                "s3:Get*",
                "s3:List*"
            ],
            resources = [
                "arn:aws:s3:::{}".format(test_bucket),
                "arn:aws:s3:::{}/*".format(test_bucket)
            ]
        )])
        automation_role=iam.Role(
            self,
            f"EncryptRDSAutomationRole-{number}",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal('ssm.amazonaws.com'),
                iam.ServicePrincipal('rds.amazonaws.com')
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonSSMAutomationRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRDSFullAccess")
            ],
            inline_policies=inline_policies
        )
