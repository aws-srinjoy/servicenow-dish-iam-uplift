import json
import logging
import sys
import argparse
import re
from policyuniverse.policy import Policy
from policyuniverse.arn import ARN



###################SETTINGS#############################

# When marked as False - will mark any "*" Principal as Non-Compliant
# Warning! Setting this to true will allow the "*" to appear as non-compliant
# This means any IAM Principal in any account can assume the role!!!!!

WildCardAllowed = False

# When Marked as True - will check for the Environment level that is associated
# with the account number in the allowed accounts variable. In order to marked compliant,
# The Role of the Target account must be in the Same environment as the account specified in
# the Trust Policy - Eg Dev to Dev, Prod to Prod would be compliant but Lab to Prod would be
# Non-Compliant

CrossEnvironmentCheckEnabled = True

# AWS Accounts listed in the hashmap below will be marked compliant.
# Format is "AccountNum":"EnvironmentLvl"


AllowedAccounts = {
    "111111111111":"Test",
    "222222222222":"Test",
    "333333333333":"Prod",
    "444444444444":"Prod"
}
  
# Logic :
# AWS Services listed below will be marked compliant, anything else will
# return non-compliant

AllowedServices = [
    "lambda.amazonaws.com",
    "ec2.amazonaws.com",
    "config.amazonaws.com",
    "ssm.amazonaws.com",
    "logs.us-east-1.amazonaws.com",
    "logs.us-east-2.amazonaws.com",
    "logs.amazonaws.com"
    
    ]
    
# Logic :
# Federation Sources listed below will be marked compliant, anything else will
# return non-compliant
# eg - "arn:aws:iam::112233445566:saml-provider/provider-name"

AllowedSAMLFederation = [
    
    ]


# Web Federation Sources Listed below will be marked as compliant
# if not using web federation - leave blank!!!

AllowedWebFederation = [
    ]






# class TrustPolicy(RawPayload):
    
#     def init(self):
#         TrustPolicyJsonPayload = json.loads(self.RawPayload)
#         TrimmedTrustPolicy = TrustPolicyJsonPayload[u'Statement']
#         self.

# class TerraformPlan(JSONPlan):
#   def init(self)


##def GenerateTerraformPlan():
    ###Terraform plan --out-file planfile

# def GetArguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--TerraformPlanJson", help="Enter the json Terraform Plan File. Can be generated by: \n terraform plan -out terraformplan \n terraform show -json terraformplan > terraformplan.json")
#     args = parser.parse_args()
#     return args

'''
 _____              _       
|_   _|            | |      
  | |_ __ _   _ ___| |_     
  | | '__| | | / __| __|    
  | | |  | |_| \__ \ |_     
  \_/_|   \__,_|___/\__|    
                            
                            
______     _ _              
| ___ \   | (_)             
| |_/ /__ | |_  ___ _   _   
|  __/ _ \| | |/ __| | | |  
| | | (_) | | | (__| |_| |  
\_|  \___/|_|_|\___|\__, |  
                     __/ |  
                    |___/   
 _     _       _            
| |   (_)     | |           
| |    _ _ __ | |_ ___ _ __ 
| |   | | '_ \| __/ _ \ '__|
| |___| | | | | ||  __/ |   
\_____/_|_| |_|\__\___|_|   
'''


class TerraformPlan():
    
    def __init__(self, JsonPayload):
        
        # relying on the schema posted at:
        # https://www.terraform.io/docs/internals/json-format.html
        # be warned this is subject to change
        
        # We parse Create and Update Actions only - as we want to see the
        # configurations that are going to be created in the account....
        # this could be adjusted to target actions such as "no-op", 
        # "read", "delete" as well
        
        self.TerraformUpdateActions = ["create","update"]
        self.resources = []
        
        # we will parse the json terraform plan to grab all resources that have
        # a Change Representation action listed in the TerraformUpdateActions
        
        # Checking for the existence of the 'terraform_version' key - if it doesnt exist
        # likely that the provided JSON isnt actually a valid terraform plan
        
        
        if 'terraform_version' not in JsonPayload:
            print('terraform_version key missing - is this a valid Terraform plan?')
            raise ValueError('TerraformPlanNotValid', JsonPayload)
        
        
        # We need to check for the existence of the "resource_changes" key in the JSON payload
        # If it doesnt exist - this either indicates it isnt a proper terraform plan, or is a terraform plan
        # that doesnt have any changes - which we dont need to parse - we will just leave
        # self.resources empty
        
        if 'resource_changes' not in JsonPayload:
            print('Terraform plan has no changes')
            return
            
        
        for Resource in JsonPayload['resource_changes']:
            
            # Checking if any of the resources Change Actions exist in the 
            # TerraformUpdateActions variable above
            
            if len(set(self.TerraformUpdateActions).intersection(Resource['change']['actions'])) > 0:
                self.resources.append(Resource)
            
    # a Function to get return all resources of a particular type in an array
    # will return a json payload with all the configuration data of the resource
    
    def GetResources(self, ResourceType):
        result = []
        for Resource in self.resources:
            if Resource['type'] == ResourceType:
                result.append(Resource)
        return result

