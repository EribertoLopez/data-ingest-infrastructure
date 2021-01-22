variable "region" {
  description = "AWS region"
  default     = "us-west-2"
}

variable "customer" {
  description = "Customer name for prefixing AWS names."
  default     = "strateos"
}

variable "workspace" {
  description = ""
  default = terraform.workspace
}