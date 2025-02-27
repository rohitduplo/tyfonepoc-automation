#provider "aws" {
#  profile = var.aws_profile # Use AWS profile for local testing
#  region  = var.aws_region
#}
terraform {

  backend "s3" {
    bucket         = "tyfonepoc-automation"
    #key            = "customer"
    key            = var.customer_name
    region         = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

# Create a Customer Gateway for VPN
resource "aws_customer_gateway" "cgw" {
  bgp_asn    = var.vpn_routing == "BGP" ? tonumber(var.asn) : 65000 # Default ASN for Static Routing
  ip_address = var.customer_gateway_ip
  type       = "ipsec.1"

  tags = {
    Name = "${var.customer_name}-cgw"
  }
}

# Reference the existing Transit Gateway
data "aws_ec2_transit_gateway" "tgw" {
 filter {
  name   = "transit-gateway-id"
  #id = var.transit_gateway_id # Provide your TGW ID
  values = [var.transit_gateway_id]  # Ensure this matches the exact TGW ID
}
}

# Create the Site-to-Site VPN Connection using TGW
resource "aws_vpn_connection" "vpn" {
  customer_gateway_id = aws_customer_gateway.cgw.id
  transit_gateway_id  = data.aws_ec2_transit_gateway.tgw.id
  type                = "ipsec.1"

  static_routes_only = var.vpn_routing == "Static" ? true : false

  #tunnel1_inside_cidr = var.ipv4_cidr
  #tunnel2_inside_cidr = var.ipv4_cidr

  tunnel1_preshared_key = var.preshared_key
  tunnel2_preshared_key = var.preshared_key

  tunnel1_phase1_encryption_algorithms = [var.encryption_phase1]
  tunnel1_phase2_encryption_algorithms = [var.encryption_phase1]
  tunnel1_phase1_integrity_algorithms  = [var.integrity_phase1]
  tunnel1_phase2_integrity_algorithms  = [var.integrity_phase1]
  tunnel1_phase1_dh_group_numbers      = [tonumber(var.dh_group_phase1)]
  tunnel1_phase2_dh_group_numbers      = [tonumber(var.dh_group_phase1)]
  tunnel1_phase1_lifetime_seconds      = tonumber(var.lifetime_phase1)
  tunnel1_phase2_lifetime_seconds      = var.life_time_renegotiation
  tunnel1_ike_versions                 = [var.ike_version_phase1]

  tunnel2_phase1_encryption_algorithms = [var.encryption_phase2]
  tunnel2_phase2_encryption_algorithms = [var.encryption_phase2]
  tunnel2_phase2_integrity_algorithms  = [var.integrity_phase2]
  tunnel2_phase1_integrity_algorithms  = [var.integrity_phase2]
  tunnel2_phase1_dh_group_numbers      = [tonumber(var.dh_group_phase2)]
  tunnel2_phase2_dh_group_numbers      = [tonumber(var.dh_group_phase2)]
  tunnel2_phase1_lifetime_seconds      = tonumber(var.lifetime_phase1)
  tunnel2_phase2_lifetime_seconds      = var.life_time_renegotiation
  tunnel2_ike_versions                 = [var.ike_version_phase2]

  tags = {
    Name = "${var.customer_name}-vpn"
  }
}

# Add route to Transit Gateway Route Table if VPN uses Static Routing
resource "aws_ec2_transit_gateway_route" "vpn_route" {
  count = var.vpn_routing == "Static" ? 1 : 0

  destination_cidr_block         = var.ipv4_cidr
  transit_gateway_route_table_id = var.transit_gateway_route_table_id
  transit_gateway_attachment_id  = aws_vpn_connection.vpn.transit_gateway_attachment_id
}
