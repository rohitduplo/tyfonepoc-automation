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
overlapping_cidrs = check_cidr_overlap(input_cidr)

if overlapping_cidrs:
    message = f"🚨 **CIDR Overlap Detected for {customer_name}!** 🚨\n"
    message += f"🔹 **Input CIDR:** {input_cidr}\n\n"
    message += "**🔹 Overlapping CIDRs:**\n"
    for overlap in overlapping_cidrs:
        message += f"🔹 {overlap['OverlappingCIDR']} (TGW Route Table: {overlap['TransitGatewayRouteTableId']})\n"

    print("CIDR Overlap detected. Sending SNS alert...")
    
    sns.publish(
        TopicArn=sns_topic_arn,
        Subject="⚠️ CIDR Overlap Detected",
        Message=message
    )

    print("Alert sent successfully!")
else:
    print(f"No CIDR overlaps found for {input_cidr}.")
