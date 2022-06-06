import aws_cdk as cdk
import aws_cdk.aws_iam as iam


class App(cdk.App):
    def __init__(self):
        super().__init__()
        Account(scope=self, id="Account")


class Account(cdk.Stack):
    """Defines AWS account management resources.

    Non-interactive IAM users are defined as a list of IDs.

    Use the following command to create an access key for a user:

        aws iam create-access-key --user-name UserName

    IAM users are defined as a list of IDs. The policy attached to IAM users
    enforces MFA for every action. AWS Vault makes it easy to configure a profile
    that assumes the administrator role and prompts for an MFA token.

    User names are generated automatically by CloudFormation. Run the following
    command to see user names:

        aws iam create-access-key --user-name UserName
    """

    def __init__(self, scope, id):
        super().__init__(scope, id, description="Account management stack")

        # Reference existing CDK roles to be assumed by non-interactive users.
        cdk_roles = [
            iam.Role.from_role_name(self, id, role_name)
            for id, role_name in (
                (
                    "CdkDeployRole",
                    "cdk-hnb659fds-deploy-role-961672313229-ap-southeast-2",
                ),
                (
                    "CdkFilePublishingRole",
                    "cdk-hnb659fds-file-publishing-role-961672313229-ap-southeast-2",
                ),
                (
                    "CdkImagePublishingRole",
                    "cdk-hnb659fds-image-publishing-role-961672313229-ap-southeast-2",
                ),
            )
        ]

        # Create non-interactive IAM users (e.g., for CI/CD pipelines). Allow users
        # to assume CDK roles.
        for id in [
            # Used by https://github.com/eidorb/aws Github Actions workflow.
            "github-eidorb-aws",
        ]:
            user = iam.User(self, id)
            for role in cdk_roles:
                role.grant_assume_role(user)

        # Create a policy to allow IAM users to self-manage credentials.
        iam_policy = SelfManageCredentialsWithMFA(
            scope=self, id="SelfManageCredentials"
        )

        # Create an administrator role.
        administrator_role = iam.Role(
            scope=self,
            id="Administrator",
            assumed_by=iam.AccountPrincipal(self.account),
            description="Administrator role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ],
        )

        # Create IAM users. Attach policy and grant assume Administrator role to
        # IAM users. This means IAM users can't do much without assuming the
        # Administrator role with MFA.
        for id in [
            # "brodie",
        ]:
            user = iam.User(scope=self, id=id)
            iam_policy.attach_to_user(user)
            administrator_role.grant_assume_role(user)


class SelfManageCredentialsWithMFA(iam.ManagedPolicy):
    """Allows users to self-manage their credentials with MFA.

    Note, all other actions are denied without MFA.

    https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_aws_my-sec-creds-self-manage.html
    """

    def __init__(self, scope, id):
        super().__init__(
            scope,
            id,
            description="Allows MFA-authenticated IAM users to manage their own credentials on the My Security Credentials page",
            statements=[
                iam.PolicyStatement(
                    sid="AllowViewAccountInfo",
                    actions=[
                        "iam:GetAccountPasswordPolicy",
                        "iam:GetAccountSummary",
                        "iam:ListVirtualMFADevices",
                    ],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnPasswords",
                    actions=["iam:ChangePassword", "iam:GetUser"],
                    resources=["arn:aws:iam::*:user/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnAccessKeys",
                    actions=[
                        "iam:CreateAccessKey",
                        "iam:DeleteAccessKey",
                        "iam:ListAccessKeys",
                        "iam:UpdateAccessKey",
                    ],
                    resources=["arn:aws:iam::*:user/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnSigningCertificates",
                    actions=[
                        "iam:DeleteSigningCertificate",
                        "iam:ListSigningCertificates",
                        "iam:UpdateSigningCertificate",
                        "iam:UploadSigningCertificate",
                    ],
                    resources=["arn:aws:iam::*:user/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnSSHPublicKeys",
                    actions=[
                        "iam:DeleteSSHPublicKey",
                        "iam:GetSSHPublicKey",
                        "iam:ListSSHPublicKeys",
                        "iam:UpdateSSHPublicKey",
                        "iam:UploadSSHPublicKey",
                    ],
                    resources=["arn:aws:iam::*:user/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnGitCredentials",
                    actions=[
                        "iam:CreateServiceSpecificCredential",
                        "iam:DeleteServiceSpecificCredential",
                        "iam:ListServiceSpecificCredentials",
                        "iam:ResetServiceSpecificCredential",
                        "iam:UpdateServiceSpecificCredential",
                    ],
                    resources=["arn:aws:iam::*:user/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnVirtualMFADevice",
                    actions=[
                        "iam:CreateVirtualMFADevice",
                        "iam:DeleteVirtualMFADevice",
                    ],
                    resources=["arn:aws:iam::*:mfa/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="AllowManageOwnUserMFA",
                    actions=[
                        "iam:DeactivateMFADevice",
                        "iam:EnableMFADevice",
                        "iam:ListMFADevices",
                        "iam:ResyncMFADevice",
                    ],
                    resources=["arn:aws:iam::*:user/${aws:username}"],
                ),
                iam.PolicyStatement(
                    sid="DenyAllExceptListedIfNoMFA",
                    effect=iam.Effect.DENY,
                    not_actions=[
                        "iam:CreateVirtualMFADevice",
                        "iam:EnableMFADevice",
                        "iam:GetUser",
                        "iam:ListMFADevices",
                        "iam:ListVirtualMFADevices",
                        "iam:ResyncMFADevice",
                        "sts:GetSessionToken",
                    ],
                    resources=["*"],
                    conditions={
                        "BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}
                    },
                ),
            ],
        )


if __name__ == "__main__":
    App().synth()
