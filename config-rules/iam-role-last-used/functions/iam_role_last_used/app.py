import os, sys, json, datetime, fnmatch, re, boto3, botocore, collections, smtplib, pysnow
from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType
from aws_lambda_powertools import Logger
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication 
from smtplib import SMTPException

logger = Logger(service="find-unused-iam-roles")

###custom modifications and methods###
DEFAULT_RESOURCE_TYPE = 'AWS::IAM::Role'
APPLICABLE_RESOURCES = ["AWS::IAM::Role"]
NON_COMPLIANT = 'NON_COMPLIANT'
non_compliant_app_roles_list = []
app_iam_role_dict = collections.defaultdict(list)
owner_account_id_non_compliant_role = ""

def create_new_incident(incident, short_desc, desc):
    '''creates new service now incident with given description'''
    new_record = {'short_description': short_desc, 'description': desc, 'impact': 1, 'urgency': 1} # Set the payload
    result = incident.create(payload = new_record)    # Create a new incident record
    print(result)

def check_incident_exists_then_update_else_create_new(incident, short_desc, desc):
    '''returns first non compiant iam role from service now incidents table'''
    response = incident.get(query = {'short_description': short_desc}, stream = True)
    dic = response.first_or_none() # Print out the first match, or `None`
    if dic == None:
        create_new_incident(incident, short_desc, desc)
    else:
        incidentID = (dic.get('task_effective_number'))
        update = {'description': 'Lol', 'impact': 1, 'urgency': 1}
        updated_record = incident.update(query={'number': incidentID}, payload=update)
        print(updated_record)


def service_now_incident(Msg,owner_account_id_non_compliant_role):
    serviceNowClient = pysnow.Client(instance = "dev106851", user = "admin", password = "YYOkU7Mu8rzj")  # Create client object
    incident = serviceNowClient.resource(api_path = "/table/incident") # Define a resource, here we'll use the incident table API
    short_desc = 'ALERT - Non-Compliant roles detected on account: '+ owner_account_id_non_compliant_role + "!"
    desc = Msg+' \n Service Now Incident \nBest Regards,\n AWS ProServe Security Consultant\n Srinjoy Chakravarty <srinjoy@amazon.com>'
    check_incident_exists_then_update_else_create_new(incident, short_desc, desc)

#This is the function used to build non_compliant application role list with their tags
def build_non_compliant_application_role_list(role_name, annotation=None):
    evaluation = {}
    evaluation['role_name'] = role_name
    return evaluation

#This method is used to publish to SNS topic (not SNS topic is already present with email address verified)
def sns_publish(Msg,owner_account_id_non_compliant_role):
    sns_client = boto3.client("sns")
    Topics = sns_client.list_topics()
    Topics = Topics.get("Topics")
    topicName = "test-python-sns"
    message_text = Msg+' \n Message Sent from SNS Topic \nBest Regards,\n AWS ProServe Security Consultant\n Srinjoy Chakravarty <srinjoy@amazon.com>'
    for topic in Topics:
        if topicName in topic.get("TopicArn"):
            topic_arn = topic.get("TopicArn")
            sns_client.publish(
                TopicArn=topic_arn, 
                Message=message_text,
                Subject='ALERT - Non-Compliant roles detected on account: '+ owner_account_id_non_compliant_role + "!"
            )
            print("SNS message published successfully")


#This method can be used to send emails using SMTP
def send_email_smtp(app_owner_email,Msg,owner_account_id_non_compliant_role):
    try:
        # if("@domain.com" not in app_owner_email):
        #     app_owner_email = "srinjoy@amazon.com" #Update with default user id
        
        message_text = Msg+' \n\nBest Regards,\n AWS ProServe Security Consultant\n Srinjoy Chakravarty <srinjoy@amazon.com>'

        fromAddr='srinjoy@amazon.com' 
        cc= ['srinjoy@amazon.com']

        message_subject = 'ALERT - Non-Compliant roles detected on account: '+ owner_account_id_non_compliant_role + "!"
        message = "From: %s\r\n" % fromAddr + "To: %s\r\n" % app_owner_email + "CC: %s\r\n" % ",".join(cc) + "Subject: %s\r\n" % message_subject + "\r\n" + message_text
        toAddr = [app_owner_email] + cc
        #Create SMTP session for sending the mail
        sender_address = 'srinjoychakravarty@gmail.com'
        sender_pass = 'twbvaxctpybucraq'

        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        session.sendmail(fromAddr, toAddr, message) 
        session.quit()

        
        ###Uncomment below and comment above session code for using mailserver###

        ##Configure SMTP server for sending the mail
        #smtpServer='companyservermail'      
        #server = smtplib.SMTP(smtpServer,25)
        #server.sendmail(fromAddr, toAddr, message) 
        #server.quit()
        ###Uncomment till here###
        print("mail sent successfull")

    except SMTPException:
        print("Error: unable to send email")

