import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import argparse
import json

import parliament
from parliament import analyze_policy_string, enhance_finding
from parliament.cli import find_files

def main():
  version=parliament.__version__
  logger.info(f"parliament version {version}")

  parser = argparse.ArgumentParser()
  parser.add_argument("--directory", help="Provide a path to directory with policy files", type=str, default=".")
  args = parser.parse_args()

  logger.info(f"policy files directory {args.directory}")
  policy_files=find_files(args.directory,policy_extension="json")
  if not policy_files:
    return 0
  for policy_filename in policy_files:
    with open(policy_filename) as file_handle:
      policy_doc=file_handle.read()
      analyzed_policy = analyze_policy_string(policy_doc)
      for finding in analyzed_policy.findings:
        #enhancements are parliament doing a lookup to it's config.yaml
        #https://github.com/duo-labs/parliament/blob/800482df3b75c1dc172ccae2e669d13324bafb4d/parliament/config.yaml
        finding=enhance_finding(finding)
        logger.info("---"*30)
        logger.info(f"ISSUE {finding.issue}")
        logger.info(f"DETAIL {finding.detail}")
        logger.info(f"FILENAME {policy_filename}")
        location=json.dumps(finding.location["statement"],indent=4) if "statement" in finding.location else json.dumps(finding.location["location"],indent=4)
        logger.info(f"LOCATION \n{location}")
        logger.info(f"SEVERITY {finding.severity}")
        logger.info(f"TITLE {finding.title}")
        logger.info(f"DESCRIPTION {finding.description}")
  return 1

if __name__ == "__main__":
  code=main()
  sys.exit(code)

