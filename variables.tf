variable "region" {
  description = "AWS region"
  default     = "us-west-2"
}

variable "customer" {
  description = "Customer name for prefixing AWS names."
  default     = "strateos"
}

variable "appname" {
  description = "App name."
  default     = "data-ingest"
}