import json
import boto3
import ipaddress
import os
import sys

# Load CIDR from GitHub Environment
input_cidr = os.getenv("IPV4_CIDR")
customer_name = os.getenv("CUSTOMER_NAME")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

if not input_cidr:
    print("Error: CIDR is missing from the environment!")
    sys.exit(1)

# Initialize AWS Clients
ec2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
sns = boto3.client("sns", region_name=os.getenv("AWS_REGION"))

# Hardcoded TGW Route Table ID
tgw_table_id = "tgw-rtb-08b96e71763e7b5ad"

def check_cidr_overlap(input_cidr, tgw_table_id):
    input_network = ipaddress.ip_network(input_cidr)
    overlaps_found = []

    try:
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

    except Exception as e:
        print(f"Error fetching routes: {e}")
        sys.exit(1)

    return overlaps_found

# Check for CIDR overlaps
overlapping_cidrs = check_cidr_overlap(input_cidr, tgw_table_id)

if overlapping_cidrs:
    message = f"🚨 **CIDR Overlap Detected for {customer_name}!** 🚨\n"
    message += f"🔹 **Input CIDR:** {input_cidr}\n\n"
    message += "**🔹 Overlapping CIDRs:**\n"
    for overlap in overlapping_cidrs:
        message += f"🔹 {overlap['OverlappingCIDR']} (TGW Route Table: {overlap['TransitGatewayRouteTableId']})\n"

    sns.publish(
        TopicArn=sns_topic_arn,
        Subject="⚠️ CIDR Overlap Detected",
        Message=message
    )

    print("Alert sent successfully!")
    print("overlap=true")
    sys.exit(1)  # Exit with an error to stop Terraform deployment
else:
    print(f"No CIDR overlaps found for {input_cidr} in TGW Route Table {tgw_table_id}.")
    print("overlap=false")
    sys.exit(0)  # Continue to Terraform deployment

# Ensure this is outside the if-else block
if __name__ == "__main__":
    cidr_to_check = sys.argv[1]
    check_cidr_overlap(cidr_to_check, tgw_table_id)
