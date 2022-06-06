# aws

AWS accounts as code.


# Getting started

Set up a local development environment.

Assuming [`micromamba`](https://mamba.readthedocs.io/en/latest/installation.html#micromamba) is installed, create a Mamba environment named `aws` defined in `environment.yml`:

    micromamba create --file environment.yml --yes

This creates a Mamba environment with the programs required to build and deploy the project.

Next, install Node.js package dependencies (defined in `package-lock.json`):

    micromamba run --name aws npm ci

Assuming [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer) is installed, install Python package dependencies (defined in `poetry.lock`):

    micromamba run --name aws poetry install

Activate the `aws` environment to run programs without having to prefix them with `micromamba run --name aws ...`:

    micromamba activate aws
    git-crypt status


# Bootstrapping

## Bootstrap AWS CDK

Before using CDK to deploy to an AWS account and region, we must first [bootstrap it](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html). This provisions resources used by AWS CDK during deployment.

Initially, we have an AWS account with only a root user. Therefore, the first CDK bootstrap must done using root credentials. Assuming credentials are managed with an [AWS Vault](https://github.com/99designs/aws-vault) profile named `root`, and a default account and region have been configured, run the following:

    micromamba activate aws
    aws-vault exec root -- npx cdk bootstrap


## Bootstrap automatic deployment

This project's CDK stack defines an IAM user that is used to perform automatic deployments from a CI/CD pipeline. Deploy the CDK stack manually:

    aws-vault exec root -- npx cdk deploy

This created a non-interactive IAM user that can perform CDK deployments. Find the IAM user's ARN:

    aws-vault exec root -- aws iam list-users

In my case it is `arn:aws:iam::961672313229:user/Account-githubeidorbaws9CA4BAE6-18WS93GLVLV5A`. Create an access key for this user:

    aws-vault exec root -- aws iam create-access-key --user-name Account-githubeidorbaws9CA4BAE6-18WS93GLVLV5A

Store the credentials in `.aws/config`. (This file is encrypted using [git-crypt](https://www.agwa.name/projects/git-crypt/).)
