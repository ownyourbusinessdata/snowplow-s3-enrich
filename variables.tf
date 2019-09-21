variable env {
  description = "Service"
  default = "sp-pixel-lambda"
}
variable creator {
  description = "Owner of service"
  default = "aleksey"
}

variable website {
  description = "System tag"
  default = "magenable.com.au"
}

variable primary_domain {
  description = "Cloudfront distribution CNAME"
  default = "magenable.com.au"
}

variable access_key {
  description = "AWS access key"
  default = "AKIAXRJUUTMQHWJYBMWN"
}

variable secret_key {
  description = "AWS secret key"
  default = "pzJ0LD54XCIunmwPEy79vy4KQ20q9Uo8SJrT7AQT"
}

variable region {
  description = "AWS region"
  default = "us-west-2"
}