def GetAccountEnv(AccountNumber):
    
    # Gets the Associated Environment with the Account Number
    # If not found - returns None
    if AccountNumber in AllowedAccounts:
        Environment = AllowedAccounts[AccountNumber]
        return Environment
    else:
        print('Account ' + AccountNumber + ' Doesnt Exist in in AllowedAccounts')
        return None
        
def CrossEnvironmentCompliant(TargetAccountId, TrustPolicyPrincipalAccountId):
    
    # Takes in the TargetAccountId (The Account we are deploying the Role to) and
    # TrustPolicyPrincipalAccountId (basically - the account ID we are allowing the role
    # to be assumed by) and uses GetAccountEnv to get the Environment of both accounts
    # Returns True if Environments match, false if they are different
    
    # Checking to be sure the value is a valid accountID - accidentally passed the ARN during Dev
    # was difficult to troubleshoot
    

    AccNumberPattern = '^[0-9]{12}$'
    
    if not re.match(AccNumberPattern, TargetAccountId) or not re.match(AccNumberPattern, TrustPolicyPrincipalAccountId):
        print('CrossEnvironmentCompliant requires Account ID')
        raise ValueError('Parameter must be an AccountId')
        
    
    DeployAccountEnv = GetAccountEnv(TargetAccountId)
    AssumingAccountEnv = GetAccountEnv(TrustPolicyPrincipalAccountId)
    
    # this shouldnt happen - but just in case
    if DeployAccountEnv == None:
        return False
    
    #this shouldnt happen - but just in case
    if AssumingAccountEnv == None:
        return False
    
    if DeployAccountEnv == AssumingAccountEnv:
        print(DeployAccountEnv + ' to ' + AssumingAccountEnv + ' Allowed' )
        return True
    
    else:
        print(DeployAccountEnv + ' to ' + AssumingAccountEnv + ' Not Allowed' )
        return False
        
    
def IdentifyPrincipalType(Principal):
    
    # Input - String - specifically a principal parsed out using the
    # policyuniverse Policy.principals method
    #
    # As policyuniverse only parses out the Principal - we need to classify
    # so we can appropriately compare it against the whitelists
    # based off of:
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html
    # Can identify the following principal types:
    # Account Number
    # AWS Service
    # AWS ARN (specifically the root account notation and IAM Principal)
    # SAML Provider ARN
    # Non-AWS Federation - (May need tweaking if this in use)
    # Wildcard Principal
    # if a Principal cannot be identified - returns "Unknown"
    
    AccNumberPattern = '^[0-9]{12}$'
    AwsServicePattern = '^.*\.amazonaws\.com$'
    AwsArnPattern = 'arn:aws:iam::[0-9]{12}.*'
    AwsSamlFederatedArnPattern = 'arn:aws:iam::[0-9]{12}:saml-provider/.*'
    NonAWSFederation = '.*\..*\.com'
    WildcardPrincipal = '^\*$'
    
    PrincipalType = None
    
    if re.match(AccNumberPattern, Principal):
        
        PrincipalType = "AccountNumber"
        return PrincipalType
        
    elif re.match(AwsServicePattern, Principal):
    
        PrincipalType = "AWSService"
        return PrincipalType
        
    elif re.match(AwsArnPattern, Principal):
        
        if re.match(AwsSamlFederatedArnPattern, Principal):
            PrincipalType = "SamlFederation"
            return PrincipalType
        else:
            PrincipalType = "AWSArn"
            return PrincipalType
            
    elif re.match(NonAWSFederation, Principal):
        
        PrincipalType = "WebIdentityFederation"
        return PrincipalType
        
    elif re.match(WildcardPrincipal, Principal):
        
        PrincipalType = "Wildcard"
        return PrincipalType
    
    else:
        print('Unable to match principal type for Principal: ' + Principal)
        PrincipalType = "Unknown"
        return PrincipalType



