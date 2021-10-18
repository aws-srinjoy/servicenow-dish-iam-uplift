# Copyright 2017-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License"). You may
# not use this file except in compliance with the License. A copy of the License is located at
#
#        http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
import logging
import sys

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from time import sleep

import json
import urllib.parse

import boto3, botocore

DEFAULT_THROTTLE_PERIOD = 0.1
CONFIG_PAGE_SIZE = 100

def get_resource_keys(config_client, resource_type):
    paginator=config_client.get_paginator('list_discovered_resources')
    parameters={
      'resourceType':resource_type,
      'limit':CONFIG_PAGE_SIZE,
    }
    for page in paginator.paginate(**parameters):
      resource_keys=[]
      for role_resource in page["resourceIdentifiers"]:
        resource_keys.append(
          {
            "resourceType": resource_type,
            "resourceId": role_resource["resourceId"]
          }
        )
      yield resource_keys

def get_configuration_items(config_client, resource_keys):
  unprocessed_resource_keys=[]
  while resource_keys or unprocessed_resource_keys:
    keys_to_fetch=unprocessed_resource_keys if unprocessed_resource_keys else next(resource_keys,None)
    #not a way to test if the generator is exhaused and we have to iterate over unprocessed so for loop wasn't possible
    if not keys_to_fetch:
      break
    response=config_client.batch_get_resource_config(resourceKeys=keys_to_fetch)
    configuration_items=response["baseConfigurationItems"]
    unprocessed_resource_keys = response.get("unprocessedResourceKeys", [])
    for configuration_item in configuration_items:
      configuration = json.loads(configuration_item["configuration"])
      yield configuration
    sleep(DEFAULT_THROTTLE_PERIOD)            


