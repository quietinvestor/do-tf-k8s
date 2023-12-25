resource "digitalocean_vpc" "project001" {
  description = "project001 test VPC"
  ip_range    = "10.111.0.0/16"
  name        = "vpc-project001-test"
  region      = "nyc1"
}
