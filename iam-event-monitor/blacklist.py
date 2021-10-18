import boto3,os
from datetime import datetime

IAM_CLIENT=boto3.client('iam')
SNS_CLIENT= boto3.client('sns')

def main(event,context):
    try: 
        #get data out of the JSON event to make part of the notification
        #Depending on the type of IAM call these fields would vary. The function
        # has been tested on a subset of those IAM calls. Calls such as ListRoles don't have 
        # requestParameters element so it will give an error with the current code.
        role_arn = event['detail']['userIdentity']['arn']
        source_ip = event['detail']['sourceIPAddress']
        account_number = event['account']
        region = event['region']
        iam_action = event['detail']['eventName']
        

        if not event['detail']['requestParameters']:
            message = 'The IAM principal '+role_arn+' has tried to perform '+iam_action+' in account: '+account_number+' from sourceip '+source_ip
        else :
            affected_role = event['detail']['requestParameters']['roleName']
            message = 'The IAM principal '+role_arn+' has tried to perform '+iam_action+' on the IAM role '+affected_role+' in account: '+account_number+' from sourceip '+source_ip
        # Any principal doing UpdateAssumeRolePolicy change will be flagged by this code. 
        
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        timestamp = timestamp+'Z'


        #We can revoke the policy for the entire role but be aware the revocation will disable the entire role, which could be assumed by 100 devs. For example, the dev-role will be marked unusable for one person's violation.

        SNS_CLIENT.publish(
            TopicArn=os.environ['sns_topic'],
            Message=message
        )
    except NameError as e:
        print(" Cannot find the following variable [NameError]", e)
        print ("{0}".format(e))
    except:
        raise