#This method can be used to send emails about non-compliant roles using SES [not yet configured with SES currently SMTP is used.]
def send_email_ses(app_owner_email,Msg,owner_account_id_non_compliant_role):
    ses_client = boto3.client('ses')
    subjectData = 'ALERT - Non-Compliant roles detected on account: '+ owner_account_id_non_compliant_role + "!"
    #Update the Source email below
    ses_client.send_email(
        Source='srinjoy@amazon.com',
        Destination={
            'ToAddresses': [
                app_owner_email,
            ]
        },
        Message={
            'Subject': {
                'Data': subjectData,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': Msg,
                    'Charset': 'UTF-8'
                }
            }
        },
    )

# This is the function is used to create a address-book that is used to send emails containing all non-compliant roles (read comments below!!! -- to update required information)
def create_consolidated_notifications(non_compliant_roles_list,owner_account_id_non_compliant_role):
    app_owner_email="srinjoy@amazon.com"
    #removing spaces and extra bractes from the list
    acceptable = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,: ')
    non_compliant_roles_list_msg=''.join(filter(acceptable.__contains__, str(non_compliant_roles_list)))
    Msg ="Please find below list of non-compliant roles- \nNon Compliant Roles: " + non_compliant_roles_list_msg + "."
    sns_publish(Msg,owner_account_id_non_compliant_role)
    service_now_incident(Msg,owner_account_id_non_compliant_role)
    
###custom functions end###

# If the rolename is in the authorized list, then it is authorized
def is_authorized_role(role_arn, authorized_roles_list):
    if role_arn in authorized_roles_list:
        return True
    return False


# Determine if any roles were used to make an AWS request
def determine_last_used(
    role_id, role_name, last_used_date, last_used_region, max_age_in_days
):
    # Condition 1: If Role is NEVER USED it is NON-COMPLIANT
    if not last_used_date:
        compliance_result = NON_COMPLIANT
        reason = "No record of usage"
        logger.info(f"NON_COMPLIANT: {role_name} has never been used")
        # # removes aws managed service roles i.e., aws managed
        # if "AWSServiceRoleFor" not in role_name:
        non_compliant_app_roles_list.append(build_non_compliant_application_role_list(role_name, annotation=reason))
        return Evaluation(
            ComplianceType.NON_COMPLIANT,
            role_id,
            APPLICABLE_RESOURCES[0],
            annotation=reason,
        )
    #Condition 2: If Role has not been used for GREATER than MAX_AGE_IN_DAYS it is NON-COMPLIANT
    days_unused = (datetime.datetime.now() - last_used_date.replace(tzinfo=None)).days
    if days_unused > max_age_in_days:
        compliance_result = NON_COMPLIANT
        reason = f"Was used {days_unused} days ago in {last_used_region} and not within {max_age_in_days}"
        logger.info(
            f"NON_COMPLIANT: {role_name} has not been used for {days_unused} days and not within {max_age_in_days}, last use in {last_used_region}"
        )
        # # removes aws managed service roles i.e., aws managed
        # if "AWSServiceRoleFor" not in role_name:
        non_compliant_app_roles_list.append(build_non_compliant_application_role_list(role_name, annotation=reason))
        return Evaluation(
            ComplianceType.NON_COMPLIANT,
            role_name,
            APPLICABLE_RESOURCES[0],
            annotation=reason,
        )

    reason = f"Was used {days_unused} days ago in {last_used_region} within {max_age_in_days}"
    logger.info(
        f"COMPLIANT: {role_name} used {days_unused} days ago in {last_used_region} within {max_age_in_days}"
    )
    return Evaluation(
        ComplianceType.COMPLIANT, role_id, APPLICABLE_RESOURCES[0], annotation=reason
    )


