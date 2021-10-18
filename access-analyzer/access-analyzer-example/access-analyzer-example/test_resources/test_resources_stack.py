from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_kms as kms,
  aws_iam as iam,
  aws_sqs as sqs,
  aws_lambda
)



class TestResourcesStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    block_access_analyzer_statement=iam.PolicyStatement(
      actions=["*"],
      effect=iam.Effect.DENY,
    )
    block_access_analyzer_statement.add_all_resources()
    """
    block_access_analyzer_statement.add_service_principal(
      service="access-analyzer.amazonaws.com"
    )
    """
    access_analyzer_principal_arn=f"arn:aws:iam::{self.account}:role/aws-service-role/access-analyzer.amazonaws.com/AWSServiceRoleForAccessAnalyzer"
    block_access_analyzer_statement.add_arn_principal(
      arn=access_analyzer_principal_arn
    )

    #s3
    s3_bucket=s3.Bucket(
      self,
      "S3TestBucket"
    )
    core.Tag.add(s3_bucket,"s3key","value")

    s3_bucket_no_tag=s3.Bucket(
      self,
      "NoTagS3Bucket"
    )
    s3_bucket_no_tag.add_to_resource_policy(
      iam.PolicyStatement(
          effect=iam.Effect.DENY,
          actions=["s3:*"],
          resources=[s3_bucket_no_tag.arn_for_objects("*"),s3_bucket_no_tag.bucket_arn],
          principals=[iam.ArnPrincipal(arn=access_analyzer_principal_arn)]
      )
    )

    s3_bucket_block_access_analyzer=s3.Bucket(
      self,
      "BlockAccessAnalyzer"
    )
    s3_bucket_block_access_analyzer.add_to_resource_policy(
      iam.PolicyStatement(
          effect=iam.Effect.DENY,
          actions=["s3:*"],
          resources=[s3_bucket_block_access_analyzer.arn_for_objects("*"),s3_bucket_block_access_analyzer.bucket_arn],
          principals=[iam.ArnPrincipal(arn=access_analyzer_principal_arn)]
      ) 
    ) 

    public_key=kms.Key(
      self,
      "AccidentalPublicKey",
      alias="accidental-public-key",
      enable_key_rotation=True
    )
    statement = iam.PolicyStatement(
      actions=["kms:Decrypt","kms:ScheduleKeyDeletion"],
      effect=iam.Effect.ALLOW
    )
    statement.add_any_principal()
    public_key.add_to_resource_policy(statement)
    core.Tag.add(public_key,"kmskey","value")

    block_key=kms.Key(
      self,
      "BlockedKey",
      alias="blocked-key",
      enable_key_rotation=True
    )
    block_key.add_to_resource_policy(block_access_analyzer_statement)


    #sqs
    public_queue=sqs.Queue(
      self,
      "AccidentalPublicSQSQueue"
    )
    core.Tag.add(public_queue,"sqskey","test")
    sqs_statement=iam.PolicyStatement(
      actions=["sqs:*"],
      effect=iam.Effect.ALLOW
    )
    sqs_statement.add_any_principal()
    public_queue.add_to_resource_policy(sqs_statement)

    #lambda layer
    runtime=aws_lambda.Runtime.PYTHON_3_8
    public_boto3_lambda_layer=aws_lambda.LayerVersion(
      self,
      "PublicBoto3LambdaLayer",
      code=aws_lambda.AssetCode("./layers/boto3"),
      compatible_runtimes=[runtime],
      description="Public Boto3 Lambda Layer"
    )
    core.Tag.add(public_boto3_lambda_layer,"lambdalayer","test")
    public_boto3_lambda_layer.add_permission(
      "PublicLayerPermissions",
      account_id="*"
    )
      
    #lambda function
    public_access_analyzer_finding_handler=aws_lambda.Function(
      self,
      "public_access_analyzer_finding_handler",
      runtime=runtime,
      handler="app.handler",
      code=aws_lambda.AssetCode("./functions/context-enrichment"),
    )
    core.Tag.add(public_access_analyzer_finding_handler,"lambdakey","test")
    public_access_analyzer_finding_handler.add_permission(
      "PublicLambdaPermission",
      principal=iam.AccountPrincipal("*"),
      action="lambda:*"
    ) 
