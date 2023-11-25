resource "digitalocean_project" "do_tf_k8s" {
  environment = var.do_project_environment
  description = var.do_project_description
  name        = var.do_project_name
  purpose     = var.do_project_purpose
  resources   = var.do_project_resources
}
