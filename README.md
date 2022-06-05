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
