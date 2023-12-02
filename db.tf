resource "digitalocean_database_cluster" "postgresql" {
  engine               = "pg"
  name                 = "db-postgresql-${var.do_region}-${var.do_project_name}-${var.do_environment}"
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

resource "digitalocean_database_db" "terraform_backend" {
  cluster_id = digitalocean_database_cluster.postgresql.id
  name       = var.do_db_postgresql_terraform_backend_name
}
