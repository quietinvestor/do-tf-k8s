terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "2.32.0"
    }
    ##################################################
    #                                                #
    # STEP 2: Terraform remote backend setup - START #
    #                                                #
    ##################################################
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.21.0"
    }
    ##################################################
    #                                                #
    # STEP 2: Terraform remote backend setup - END   #
    #                                                #
    ##################################################
  }

  ##################################################
  #                                                #
  # STEP 3: Terraform remote backend setup - START #
  #                                                #
  ##################################################
  backend "pg" {}
  ##################################################
  #                                                #
  # STEP 3: Terraform remote backend setup - END   #
  #                                                #
  ##################################################
}

provider "digitalocean" {
  token = var.do_token
}

##################################################
#                                                #
# STEP 2: Terraform remote backend setup - START #
#                                                #
##################################################
provider "postgresql" {
  database    = var.do_db_postgresql_terraform_backend_name
  host        = var.psql_terraform_backend_host
  password    = var.psql_terraform_backend_password
  port        = var.psql_terraform_backend_port
  username    = var.psql_terraform_backend_username
  sslmode     = "verify-full"
  sslrootcert = var.psql_terraform_backend_ca_path
}
##################################################
#                                                #
# STEP 2: Terraform remote backend setup - END   #
#                                                #
##################################################
