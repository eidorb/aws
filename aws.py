import aws_cdk as cdk


class App(cdk.App):
    def __init__(self):
        super().__init__()

        ManagementStack(scope=self, id="ManagementStack")


class ManagementStack(cdk.Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id, description="Management stack")


if __name__ == "__main__":
    App().synth()