# Returns a list of dicts, each of which has authorization details of each role.  More info here:
#   https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.get_account_authorization_details
def get_role_authorization_details(iam_client):
    roles_authorization_details = []

    paginator = iam_client.get_paginator("get_account_authorization_details")
    for page in paginator.paginate(Filter=["Role"]):
        for role in page["RoleDetailList"]:
            # roles_authorization_details.append(role)
            yield role
    # return roles_authorization_details

#modified ids to names for config results.
class FindUnusedIamRoles(ConfigRule):
    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        #Custom modifications for getting accountID
        accID = event.get('invokingEvent').split(":")[1]
        #regex for filtering account id
        acceptableAccNumber = set('0123456789')
        owner_account_id_non_compliant_role = ''.join(filter(acceptableAccNumber.__contains__, str(accID)))
        # List of resource evaluations to return back to AWS Config
        evaluations = []
        iam_client = client_factory.build_client("iam")

        # Maximum allowed days that a role can be unused, or has been last used for an AWS request
        max_days_for_last_used = int(os.environ.get("max_days_for_last_used", "60"))
        if "max_days_for_last_used" in valid_rule_parameters:
            max_days_for_last_used = int(
                valid_rule_parameters["max_days_for_last_used"]
            )

        authorized_roles_list = []
        if "role_authorized_list" in valid_rule_parameters:
            authorized_roles_list = valid_rule_parameters["role_authorized_list"]

        # List of dicts of each role's authorization details as returned by boto3
        all_roles = get_role_authorization_details(iam_client)

        # Iterate over all our roles.  If the creation date of a role is <= max_days_for_last_used, it is compliant
        for role in all_roles:
            role_id = role["RoleId"]
            role_name = role["RoleName"]
            role_path = role["Path"]
            role_creation_date = role["CreateDate"]
            role_last_used = role["RoleLastUsed"]
            role_age_in_days = (
                datetime.datetime.now() - role_creation_date.replace(tzinfo=None)
            ).days

            # If the role is in the authorized list, it is COMPLIANT straighaway!
            if is_authorized_role(f"{role_path}/{role_name}", authorized_roles_list):
                reason = "Role is in authorized list"
                evaluations.append(
                    Evaluation(
                        ComplianceType.COMPLIANT,
                        role_name,
                        APPLICABLE_RESOURCES[0],
                        annotation=reason,
                    )
                )
                logger.info(f"COMPLIANT: {role} is in authorized list")
                continue
            
            # If the role is NEW with a AGE smaller than MAX_DAYS_FOR_LAST_USED, it is COMPLIANT!
            if role_age_in_days <= max_days_for_last_used:
                reason = f"Role age is {role_age_in_days} days"
                evaluations.append(
                    Evaluation(
                        ComplianceType.COMPLIANT,
                        role_name,
                        APPLICABLE_RESOURCES[0],
                        annotation=reason,
                    )
                )
                logger.info(
                    f"COMPLIANT: {role_name} - {role_age_in_days} is newer or equal to {max_days_for_last_used} days"
                )
                continue

            role_last_used_date = role_last_used.get("LastUsedDate", None)
            role_last_used_region = role_last_used.get("Region", None)
            
            # If the role is OLD we check when it was LAST USED and if greater than MAX_DAYS_FOR_LAST_USED, it is NON-COMPLIANT!
            evaluation_result = determine_last_used(
                role_id,
                role_name,
                role_last_used_date,
                role_last_used_region,
                max_days_for_last_used,
            )
            evaluations.append(evaluation_result)
        create_consolidated_notifications(non_compliant_app_roles_list,owner_account_id_non_compliant_role)
        return evaluations


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    my_rule = FindUnusedIamRoles()
    evaluator = Evaluator(my_rule, APPLICABLE_RESOURCES)
    return evaluator.handle(event, context)
