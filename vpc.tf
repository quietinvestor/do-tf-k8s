resource "digitalocean_vpc" "postgresql" {
  description = var.do_vpc_postgresql_description
  ip_range    = var.do_vpc_postgresql_ip_range
  name        = "vpc-postgresql-${var.do_region}-${var.do_project_name}"
  region      = var.do_region
}
