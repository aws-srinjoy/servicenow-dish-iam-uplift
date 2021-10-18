import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import argparse

from pathlib import Path

import json

def main(policy_to_parse,output_directory):
  Path(output_directory).mkdir(parents=True, exist_ok=True)
  roles=policy_to_parse["Roles"]
  for role in roles:
    role_name=role["RoleName"]
    policies=role["Policies"]
    for policy in policies:
      resource_id=policy["Name"]
      policy_json=policy["Policy"]
      filename=f"{output_directory}/{role_name}-{resource_id}.json"
      with open(filename,"w") as json_file:
        json_file.write(json.dumps(policy_json,indent=4))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--filename", help="Provide a filename of the parsed JSON file to analyze", type=str, default="input.json")
  parser.add_argument("--output_dir", help="Provide the output directory of the IAM Policy files", type=str, default="policies-to-analyze")
  args = parser.parse_args()

  filename=args.filename
  output_directory=args.output_dir
  logger.info(f"Filename {filename} Output Directory {output_directory}")

  policy_to_parse={}
  with open(filename) as json_file:
    policy_to_parse=json.load(json_file)
  logger.info(f"policy_to_parse {json.dumps(policy_to_parse,indent=4)}")

  main(policy_to_parse,output_directory)
