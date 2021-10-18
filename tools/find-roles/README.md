#Purpose
We are formulating the [IAM Permissions Monitoring builder project](https://w.amazon.com/bin/view/AWS/Teams/Proserve/SRC/Identity_and_Access_Management/Offerings/IAM_Audit/). As a way to quickly provide customer value and to work backwards from defining customer use cases, we have developed this tool to quickly locate IAM Roles that contain destructive permissions. 

This tool can be run against a single AWS Account.

By using this tool, you agree to provide feedback on customer IAM use cases. For example, related to use cases related to montoring IAM permissions or verifying IAM policies.

#Install dependencies
pipenv install -r requirements.txt 

#virtualenv
pipenv shell

#set the AWS profile name based on credential file
export AWS_DEFAULT_PROFILE=

#Execute
python3 findroles.py 

#Notes
The methods are defined in findroles.py

###find_create_roles()
This finds all the constructive roles using the prefixes in constructive.txt

###find_destructive_roles()
This finds all the destructive roles using the prefixes in destructive.txt

###find_sensitive_permissions_roles()
This finds all the sensitive permissions defined in sensitive-permissions-list.txt. Update to your use cases as needed

#Questions
Feel free to email us at team-permission-invariants@amazon.com or open a [SIM](https://sim.amazon.com/issues/create?template=9315ee1f-0bcd-4392-ab25-931060d58b13).
