from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_lambda
)


class S3LambdaExampleStack(core.Stack):

 def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
  super().__init__(scope, id, **kwargs)

  bucket = s3.Bucket(
   self, "SourceBucket",
   bucket_name=f"test-{core.Aws.ACCOUNT_ID}-{core.Aws.REGION}",
   versioned=True)

  producer_lambda = aws_lambda.Function(
    self,
    "producer_lambda_function",
    runtime=aws_lambda.Runtime.PYTHON_3_6,
    handler="lambda_function.lambda_handler",
    code=aws_lambda.Code.asset("./lambda/producer")
  )
  bucket.grant_read_write(producer_lambda)

  producer_lambda2 = aws_lambda.Function(
    self,
    "producer_lambda_function2",
    runtime=aws_lambda.Runtime.PYTHON_3_6,
    handler="lambda_function.lambda_handler",
    code=aws_lambda.Code.asset("./lambda/producer")
  )
  bucket.grant_read(producer_lambda2)


  producer_lambda3 = aws_lambda.Function(
    self,
    "producer_lambda_function3",
    runtime=aws_lambda.Runtime.PYTHON_3_6,
    handler="lambda_function.lambda_handler",
    code=aws_lambda.Code.asset("./lambda/producer")
  )
  bucket.grant_write(producer_lambda3)


