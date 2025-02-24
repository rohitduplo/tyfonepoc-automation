import json
import boto3
import ipaddress
import sys

# Initialize AWS Clients
ec2 = boto3.client("ec2")
sns = boto3.client("sns")

# SNS Topic ARN
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:590184024707:tyfone-poc"

def check_cidr_overlap(input_cidr):
    input_network = ipaddress.ip_network(input_cidr)
    transit_gateway_tables = ec2.describe_transit_gateway_route_tables()
    overlaps_found = []

    for tgw_table in transit_gateway_tables["TransitGatewayRouteTables"]:
        tgw_table_id = tgw_table["TransitGatewayRouteTableId"]

        tgw_routes = ec2.search_transit_gateway_routes(
            TransitGatewayRouteTableId=tgw_table_id,
            Filters=[{"Name": "state", "Values": ["active"]}]
        )

        for route in tgw_routes["Routes"]:
            if "DestinationCidrBlock" in route:
                cidr = route["DestinationCidrBlock"]

                # Skip default route
                if cidr == "0.0.0.0/0":
                    continue  

                existing_network = ipaddress.ip_network(cidr)

                if input_network.overlaps(existing_network):
                    overlaps_found.append({
                        "TransitGatewayRouteTableId": tgw_table_id,
                        "OverlappingCIDR": cidr
                    })

    if overlaps_found:
        message = f"🚨 CIDR Overlap Detected! 🚨\n\n"
        message += f"🔹 **Input CIDR:** {input_cidr}\n\n"
        message += "**🔹 Overlapping CIDRs:**\n"
        for overlap in overlaps_found:
            message += f"🔹 {overlap['OverlappingCIDR']} (TGW Route Table: {overlap['TransitGatewayRouteTableId']})\n"

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="⚠️ CIDR Overlap Detected in AWS Transit Gateway",
            Message=message
        )

        print("overlap=true")
        sys.exit(1)  # Exit with an error to stop Terraform deployment
    else:
        print("overlap=false")
        sys.exit(0)  # Continue to Terraform deployment

if __name__ == "__main__":
    cidr_to_check = sys.argv[1]
    check_cidr_overlap(cidr_to_check)
