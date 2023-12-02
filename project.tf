resource "digitalocean_project" "do_tf_k8s" {
  description = var.do_project_description
  environment = var.do_project_environment
  name        = "${var.do_project_name}-${var.do_environment}"
  purpose     = var.do_project_purpose
}
