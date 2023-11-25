##################################################
#                                                #
# STEP 1: Terraform remote backend setup - START #
#                                                #
##################################################
resource "digitalocean_database_cluster" "postgresql" {
  engine               = "pg"
  name                 = "db-postgresql-${var.do_region}-${var.do_project_name}"
  node_count           = var.do_db_cluster_postgresql_node_number
  private_network_uuid = digitalocean_vpc.postgresql.id
  project_id           = digitalocean_project.do_tf_k8s.id
  region               = var.do_region
  size                 = var.do_db_cluster_postgresql_node_size
  version              = var.do_db_cluster_postgresql_version

  maintenance_window {
    day  = var.do_db_cluster_postgresql_window_day
    hour = var.do_db_cluster_postgresql_window_hour
  }
}

resource "digitalocean_database_firewall" "postgresql" {
  cluster_id = digitalocean_database_cluster.postgresql.id

  rule {
    type  = "ip_addr"
    value = var.ip_local_admin
  }
}

resource "digitalocean_database_user" "local_admin" {
  cluster_id = digitalocean_database_cluster.postgresql.id
  name       = var.do_db_cluster_postgresql_user_local_admin
}

resource "digitalocean_database_db" "terraform_backend" {
  cluster_id = digitalocean_database_cluster.postgresql.id
  name       = var.do_db_postgresql_terraform_backend_name
}
##################################################
#                                                #
# STEP 1: Terraform remote backend setup - END   #
#                                                #
##################################################

##################################################
#                                                #
# STEP 2: Terraform remote backend setup - START #
#                                                #
##################################################
resource "postgresql_role" "terraform" {
  name = var.do_db_postgresql_terraform_backend_group_role_admin_name
}

resource "postgresql_grant" "terraform_db" {
  database    = digitalocean_database_db.terraform_backend.name
  role        = postgresql_role.terraform.name
  object_type = "database"
  privileges  = ["CREATE"]
}

resource "postgresql_grant" "terraform_schema_public" {
  database    = digitalocean_database_db.terraform_backend.name
  object_type = "schema"
  privileges  = ["CREATE"]
  role        = postgresql_role.terraform.name
  schema      = "public"
}

resource "postgresql_grant_role" "terraform" {
  role       = digitalocean_database_user.local_admin.name
  grant_role = postgresql_role.terraform.name
}
##################################################
#                                                #
# STEP 2: Terraform remote backend setup - END   #
#                                                #
##################################################
