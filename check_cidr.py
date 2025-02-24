import json
import boto3
import ipaddress
import sys
import os

# AWS Region
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # Default to us-east-1 if not set

# Initialize AWS Clients
ec2 = boto3.client("ec2", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

# SNS Topic ARN
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:590184024707:tyfone-poc"

# Specific Transit Gateway Route Table ID
TGW_ROUTE_TABLE_ID = "tgw-00300246ad005bc2b"

def check_cidr_overlap(input_cidr):
    input_network = ipaddress.ip_network(input_cidr)
    overlaps_found = []

    tgw_routes = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=TGW_ROUTE_TABLE_ID,
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
                overlaps_found.append(cidr)

    if overlaps_found:
        message = f"🚨 CIDR Overlap Detected! 🚨\n\n"
        message += f"🔹 **Input CIDR:** {input_cidr}\n\n"
        message += "**🔹 Overlapping CIDRs:**\n"
        for overlap in overlaps_found:
            message += f"🔹 {overlap} (TGW Route Table: {TGW_ROUTE_TABLE_ID})\n"

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
