import aws_cdk as cdk
import aws_cdk.aws_cloudtrail as cloudtrail
import aws_cdk.aws_iam as iam
import aws_cdk.aws_route53 as route53
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

    Account actions are audited with CloudTrail.

    Set up brodie.id.au hosted zone.
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
                (
                    "CdkDeployRoleUsEast1",
                    "cdk-hnb659fds-deploy-role-961672313229-us-east-1",
                ),
                (
                    "CdkFilePublishingRoleUsEast1",
                    "cdk-hnb659fds-file-publishing-role-961672313229-us-east-1",
                ),
                (
                    "CdkImagePublishingRoleUsEast1",
                    "cdk-hnb659fds-image-publishing-role-961672313229-us-east-1",
                ),
            )
        ]

        # Configure GitHub OIDC identity provider.
        # https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
        github_provider = iam.OpenIdConnectProvider(
            scope=self,
            id="GithubProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            # See https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/
            thumbprints=[
                "6938fd4d98bab03faadb97b34396831e3780aea1",
                "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
            ],
        )

        # Configure a role assumed by the GitHub identity provider.
        github_oidc_role = iam.Role(
            scope=self,
            id="GithubOidcRole",
            # The role can only be assumed by principals that that match the specified
            # conditions. The conditions verify the claims of GitHub Actions workflow
            # tokens.
            assumed_by=iam.WebIdentityPrincipal(
                identity_provider=github_provider.open_id_connect_provider_arn,
                conditions={
                    "StringLike": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": [
                            # Trust tokens issued to the following GitHub Actions
                            # workflows:
                            # Repo: eidorb/aws, branch: master.
                            "repo:eidorb/aws:ref:refs/heads/master",
                            # TODO: Limit to master branch only.
                            # Repo: eidorb/portfolio, branch: any.
                            "repo:eidorb/portfolio:ref:refs/heads/*",
                            # Repo: eidorb/brodie.id.au, branch: ANY.
                            "repo:eidorb/brodie.id.au:ref:refs/heads/*",
                            # Repo: eidorb/lungs, branch: main.
                            "repo:eidorb/lungs:ref:refs/heads/main",
                            # Repo: eidorb/oopsie, branch: main.
                            "repo:eidorb/oopsie:ref:refs/heads/main",
                            # Repo: eidorb/serverlisso, branch: ANY.
                            "repo:eidorb/serverlisso:ref:refs/heads/*",
                        ],
                    }
                },
            ),
        )

        # Grant the role the ability to assume CDK roles.
        for role in cdk_roles:
            role.grant_assume_role(github_oidc_role)

        # Audit account actions with CloudTrail.
        cloudtrail.Trail(scope=self, id="Trail")

        # Create public hosted zone for brodie.id.au.
        route53.PublicHostedZone(
            scope=self, id="BrodieIdAuHostedZone", zone_name="brodie.id.au"
        )


if __name__ == "__main__":
    App().synth()
