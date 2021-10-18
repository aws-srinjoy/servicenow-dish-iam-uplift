from enum import Enum

from parliament.statement import get_arn_format, get_privilege_info
from parliament import is_arn_match

class Principle(Enum):
  user=("user","CreateUser")
  role=("role","CreateRole")
  group=("group","CreateGroup")
  saml_provider=("saml-provider","CreateSAMLProvider")


def check_iam_type(principal_enum,arn_to_check):
  resource_type=principal_enum.value[0]
  iam_action=principal_enum.value[1]
  privilege_info=get_privilege_info("iam",iam_action)
  arn_format=get_arn_format(resource_type,privilege_info["service_resources"])
  if is_arn_match(resource_type,arn_format,arn_to_check):
    return principal_enum
  return None

def identify_principle_type(arn_to_check):
  if check_iam_type(Principle.user,arn_to_check):
    return Principle.user

  if check_iam_type(Principle.group,arn_to_check):
    return Principle.group

  if check_iam_type(Principle.role,arn_to_check):
    return Principle.role

  if check_iam_type(Principle.saml_provider,arn_to_check):
    return Principle.saml_provider

  return None
  
if __name__ == "__main__":
  user_arn="arn:aws:iam::123456789123:user/test"
  principle_type=identify_principle_type(user_arn)
  print(principle_type)

  group_arn="arn:aws:iam::123456789123:group/test"
  principle_type=identify_principle_type(group_arn)
  print(principle_type)

  role_arn="arn:aws:iam::123456789123:role/AWSCloudFormationStackSetExecutionRole"
  principle_type=identify_principle_type(role_arn)
  print(principle_type)

  saml_provider_arn="arn:aws:iam::123456789123:saml-provider/AWSCloudFormationStackSetExecutionRole"
  principle_type=identify_principle_type(saml_provider_arn)
  print(principle_type)
