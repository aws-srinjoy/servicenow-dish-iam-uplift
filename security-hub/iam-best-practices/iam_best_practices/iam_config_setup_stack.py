from aws_cdk import (
  core,
  aws_iam as iam,
  aws_s3 as s3,
  aws_config
)

#https://github.com/aws/aws-cdk/issues/3492
class IAMConfigSetupStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    config_bucket=s3.Bucket(
      self,
      "ConfigBucket",
      versioned=True,
      block_public_access=s3.BlockPublicAccess.BLOCK_ALL
    )

    """
    config_role=iam.CfnServiceLinkedRole(
      self,
      "ConfigServiceLinkedRole",
      aws_service_name="config.amazonaws.com",
    )
    """

    config_role=iam.Role(
      self,
      "ConfigServiceRole",
      role_name="ConfigServiceRole",
      description="AWS Service Role For Config",
      assumed_by=iam.ServicePrincipal("config.amazonaws.com"),
      managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSConfigRole")],
    )

    config_role.add_to_policy(
        iam.PolicyStatement(
          sid="BucketPermissions1",
          effect=iam.Effect.ALLOW,
          actions=[
            "s3:PutObject"
          ],
          resources=[
            config_bucket.arn_for_objects("*"),
            config_bucket.arn_for_objects(f"AWSLogs/{core.Aws.ACCOUNT_ID}/Config/*"),
          ],
          conditions={
            "StringEquals": {
              "s3:x-amz-acl": "bucket-owner-full-control"
            }
          }
        ),
    )
    config_role.add_to_policy(
        iam.PolicyStatement(
          sid="BucketPermissions2",
          effect=iam.Effect.ALLOW,
          actions=[
            "s3:GetBucketAcl",
          ],
          resources=[
            config_bucket.bucket_arn,
          ]
        )
    )
    
    #config_bucket.grant_read_write(config_role)

    config_bucket.add_to_resource_policy(
        iam.PolicyStatement(
          sid="AWSConfigBucketPermissionsCheck",
          effect=iam.Effect.ALLOW,
          principals=[
            iam.ServicePrincipal("config.amazonaws.com"),
          ],
          actions=[
            "s3:GetBucketAcl",
          ],
          resources=[
            config_bucket.bucket_arn,
          ]
        )
    )

    config_bucket.add_to_resource_policy(
        iam.PolicyStatement(
          sid="AWSConfigBucketExistenceCheck",
          effect=iam.Effect.ALLOW,
          principals=[
            iam.ServicePrincipal("config.amazonaws.com"),
          ],
          actions=[
            "s3:ListBucket",
          ],
          resources=[
            config_bucket.bucket_arn,
          ]
        )
    )

    config_bucket.add_to_resource_policy(
        iam.PolicyStatement(
          sid="AWSConfigBucketDelivery",
          effect=iam.Effect.ALLOW,
          principals=[
            iam.ServicePrincipal("config.amazonaws.com"),
          ],
          actions=[
            "s3:PutObject"
          ],
          resources=[
            config_bucket.arn_for_objects("*"),
            config_bucket.arn_for_objects(f"AWSLogs/{core.Aws.ACCOUNT_ID}/Config/*"),
          ],
          conditions={
            "StringEquals": {
              "s3:x-amz-acl": "bucket-owner-full-control"
            }
          }
        )
    )

    core.CfnOutput(self,"ConfigRoleOutput",value=config_role.role_arn,description="Config Role",export_name=f"{self.stack_name}-ConfigRole")
    core.CfnOutput(self,"ConfigBucketOutput",value=config_bucket.bucket_arn,description="Config Bucket",export_name=f"{self.stack_name}-ConfigBucket")
