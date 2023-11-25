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

variable "do_project_resources" {
  type        = list(string)
  description = "DigitalOcean project resource list of Uniform Resource Names (URN)"
  sensitive   = true
}

variable "do_token" {
  type        = string
  description = "DigitalOcean API token"
  sensitive   = true
}

