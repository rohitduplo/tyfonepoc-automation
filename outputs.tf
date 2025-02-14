output "vpn_id" {
  description = "ID of the created VPN connection"
  value       = aws_vpn_connection.vpn.id
}

# Remove the incorrect `state` attribute
# Use `aws_vpn_connection.vpn.transit_gateway_attachment_id` instead
output "vpn_attachment_id" {
  description = "The attachment ID of the VPN connection to the Transit Gateway"
  value       = aws_vpn_connection.vpn.transit_gateway_attachment_id
}

output "customer_gateway_id" {
  description = "ID of the created Customer Gateway"
  value       = aws_customer_gateway.cgw.id
}