from aws_cdk import (
    core,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_applicationautoscaling as applicationautoscaling,
)


class FargateTaskStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        enable_security_hub_parameter = core.CfnParameter(
            self,
            "EnableSecurityHub",
            default="False",
            description="Send findings to AWS Security Hub",
            allowed_values=["True", "False"],
        )

        email_notification_address_parameter = core.CfnParameter(
            self,
            "EmailNotificationAddress",
            default="",
            description="Email Notification Address to notify when the IAM Assessment tool has completed.",
        )

        results_bucket = s3.Bucket(
            self,
            "IAMPermissionsGuardrailsResults",
            versioned=True,
            encryption=s3.BucketEncryption.KMS_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        target_subnet = ec2.SubnetType.ISOLATED
        target_subnet = ec2.SubnetType.PRIVATE

        vpc = ec2.Vpc(
            self,
            "IAMPermissionsGuardrailsVPC",
            max_azs=3,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="assessment-public", subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="assessment-private", subnet_type=target_subnet
                ),
            ],
            flow_logs=ec2.FlowLogOptions(
                destination=ec2.FlowLogDestination.to_cloud_watch_logs(),
                traffic_type=ec2.FlowLogTrafficType.ALL,
            ),
        )
        security_group = ec2.SecurityGroup.from_security_group_id(
            self, "test", security_group_id=vpc.vpc_default_security_group
        )
        """
        vpc.add_gateway_endpoint(
          "IAMPermissionsGuardrailsVPCS3Endpoint",
          service=ec2.GatewayVpcEndpointAwsService('S3'),
          subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)]
        )
        """
        vpc.add_s3_endpoint(
            id="IAMPermissionsGuardrailsVPCS3Endpoint",
            subnets=[ec2.SubnetSelection(subnet_type=target_subnet)],
        )
        vpc.add_interface_endpoint(
            id="IAMPermissionsGuardrailsVPCECREndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(subnet_type=target_subnet),
        )
        vpc.add_interface_endpoint(
            id="IAMPermissionsGuardrailsVPCECRDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(subnet_type=target_subnet),
        )
        vpc.add_interface_endpoint(
            id="IAMPermissionsGuardrailsVPCCLOUDWATCHEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(subnet_type=target_subnet),
        )
        vpc.add_interface_endpoint(
            id="IAMPermissionsGuardrailsVPCCLOUDWATCHLOGSEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(subnet_type=target_subnet),
        )

        vpc.add_interface_endpoint(
            id="IAMPermissionsGuardrailsSTSVPCEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.STS,
            private_dns_enabled=True,
            security_groups=[security_group],
            subnets=ec2.SubnetSelection(subnet_type=target_subnet),
        )

        vpc.add_flow_log(
            "IAMPermissionsGuardrailsFlowLogCloudWatch",
            traffic_type=ec2.FlowLogTrafficType.REJECT,
        )

        cluster = ecs.Cluster(self, "IAMPermissionsGuardrailsCluster", vpc=vpc)
        """
        scheduled_fargate_task_image_options=ecs_patterns.ScheduledFargateTaskImageOptions(
          image=ecs.ContainerImage.from_ecr_repository(
            repository=ecr.Repository.from_repository_name(
              self,
              "IAMPermissionGuardrailsECR",
              repository_name="iam-permissions-guardrails"
            )
          ),
          cpu=512,
          memory_limit_mib=2048
        )
        ecs_patterns.ScheduledFargateTask(self, "IAMPermissionsGuardrailsFargateService",
            cluster=cluster,
            desired_task_count=1,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED),
            scheduled_fargate_task_image_options=scheduled_fargate_task_image_options,
            schedule=applicationautoscaling.Schedule.expression("rate(7 days)")
        )
        """

        # security_group
        # https://stackoverflow.com/questions/59067514/aws-cdk-ecs-task-scheduling-specify-existing-securitygroup
        task_definition = ecs.FargateTaskDefinition(
            self,
            id="IAMPermissionsGuardrailsTaskDefinition",
            cpu=512,
            memory_limit_mib=2048,
        )
        container_definition = task_definition.add_container(
            id="IAMPermissionsGuardrailsTaskDefinitionContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr.Repository.from_repository_name(
                    self,
                    "IAMPermissionGuardrailsECR",
                    repository_name="iam-permissions-guardrails",
                )
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix="iam-permissions-guardrails"),
            environment={
                "AWS_REGION": core.Aws.REGION,
                "ENABLE_SECURITY_HUB_INTEGRATION": enable_security_hub_parameter.value_as_string,
                "NOTIFICATION_EMAIL_ADDRESS": email_notification_address_parameter.value_as_string,
                "S3_BUCKET": results_bucket.bucket_name,
            },
        )
        # for the application
        statements = [
            iam.PolicyStatement(
                actions=[
                    "iam:GetAccountAuthorizationDetails",
                    "iam:GetRolePolicy",
                    "iam:ListAttachedRolePolicies",
                    "iam:GetRole",
                    "iam:ListRolePolicies",
                    "iam:ListAccessKeys",
                    "iam:GetPolicyVersion",
                    "iam:ListUsers",
                    "iam:ListSAMLProviders",
                    "iam:ListRoles",
                    "iam:GetPolicy",
                    "iam:GenerateServiceLastAccessedDetails",
                    "iam:GetServiceLastAccessedDetails",
                    "iam:SimulatePrincipalPolicy",
                ],
                resources=["*"],
            ),
            iam.PolicyStatement(
                actions=[
                    "ec2:DescribeVpcEndpoints",
                    "ec2:DescribeKeyPairs",
                    "ec2:DescribeInstances",
                    "ec2:DescribeRegions",
                ],
                resources=["*"],
            ),
            iam.PolicyStatement(actions=["cloudtrail:LookupEvents"], resources=["*"]),
            iam.PolicyStatement(
                actions=[
                    "access-analyzer:ListAnalyzers",
                    "access-analyzer:ListFindings",
                    "access-analyzer:ValidatePolicy"
                ],
                resources=["*"],
            ),
            iam.PolicyStatement(
                actions=["ssm:DescribeInstanceInformation"], resources=["*"]
            ),
            iam.PolicyStatement(
                actions=["s3:ListAllMyBuckets", "s3:GetReplicationConfiguration"],
                resources=["*"],
            ),
            iam.PolicyStatement(actions=["ses:SendEmail"], resources=["*"]),
            iam.PolicyStatement(
                actions=["securityhub:BatchImportFindings"], resources=["*"]
            ),
        ]
        task_definition_managed_policy = iam.ManagedPolicy(
            self,
            "IAMAssessmentManagedPolicy",
            description="IAM assessment managed policy",
            path="/",
            statements=statements,
        )
        task_definition.task_role.add_managed_policy(task_definition_managed_policy)
        results_bucket.grant_read_write(task_definition.task_role)
        # https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html
        events.Rule(
            self,
            id="IAMPermissionsGuardrailsEventsRule",
            enabled=True,
            schedule=events.Schedule.expression("rate(8 hours)"),
            targets=[
                events_targets.EcsTask(
                    cluster=cluster,
                    task_count=1,
                    task_definition=task_definition,
                    subnet_selection=ec2.SubnetSelection(subnet_type=target_subnet),
                    security_group=security_group,
                )
            ],
        )

        stack_name = "iam-permissions-guardrails-fargate-stack"
        core.CfnOutput(
            self,
            id="S3BucketResultsArn",
            value=results_bucket.bucket_arn,
            description="IAM Assessment Results S3 Bucket Arn",
            export_name=f"{stack_name}:S3BucketResultsArn",
        )
        core.CfnOutput(
            self,
            id="S3BucketResultsName",
            value=results_bucket.bucket_name,
            description="IAM Assessment Results S3 Bucket Name",
            export_name=f"{stack_name}:S3BucketResultsName",
        )
        core.CfnOutput(
            self,
            id="FargateTaskDefinitionRole",
            value=task_definition.task_role.role_arn,
            description="IAM Assessment Results Task Definition IAM Role",
            export_name=f"{stack_name}:FargateTaskDefinitionRole",
        )
