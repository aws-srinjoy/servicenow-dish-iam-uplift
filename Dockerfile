FROM amazonlinux:latest

RUN yum -y update
RUN yum -y install python3 python3-pip

ADD assessment/iam_client.py /app/iam_client.py
ADD assessment/security_hub_findings.py /app/security_hub_findings.py
ADD assessment/iamdeco.py /app/iamdeco.py
ADD assessment/services-last-used.py /app/services-last-used.py
ADD assessment/iam-roles-metrics.py /app/iam-roles-metrics.py
ADD assessment/check-guardrails.py /app/check-guardrails.py
ADD assessment/policy-validator.py /app/policy-validator.py
ADD assessment/submit-report.py /app/submit-report.py
ADD assessment/iam-roles-metrics.sh /app/iam-roles-metrics.sh
ADD assessment/requirements.txt /app/requirements.txt
ADD guardrails /guardrails

WORKDIR /app

RUN pip3 install -r requirements.txt
 
CMD ls -al /app && ./iam-roles-metrics.sh
