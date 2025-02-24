import json
import boto3
import ipaddress
import os

# Load CIDR from GitHub Environment
input_cidr = os.getenv("IPV4_CIDR")
customer_name = os.getenv("CUSTOMER_NAME")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

if not input_cidr:
    print("Error: CIDR is missing from the environment!")
    exit(1)

# Initialize AWS Clients
ec2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
sns = boto3.client("sns", region_name=os.getenv("AWS_REGION"))

# Hardcoded Transit Gateway Route Table ID
tgw_table_id = "tgw-00300246ad005bc2b"

def check_cidr_overlap(input_cidr, tgw_table_id):
    input_network = ipaddress.ip_network(input_cidr)
    overlaps_found = []

    tgw_routes = ec2.search_transit_gateway_routes(
        TransitGatewayRouteTableId=tgw_table_id,
        Filters=[{"Name": "state", "Values": ["active"]}]
    )

    for route in tgw_routes["Routes"]:
        if "DestinationCidrBlock" in route:
            cidr = route["DestinationCidrBlock"]

            # Ignore default route
            if cidr == "0.0.0.0/0":
                continue

            existing_network = ipaddress.ip_network(cidr)
            if input_network.overlaps(existing_network):
                overlaps_found.append({
                    "TransitGatewayRouteTableId": tgw_table_id,
                    "OverlappingCIDR": cidr
                })

    return overlaps_found

# Check for CIDR overlaps
overlapping_cidrs = check_cidr_overlap(input_cidr, tgw_table_id)

if overlapping_cidrs:
    message = f"\U0001F6A8 **CIDR Overlap Detected for {customer_name}!** \U0001F6A8\n"
    message += f"\U0001F537 **Input CIDR:** {input_cidr}\n\n"
    message += "**\U0001F537 Overlapping CIDRs:**\n"
    for overlap in overlapping_cidrs:
        message += f"\U0001F537 {overlap['OverlappingCIDR']} (TGW Route Table: {overlap['TransitGatewayRouteTableId']})\n"

    print("CIDR Overlap detected. Sending SNS alert...")
    
    sns.publish(
        TopicArn=sns_topic_arn,
        Subject="⚠️ CIDR Overlap Detected",
        Message=message
    )

    print("Alert sent successfully!")
else:
    print(f"No CIDR overlaps found for {input_cidr} in TGW Route Table {tgw_table_id}.")
