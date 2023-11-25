variable "do_db_cluster_postgresql_node_number" {
  type        = number
  description = "DigitalOcean PostgreSQL cluster number of nodes"
  sensitive   = true
}

variable "do_db_cluster_postgresql_node_size" {
  type        = string
  description = "DigitalOcean PostgreSQL cluster node size"
  sensitive   = true
}

variable "do_db_cluster_postgresql_user_local_admin" {
  type        = string
  description = "DigitalOcean PostgreSQL cluster local admin user"
  sensitive   = true
}

variable "do_db_cluster_postgresql_version" {
  type        = string
  description = "DigitalOcean PostgreSQL cluster version"
  sensitive   = true
}

variable "do_db_cluster_postgresql_window_day" {
  type        = string
  description = "DigitalOcean PostgreSQL cluster maintenance window day"
  sensitive   = true
}

variable "do_db_cluster_postgresql_window_hour" {
  type        = string
  description = "DigitalOcean PostgreSQL cluster maintenance window hour"
  sensitive   = true
}

variable "do_db_postgresql_terraform_backend_name" {
  type        = string
  description = "DigitalOcean PostgreSQL database name for Terraform backend"
  sensitive   = true
}

variable "do_project_description" {
  type        = string
  description = "DigitalOcean project description"
  sensitive   = true
}

variable "do_project_environment" {
  type        = string
  description = "DigitalOcean project environment"
  sensitive   = true
}

variable "do_project_name" {
  type        = string
  description = "DigitalOcean project name"
  sensitive   = true
}

variable "do_project_purpose" {
  type        = string
  description = "DigitalOcean project purpose"
  sensitive   = true
}

variable "do_region" {
  type        = string
  description = "DigitalOcean region"
  sensitive   = true
}

variable "do_token" {
  type        = string
  description = "DigitalOcean API token"
  sensitive   = true
}

variable "do_vpc_postgresql_description" {
  type        = string
  description = "DigitalOcean PostgreSQL VPC description"
  sensitive   = true
}

variable "do_vpc_postgresql_ip_range" {
  type        = string
  description = "DigitalOcean PostgreSQL VPC IP range"
  sensitive   = true
}

variable "ip_local_admin" {
  type        = string
  description = "Local admin IP address"
  sensitive   = true
}
