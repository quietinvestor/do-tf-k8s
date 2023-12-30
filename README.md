# DigitalOcean Terraform PostgreSQL Backend

## Table of Contents

1. [General](#1-general)
  * [Overview](#-overview)
  * [Why](#-why)
  * [Architecture](#-architecture)
  * [Requirements](#-requirements)
  * [Download](#-download)
2. [Terraform](#2-terraform)
  * [Install](#-install)
  * [Run](#-run)
  * [Apply Changes](#-apply-changes)
  * [Destroy](#-destroy)
  * [Variables](#-variables)
    * [terraform.tfvars](#-terraformtfvars)
    * [Environment Variables](#-environment-variables)
3. [Python](#3-python)
  * [Setup](#-setup)
  * [Create a PostgreSQL Remote Backend](#-create-a-postgresql-remote-backend)
  * [Script](#-script)
4. [PostgreSQL Remote Backend](#4-postgresql-remote-backend)
  * [Usage](#-usage)

## 1. General

### &bull; Overview

PostgreSQL backend for Terraform on DigitalOcean.

### &bull; Why?

DigitalOcean currently supports two main Terraform remote backends:
1. *S3*: While the Terraform `s3` backend supports any "S3-compatible" backend, such as DigitalOcean spaces, the maintainers have stated time and again that they only test the code against the official Amazon Web Services (AWS) S3 buckets. Therefore, there is no guarantee that it will always work with DigitalOcean workspaces. Additionally, state locking depends on AWS' DynamoDB, so it is not supported on DigitalOcean.
2. *PostgreSQL*: The Terraform `pg` backend supports both storing the `terraform.tfstate` file in a `states` table, as well as state locking leveraging PostgreSQL's advisory locks. Moreover, PostgreSQL is not vendor-dependent.

In its current state at the time of writing, the Terraform `pg` backend hard codes a lot of PostgreSQL database element values and as a result promotes a poor and wasteful design by requiring the creation of a new PostgreSQL database for each separate Terraform project remote backend.

### &bull; Architecture

PostgreSQL per-project remote Terraform backends are instead kept separate by leveraging PostgreSQL schemas, the equivalent of namespaces in other languages, thus avoiding having to create a separate database to provide the necessary isolation for each Terraform project. What is more, separate PostgreSQL group and user roles with privileges limited to the given schema are created for security and further segregation.

The use of environment variables is promoted in the design both for security and ease-of-use when integrating it into CI/CD pipelines, such as GitHub Actions. See `.github/workflows/test-deploy.yaml` for an example.

Usage of Terraform remote backends creates a [chicken or the egg](https://en.wikipedia.org/wiki/Chicken_or_the_egg) dilemma whereby you would like to use a remote backend for every Terraform project in order to keep a redundant backup copy of your `terraform.tfstate` file, as well as perhaps access it from your CI/CD pipeline runners, but at the same time you need to first create that Terraform remote backend with Terraform. Some people opt for using a bootstrapping approach within the same Terraform project, but I believe that it is cleaner to simply accept that the Terraform project that will create the remote backends for all your future Terraform projects will have to rely on a separate local `terraform.tfstate` file that you will have to manually back up by other means.

### &bull; Requirements

- [DigitalOcean access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/) with read and write scopes. For security, said token is passed via the environment variable `DIGITALOCEAN_ACCESS_TOKEN`. This allows to pass its value as a secret if desired. For example, to manually set the environment variable on a `bash` shell:
```
export DIGITALOCEAN_ACCESS_TOKEN=<DigitalOcean API token value>
```
- [Download](https://git-scm.com/downloads) and [install](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) git.
- [Download](https://www.terraform.io/downloads) and [install](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) Terraform.
- [Download](https://www.python.org/downloads/) and install Python, if it is not already included in your Operating System (OS).

### &bull; Download

To download all the required files, input the below commands from the command line:

```
git clone https://github.com/quietinvestor/do-tf-pg-backend.git
```
## 2. Terraform

### &bull; Install

To install the Terraform DigitalOcean provider, go to the newly-downloaded `do-tf-pg-backend` directory, and initialise it:

```
cd do-tf-pg-backend
terraform init
```

### &bull; Run

Prior to executing the Terraform code and creating all the necessary DigitalOcean resources to deploy the PostgreSQL database cluster, while still inside the `do-tf-pg-backend` directory, it is recommended to input the below command from the command line to view the planned output of the DigitalOcean resources you are about to generate without actually creating them:

```
terraform plan
```

After inputting the above command, you will be prompted to provide the values for the necessary input variables, after which the planned output will be displayed.

If the result from the above is satisfactory, you can go ahead and input the below command from the command line to actually create all the necessary DigitalOcean resources to deploy the PostgreSQL database cluster:

```
terraform apply
```

Once again, after inputting the above command, you will be prompted to provide the values for the necessary input variables, after which the planned output will be displayed, alongside a prompt to continue, where you must type `yes` if you would like to go ahead and create all the necessary DigitalOcean resources to deploy the PostgreSQL database cluster.

### &bull; Apply Changes

Please note that Terraform just tracks changes in the infrastructure generated by its code. For example, if you run `terraform apply` and then manually modify any resource from the DigitalOcean Console, Terraform will not detect the change when you run again `terraform apply`. Therefore, the best way to modify the infrastructure is by modifying the corresponding Terraform code, then running `terraform apply` and typing in `yes` at the prompt to continue, once you have confirmed that the planned changes reflect what you would like to apply.

### &bull; Destroy

When the time comes to delete all your infrastructure, you can do so by running the below command:

```
terraform destroy
```

After inputting the above command, terraform will display details of all the resources that will be destroyed and will prompt you to continue. If you type `yes`, it will go ahead and destroy all the resources managed by Terraform.

Please note that Terraform just tracks changes in the infrastructure generated by its code. For example, if you run `terraform apply` and then manually add a new PostgreSQL database cluster firewall rule from the DigitalOcean Console, Terraform will not detect the change when you run `terraform destroy` and will consequently not destroy it. Therefore, the best way to modify the infrastructure is by modifying the corresponding Terraform code, then running `terraform apply` and typing in `yes` at the prompt to continue, once you have confirmed that the planned changes reflect what you would like to apply. As a result, if you later run `terraform destroy`, it will also delete the newly-created PostgreSQL database cluster firewall rule.

### &bull; Variables

Please refer to the table below for a list of the user-input Terraform variables:

| Variable | Description | Example Input | Required? |
| :--- | :--- | :---: | :---: |
| **do_db_cluster_postgresql_node_number** | Number of nodes to deploy for the PostgreSQL database cluster. | _1_ | Yes |
| **do_db_cluster_postgresql_node_size** | Size (vCPUs and Memory) slug of each node to deploy for the PostgreSQL database cluster. | _db-s-1vcpu-1gb_ | Yes |
| **do_db_cluster_postgresql_version** | PostgreSQL version to be used for the database cluster. | _15_ | Yes |
| **do_db_cluster_postgresql_window_day** | Day of the week for DigitalOcean to perform maintenance tasks on the PostgreSQL database cluster as required. | _saturday_ | Yes |
| **do_db_cluster_postgresql_window_hour** | Hour of the day for DigitalOcean to perform maintenance tasks on the PostgreSQL database cluster as required. | _2:00_ | Yes |
| **do_db_postgresql_terraform_backend_name** | Name of PostgreSQL database that will be created to contain all the schemas and corresponding Terraform `states` tables for all the remote backends created. | _pg_backend_db_ | Yes |
| **do_environment** | Environment name. This is mainly used to append it to the DigitalOcean project and PostgreSQL database cluster names. | _dev_ | Yes |
| **do_project_description** | DigitalOcean project description. | _"This is a test project"_ | Yes |
| **do_project_environment** | DigitalOcean project environment name. This has to match one of the available inputs for a project on DigitalOcean. | _Development_ | Yes |
| **do_project_name** | The name of the DigitalOcean project. Please note that, to prevent name clashes, the `do_region` and `do_environment` are appended to name, such that the final project name format is `project_name-do_region-do_environment`. Using the example values on this table, it would be `pg-backend-nyc1-dev`. | _pg-backend_ | Yes |
| **do_project_purpose** | DigitalOcean project purpose. This has to match one of the available inputs for a project on DigitalOcean. | _"Web Application"_ | Yes |
| **do_region** | Slug for one of [DigitalOcean's available regions](https://docs.digitalocean.com/products/platform/availability-matrix/). | _nyc1_ | Yes |
| **do_vpc_postgresql_description** | Description for the DigitalOcean VPC where the PostgreSQL database cluster will be deployed. | _"PostgreSQL database cluster VPC"_ | Yes |
| **do_vpc_postgresql_ip_range** | DigitalOcean VPC subnet CIDR range where the PostgreSQL database cluster will be deployed. | _10.210.0.0/16_ | Yes |
| **ip_local_admin** | For security, access to the PostgreSQL database cluster is only allowed from this local administrator IP address. This is implement by creating a DigitalOcean PostgreSQL database cluster firewall rule. | _1.1.1.1_ | Yes |
| **ip_github_actions_runner** | Similarly implemented as `ip_local_admin`, for use in a GitHub Actions CI/CD pipeline so that you may query for and pass the GitHub Actions runner's IP address at runtime to connect to the DigitalOcean PostgreSQL database cluster. In case this is not used, it has a default value of the localhost IP address: `127.0.0.1`. | _2.2.2.2_ | No |

#### &#9702; terraform.tfvars

For convenience, rather than inputting all required variables when prompted every time that you run `terraform plan` or `terraform apply`, it is recommended to create a file named `terraform.tfvars` alongside the rest of the downloaded Terraform code under `do-tf-pg-backend`, where you can include the variable names and assign the values you wish to them, separating each variable with a new line. For example,

```
do_db_cluster_postgresql_node_number    = 1
do_db_cluster_postgresql_node_size      = "db-s-1vcpu-1gb"
do_db_cluster_postgresql_version        = "15"
do_db_cluster_postgresql_window_day     = "saturday"
do_db_cluster_postgresql_window_hour    = "2:00"
do_db_postgresql_terraform_backend_name = "pg_backend_db"
do_environment                          = "dev"
do_project_description                  = "This is a test project"
do_project_environment                  = "Development"
do_project_name                         = "pg-backend"
do_project_purpose                      = "Web Development"
do_region                               = "nyc1"
do_vpc_postgresql_description           = "PostgreSQL database cluster VPC"
do_vpc_postgresql_ip_range              = "10.210.0.0/16"
ip_local_admin                          = "1.1.1.1"
```

#### &#9702; Environment Variables

You can also pass values to Terraform variables using environment variables, prepending `TF_VAR_` to their actual variable names. This allows you to pass values as secrets or environment variables using tools such as GitHub Actions.

For example, to set `ip_local_admin` in your local `bash` shell:
```
export TF_VAR_ip_local_admin="1.1.1.1"
```

## 3. Python

### &bull; Setup

Assuming that you are using a python [virtual environment](https://docs.python.org/3/tutorial/venv.html) locally within the `do-tf-pg-backend` directory, you can simply install the package dependencies using the pip `requirements.txt` file.
```
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/python/requirements.txt
```

### &bull; Create a PostgreSQL Remote Backend

Once you have deployed the PostgreSQL database cluster on DigitalOcean with Terraform, you need to:
1. Get the connection string for the database that you created with Terraform to hold all your remote backend `states` tables under different schemas.
2. Connect to the database using the default `doadmin` superuser.
3. Create all the necessary elements for a PostgreSQL remote backend for Terraform:
  * Schema: This is the equivalent of a namespace in other languages.
  * Sequence: This is used for numerically indexing the different `terraform.tfstate` row entries. The current Terraform `pg` remote backend implementation hard codes its creation under the default `public` schema of the database. However, to better leverage the separation of different terraform projects using schemas it is preferable to have a sequence within each dedidcated schema.
  * Table: This table will keep all the `terraform.tfstate` files for a given Terraform project under the schema as row entries. Please note that you have to use [Terraform workspaces](https://developer.hashicorp.com/terraform/cli/workspaces) to have different corresponding row entries for `terraform.tfstate`. Unfortunately, the current Terraform `pg` remote backend implementation hard codes the table name to `states`, hence why said table name is preserved.
  * Index: Unfortunately, the current Terraform `pg` remote backend implementation hard codes the index name to `states_by_name`, which is used by `states` table, hence why said index name is preserved.
  * Group Role: For security and scalability, a group role is created with all the necessary privileges to access and use the created schema and its contents, except for login privileges. This allows to create user roles with login privileges and a corresponding password, who in turn become members of said group and inherit its privileges.
  * User Role: Username and password to login to the PostgreSQL database.
4. Get the same connections string as 1. above, but using your newly-created PostgreSQL user role name and password.

### &bull; Script

The `postgresql-backend-create.py` script automates the PostgreSQL remote backend creation by passing a set of required arguments as per the below and returning the PostgreSQL connection string to store in the `PG_CONN_STR` environment variable as required by the Terraform `pg` backend.
```
$ python postgresql-backend-create.py --help

usage: postgresql-backend-create.py [-h] -c CLUSTER_NAME -d DATABASE_NAME -g GROUP_NAME -p USER_PASSWORD -q SEQUENCE_NAME -s SCHEMA_NAME -t TOKEN -u USER_NAME

options:
  -h, --help            show this help message and exit
  -c CLUSTER_NAME, --cluster-name CLUSTER_NAME
                        DigitalOcean PostgreSQL database cluster name
  -d DATABASE_NAME, --database-name DATABASE_NAME
                        PostgreSQL database name
  -g GROUP_NAME, --group-name GROUP_NAME
                        PostgreSQL database schema group name
  -p USER_PASSWORD, --user-password USER_PASSWORD
                        PostgreSQL database schema user password
  -q SEQUENCE_NAME, --sequence-name SEQUENCE_NAME
                        PostgreSQL database schema sequence name
  -s SCHEMA_NAME, --schema-name SCHEMA_NAME
                        PostgreSQL database schema name
  -t TOKEN, --token TOKEN
                        DigitalOcean API token
  -u USER_NAME, --user-name USER_NAME
                        PostgreSQL database schema user name
```
Please note that:
* Preferably, all names used should follow the PostgreSQL naming convention of using only lowercase letters, numbers and underscores.
* The PostgreSQL connection string is output as part of `stdout`, but there is other output printed to `stderr`. Therefore, please make sure that you redirect `stderr` when exporting the output to the `PG_CONN_STR` environment variable. For example, in `bash`,
```
export PG_CONN_STR=$(python scripts/python/postgresql-backend-create.py \
-t "$DIGITALOCEAN_ACCESS_TOKEN" \
-c "db-postgresql-${TF_VAR_do_region}-${TF_VAR_do_project_name}-${TF_VAR_do_environment}" \
-d "$TF_VAR_do_db_postgresql_terraform_backend_name" \
-s "$PG_SCHEMA_NAME" \
-q "$seq_name" \
-g "$group_name" \
-u "$user_name" \
-p "$user_password" \
2> /dev/null)
```
In the above example, I make use of previously-defined environment variables for the Terraform deployment, new environment variables required only by the python script, as well as `PG_SCHEMA_NAME`, the custom name for your schema, which is the other environment variable required by the Terraform `pg` backend. Once more, the use of environment variables allows to pass the values safely via secrets or environment variables in your CI/CD pipeline, such as when using GitHub Actions.

## 4. PostgreSQL Remote Backend

### &bull; Usage

Once the PostgreSQL database cluster has been deployed on DigitalOcean via Terraform and the necessary elements for the PostgreSQL remote backend created via the python script, including populating the `PG_CONN_STR` and `PG_SCHEMA_NAME` environment variables required by the Terraform `pg` backend, the only step left is to create a separate Terraform project that will store its `terraform.tfstate` file in that given schema `states` table.

When configuring the `backend "pg" {}` block in `providers.tf`, please make sure to set all the `skip_..._creation` keys to `true`, given that the PostgreSQL remote backend has already been created. Otherwise, it will try to use its default values and fail.

*providers.tf*
```
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "2.32.0"
    }
  }

  backend "pg" {
    skip_schema_creation = true
    skip_table_creation  = true
    skip_index_creation  = true
  }
}
```
For reference, there is an example Terraform project in this repository under `tests/tf/project001/` that uses the newly-created PostgreSQL remote backend.
