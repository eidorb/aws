import aws_cdk as cdk
import aws_cdk.aws_iam as iam
import aws_cdk.aws_sso as sso


class App(cdk.App):
    def __init__(self):
        super().__init__()
        Account(scope=self, id="Account")


class Account(cdk.Stack):
    """Defines AWS account management resources.

    AWS SSO is configured to assign AdministratorAccess permissions to a group.

    Non-interactive IAM users are defined as a list of IDs.

    Use the following command to create an access key for a user:

        aws iam create-access-key --user-name UserName
    """

    def __init__(self, scope, id):
        super().__init__(scope, id, description="Account management stack")

        # Assign administrator access to an SSO group. Create an assignemnt
        sso.CfnAssignment(
            scope=self,
            id="AdministratorAssignment",
            instance_arn="arn:aws:sso:::instance/ssoins-82598d5031b7ada7",
            permission_set_arn=sso.CfnPermissionSet(
                scope=self,
                id="AdministratorPermissionSet",
                instance_arn="arn:aws:sso:::instance/ssoins-82598d5031b7ada7",
                name="administrator",
                managed_policies=["arn:aws:iam::aws:policy/AdministratorAccess"],
            ).attr_permission_set_arn,
            principal_id="976779ecf4-ca627ff1-e7ca-4ace-9ae0-be6e495c7048",
            principal_type="GROUP",
            target_id="961672313229",
            target_type="AWS_ACCOUNT",
        )

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


if __name__ == "__main__":
    App().synth()
