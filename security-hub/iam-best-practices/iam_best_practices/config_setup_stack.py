from aws_cdk import (
  core,
  aws_iam as iam,
  aws_s3 as s3,
  aws_config
)

#https://github.com/aws/aws-cdk/issues/3492
#https://github.com/aws/aws-cdk/issues/3577
class ConfigSetupStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    recording_group=aws_config.CfnConfigurationRecorder.RecordingGroupProperty(
      all_supported=True,
      include_global_resource_types=True,
    )

    config_recorder=aws_config.CfnConfigurationRecorder(
      self,
      "ConfigurationRecorder",
      #role_arn=f"arn:aws:iam::{core.Aws.ACCOUNT_ID}:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig",
      role_arn=core.Fn.import_value("iam-config-setup-stack-ConfigRole"),
      recording_group=recording_group,
    )

    #https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html
    config_snapshot_delivery_properties=aws_config.CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty(
      delivery_frequency="Six_Hours",
    )

    delivery_channel=aws_config.CfnDeliveryChannel(
      self,
      "CfnDeliveryChannel",
      s3_bucket_name=core.Fn.import_value("iam-config-setup-stack-ConfigBucket"),
      config_snapshot_delivery_properties=config_snapshot_delivery_properties,
    )

