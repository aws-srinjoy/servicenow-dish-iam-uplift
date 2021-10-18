cdk deploy network-admin-role-example-administrator --parameters TrustedCidrRanges="192.0.2.0/24","203.0.113.0/24" --parameters IdentityProviderName=IdentityProviderNameHERE

cdk deploy network-admin-role-example-readonly --parameters IdentityProviderName=IdentityProviderNameHERE

cdk synth network-admin-role-example-administrator > network_administrator_role.yaml

cdk synth network-admin-role-example-readonly > network_readonly_role.yaml
