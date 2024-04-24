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
    which python


# Bootstrapping

## Bootstrap AWS CDK

Before using CDK to deploy to an AWS account and region, we must first [bootstrap it](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html). This provisions resources used by AWS CDK during deployment.

Initially, we have an AWS account with only a root user. Therefore, the first CDK bootstrap must done using root credentials. Assuming credentials are managed with an [AWS Vault](https://github.com/99designs/aws-vault) profile named `root`, and a default account and region have been configured, run the following:

    micromamba activate aws
    aws-vault exec root -- npx cdk bootstrap


## Bootstrap automatic deployment

This project's CDK stack defines a GitHub OIDC identity provider. The role assumed by this identity provider must be created before it can be referenced in this project's CI/CD pipeline. Deploy the CDK stack manually:

    aws-vault exec root -- npx cdk deploy

This created a an IAM role assumed by the GitHub OIDC identity provider. Find its ARN:

    aws-vault exec root -- aws iam list-roles

Configure the role's ARN in the `aws-actions/configure-aws-credentials` task in the workflow.


# SSO

The CDK stack assigns administrator access to a group in SSO. AWS SSO (and AWS Organizations too) must be enabled from the console. The AWS SSO built-in identity source can be used to manage users and groups.

## How-to guides

### How to upgrade Node.js

Pin the `nodejs` dependency in [environment.yml](environment.yml) to the active LTS version listed on [this page](https://nodejs.org/en/about/previous-releases).
