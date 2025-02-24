variable "aws_profile" {
  description = "AWS Profile for authentication"
  type        = string
  default     = "ops"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "customer_name" {
  description = "Name of the customer"
  type        = string
  default     = "rohitsingh"
}

variable "vpn_routing" {
  description = "Type of VPN Routing (Static or BGP)"
  type        = string
  default     = "Static"
}

variable "asn" {
  description = "BGP ASN number for the Customer Gateway"
  type        = number
  default     = 65000
}

variable "customer_gateway_ip" {
  description = "Public IP address of the Customer Gateway"
  type        = string
  default     = "110.227.217.101"
}

variable "transit_gateway_id" {
  description = "Transit Gateway ID"
  type        = string
  default     = "tgw-00300246ad005bc2b"
}

variable "transit_gateway_route_table_id" {
  description = "Transit Gateway Route Table ID"
  type        = string
  default     = "tgw-rtb-08b96e71763e7b5ad"
}

variable "ipv4_cidr" {
  description = "The inside CIDR block for VPN tunnels"
  type        = string
  default     = "192.168.0.0/22"
}

variable "preshared_key" {
  description = "Pre-shared key for VPN tunnels"
  type        = string
  default     = "Rohitsinghaseqw3dsada"
}

variable "encryption_phase1" {
  description = "Encryption algorithm for Phase 1"
  type        = string
  default     = "AES256"
}

variable "integrity_phase1" {
  description = "Integrity algorithm for Phase 1"
  type        = string
  default     = "SHA2-512"
}

variable "dh_group_phase1" {
  description = "Diffie-Hellman Group for Phase 1"
  type        = number
  default     = 21
}

variable "encryption_phase2" {
  description = "Encryption algorithm for Phase 2"
  type        = string
  default     = "AES256"
}

variable "integrity_phase2" {
  description = "Integrity algorithm for Phase 2"
  type        = string
  default     = "SHA2-512"
}

variable "dh_group_phase2" {
  description = "Diffie-Hellman Group for Phase 2"
  type        = number
  default     = 21
}

variable "lifetime_phase1" {
  description = "Life Time (for Negotiation)"
  type        = number
  default     = 28800
}

variable "life_time_renegotiation" {
  description = "Life Time (For Renegotiation)"
  type        = number
  default     = 3600
}

variable "ike_version_phase1" {
  description = "IKE Version [Phase1]"
  type        = string
  default     = "ikev2"
}

variable "ike_version_phase2" {
  description = "IKE Version [Phase2]"
  type        = string
  default     = "ikev2"
}
