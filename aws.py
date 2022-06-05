import aws_cdk as cdk
import aws_cdk.aws_iam as iam


class App(cdk.App):
    def __init__(self):
        super().__init__()
        Identity(scope=self, id="Identity")


class Identity(cdk.Stack):
    """Defines AWS account identities.

    Non-interactive IAM users are defined as a list of IDs. User names are generated
    automatically by CloudFormation.

    Use the following command to create an access key for a user:

        aws iam create-access-key --user-name UserName
    """

    def __init__(self, scope, id):
        super().__init__(scope, id, description="Defines account identities")

        # Create non-interactive IAM users (e.g., for CI/CD pipelines).
        [
            iam.User(scope=self, id=id)
            for id in [
                # Used by https://github.com/eidorb/aws Github Actions workflow.
                "github-eidorb-aws",
            ]
        ]


if __name__ == "__main__":
    App().synth()
