import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import boto3, botocore

IS_TRACKING_API_CALLS=False

iam_apis_used=set()

def track_api_methods(params, **kwargs):
  #logger.info(f"params {params}")
  #logger.info(f"kwargs {kwargs}")
  api=kwargs['model'].name
  event_name=kwargs['event_name']
  index=event_name.index(".")
  event_name=event_name[index+1:]
  iam_apis_used.add(event_name)
  #logger.info(f"api {api} event_name {event_name}")

def get_client(client_name,region='us-east-1',max_connections=100,max_attempts=25):
  #MAX_CONNECTIONS=100
  #MAX_ATTEMPTS=25
  config=botocore.client.Config(max_pool_connections=max_connections,retries=dict(max_attempts=max_attempts))
  client=boto3.client(client_name,region,config=config)
  if IS_TRACKING_API_CALLS:
    event_system=client.meta.events
    event_system.register('provide-client-params.*.*',track_api_methods)
  return client

def print_iam_apis_used():
  if IS_TRACKING_API_CALLS:
    logger.info(f"IAM APIs used {iam_apis_used}")
