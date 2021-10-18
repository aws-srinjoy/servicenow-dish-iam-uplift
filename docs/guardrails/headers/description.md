## Description

The IAM Permissions Guardrails help customers securely provision and monitor IAM permissions across a customer's utilization of AWS Services. Our goal is to help customers look around corners and understand the rationale and remediation for locking down specific IAM Permissions.

Also, our goal is to help customers define a measurable approach to assess their AWS IAM posture. We are looking to compile the deep fine-grained IAM knowledge of AWS experts and consultants in a scalable automated mechanism. The IAM Permissions Guardrails will be delivered via AWS Config Rules, [cfn-guard](https://w.amazon.com/bin/view/CloudFormation_Badger/), and AWS Security Hub.

Our focus is analyzing at the policy level rather than the effective permissions within an account. We want to encourage application teams to create secure policies starting in lower environments. Also, we want to reduce the blast radius due to accidental oversight and improve defense in depth, rather than relying on a single service control policy.

We would like to provide customers immediate feedback and value. Taking a rule from initial creation to an AWS Managed Rule could take anywhere from 3-9 months. In the meantime, we can deliver these custom Config rules directly to the customer, receiving feedback and providing value.

These IAM Permissions Guardrails will be integrated into the [Security Epics](https://w.amazon.com/index.php/AWS/Teams/Proserve/SRC/OfferingsMechanisms/SecurityEpics/UserStories). Though we are looking for feedback on refining the use cases and delivery mechanism to the customer.
