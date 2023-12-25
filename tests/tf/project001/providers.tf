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