class TerraformTrustPolicyCompliance():
    
    def __init__(self):
        self.Compliance = True
        self.ComplianceData = []
        self.TargetAccountId = None



    def EvalPrincipals(self, RoleName, Principals):
        # Expected Input - array of strings, specifically principals parsed out of
        # a trust policy, Example:
        # [u'arn:aws:iam::123456789101:role/DakotaRole', u'123456789101']
        #
        # Will update the self.ComplianceData attribute of the 
        # TerraformTrustPolicyCompliance Class with a key value pair of the following format:
        # {
        #    "RoleName": MyNonCompliantRole,
        #    "Principals": [
        #                       {"Principal":"123459601021",
        #                        "Compliance":"True",
        #                        "CrossEnvironment" : "False"},
        #                       {"Principal":"ssm.amazonaws.com"
        #                        "Compliance":"False",
        #                         "CrossEnvironment": None}
        #
        #                                 
        # ]
        # }
        result = {}
        result['RoleName'] = RoleName
        result["Principals"] = []
        
        for Principal in Principals:
            
            PrincipalType = IdentifyPrincipalType(Principal)
            
            if PrincipalType == 'AccountNumber':
                if Principal in AllowedAccounts:
                    CrossEnvResult = CrossEnvironmentCompliant(self.TargetAccountId, Principal)
                    if CrossEnvResult == True:
                        PrincipalEval = {"Principal": Principal, "Compliance": True, "CrossEnvironment": False}
                        result['Principals'].append(PrincipalEval)
                    else:
                        PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": True}
                        result['Principals'].append(PrincipalEval)
                        self.Compliance = False
                else:
                    PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                    self.Compliance = False
                    
            elif PrincipalType == 'AWSService':
                if Principal in AllowedServices:
                    PrincipalEval = {"Principal": Principal, "Compliance": True, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                else:
                    PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                    self.Compliance = False
                    
            elif PrincipalType == 'AWSArn':
                principalARN = ARN(Principal)
                principalAcctNumber = principalARN.account_number
                if principalAcctNumber in AllowedAccounts:
                    CrossEnvResult = CrossEnvironmentCompliant(self.TargetAccountId, principalAcctNumber)
                    if CrossEnvResult == True:
                        PrincipalEval = {"Principal": Principal, "Compliance": True, "CrossEnvironment": False}
                        result['Principals'].append(PrincipalEval)
                    else:
                        PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": True}
                        result['Principals'].append(PrincipalEval)
                        self.Compliance = False
                else:
                    PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                    self.Compliance = False
                    
            elif PrincipalType == 'SamlFederation':
                if Principal in AllowedSAMLFederation:
                    PrincipalEval = {"Principal": Principal, "Compliance": True, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                else:
                    PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                    self.Compliance = False
                    
            elif PrincipalType == 'WebIdentityFederation':
                if Principal in AllowedWebFederation:
                    PrincipalEval = {"Principal": Principal, "Compliance": True, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                else:
                    PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                    result['Principals'].append(PrincipalEval)
                    self.Compliance = False
                    
            elif PrincipalType == 'Wildcard':
                PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                result['Principals'].append(PrincipalEval)
                self.Compliance = False
                
            else:
                print('Unidentified Principal Type - setting non-compliant')
                PrincipalEval = {"Principal": Principal, "Compliance": False, "CrossEnvironment": None}
                result['Principals'].append(PrincipalEval)
                self.Compliance = False
        
        self.ComplianceData.append(result)

    
    def GenerateReport(self):
        
        if len(self.ComplianceData) == 0:
            print('No Roles Evaluated')
            return None
        
        print('\t \t RESULTS: \n \n')
    
   
        for Role in self.ComplianceData:
            print('-----------------------------------------------')
            print(Role['RoleName'])
            print('-----------------------------------------------')
            print('\n Compliant Principals: \n')
            for Principal in Role['Principals']:
                if Principal['Compliance'] == True:
                    print('\t' + Principal['Principal'])
            print('\n Non-Compliant Principals: \n')
            for Principal in Role['Principals']:
                if Principal['Compliance'] == False:
                    print('\t' + Principal['Principal'])
            
        if self.Compliance == True:
            print('Terraform plan is COMPLIANT!')
            
        if self.Compliance == False:
            print('Terraform plan is NON-COMPLIANT!')
            
            
        

print('\n  RESULTS: \n \n \n')

# Logic :
# Trusts between accounts that exist in the same environment level eg - lab to lab,
# prod to prod, however something like Lab to Prod will be marked as non-compliant


# Expected Payload:
# {
#   'TargetAccountId': '111122223333', 
#   'TerraformPlan':
#       {format_version":"0.1","terraform_version":"0.12.6",.......}
#    }

def BuildResponseObject(ComplianceResult, ComplianceReport, Comment):
        if ComplianceResult not in ['Compliant', 'Non-Compliant', 'Error']:
            raise Exception('Incorrect string for ComplianceResult')
        Payload = {}
        Payload['Result'] = ComplianceResult
        Payload['ComplianceReport'] = ComplianceReport
        Payload['Comment'] = Comment
        return Payload
        

def lambda_handler(event, context):
    logger = logging.getLogger('TerraformTrustPolicyParser')
    
    if 'TargetAccountId' not in event or 'TerraformPlan' not in event:
        result = BuildResponseObject('Error', None, 'Invalid Payload - must have TargetAccountId and TerraformPlan keys')
        return result
        
    
    TargetAccountID = event['TargetAccountId']
    TerraformPlanJson = event['TerraformPlan']
    
    #args = GetArguments()
    
    #TerraformPlanJsonFile = args.TerraformPlanJson
    
    #TerraformPlanJson = open(TerraformPlanJsonFile)
    
    try:
        TerraformPlanObject = TerraformPlan(TerraformPlanJson)
    except ValueError as e:
        result = BuildResponseObject('Error', None, 'Invalid Terraform Plan')
        return result
            
        
        
    # TerraformUpdateActions = ["create","update"]
    
    #Grabbing all U'aws_iam_role type resources from the plan - adding them to IamRoleArray
    
    # for Resource in TerraformPlanJsonload['resource_changes']:
    #     if Resource['type'] == u'aws_iam_role':
    #         logger.debug('Resource ' + Resource['name'] + ' is of type aws_iam_role')
    #         if len(set(TerraformUpdateActions).intersection(Resource['change']['actions'])) > 0:
    #             logger.debug('Resource Change ' + Resource['name'] + ' is of type create or update - proceeding')
    #             IamRoleArray.append(Resource)
    #     else:
    #         logger.info('Resource ' + Resource['name'] + ' not of type aws_iam_role, skipping')
    
    IamRoleArray = TerraformPlanObject.GetResources(u'aws_iam_role')
    if len(IamRoleArray) == 0:
        print('No IAM roles created or updated in terraform plan - exiting')
        result = BuildResponseObject('Compliant', None, 'No Roles in Terraform Plan')
        return result
        
    
    TrustPolicyTest = TerraformTrustPolicyCompliance()
    TrustPolicyTest.TargetAccountId = TargetAccountID
    print(TrustPolicyTest.TargetAccountId)
    
            
    for Role in IamRoleArray:
        #TrustPolicy Evaluation Logic Here
        TrustPolicy = Role[u'change']['after']['assume_role_policy']
        TrustPolicy = json.loads(TrustPolicy)
        TrustPolicy = Policy(TrustPolicy)
        
        # testing that the principal type matches one of the allowed types based
        # on the syntax at https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html
        
        for Statement in TrustPolicy.policy['Statement']:
            # ValidPrincipalKeys = ['AWS', 'Service', 'Federated']
            # Policy Universe wont register the principal as valid if it doesnt match one of the valid principal keys
            # The check below is for user experience - the trust policy wouldnt deploy - but 
            
            
            Counter = 0
            if 'Principal' not in Statement:
                break
            if 'AWS' not in Statement['Principal']:
                Counter = Counter + 1
                
            if 'Service' not in Statement['Principal']:
                Counter = Counter + 1
                
            if 'Federated' not in Statement['Principal']:
                Counter = Counter + 1
            
            if Counter == 3:
                result = BuildResponseObject('Error', None, 'Malformed Policy Document - Principal Field must have AWS, Service, or Federated key to be a valid trust policy')
                return result
            
                    
        RoleName = Role[u'change']['after']['name']
        Principals = TrustPolicy.principals
        TrustPolicyTest.EvalPrincipals(RoleName, Principals)
    if TrustPolicyTest.Compliance == True:
        result = BuildResponseObject('Compliant', TrustPolicyTest.ComplianceData, None)
        return result
    elif TrustPolicyTest.Compliance == False:
        result = BuildResponseObject('Non-Compliant', TrustPolicyTest.ComplianceData, None)
        return result
    
        
    #TrustPolicyTest.GenerateReport()
    # if len(Principals) == 0:
    #     logger.error("Role " + Role[u'change']['after']['name'] + " has an unparseable trust policy - or has no principals specified: non-compliant")
    #     continue
        
    # if Principals.issubset(set(AllowedPrincipals)) == True:
    #     logger.info("Role " + Role[u'change']['after']['name'] + " is a compliant trust policy. Allowed Princiapls:\n" + str(Principals) + "\n")
    # else:
    #     logger.warning("Role " + Role[u'change']['after']["name"] + " is a non-compliant trust policy. Princiapls:\n" + str(Principals) + "\n TRIGGER APPROVAL REQUEST FROM INFOSEC IN PIPELINE" + "\n")
    #     logger.debug(TrustPolicy)
    
    

    


