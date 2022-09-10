from time import sleep
import boto3
from botocore.exceptions import ClientError
import sys
import argparse


# Creates VPC on AWS in logged account


class ServiceCreation():
    def vpc_creation(self):
        try:
            create_vpc = ec2.create_vpc(
                CidrBlock=args.cidr,
                InstanceTenancy='default',
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': args.vpc_tag
                            },
                        ]
                    },
                ]
            )
            ServiceCreation.vpc_creation.vpc = create_vpc["Vpc"]["VpcId"]

            print("VPC ID:  ", ServiceCreation.vpc_creation.vpc)

            # Enables DNS hostnames in VPC
            ec2.modify_vpc_attribute(
                EnableDnsHostnames={
                    'Value': True
                },
                VpcId=ServiceCreation.vpc_creation.vpc
            )

            # Enables DNS Resolution
            ec2.modify_vpc_attribute(
                EnableDnsSupport={
                    'Value': True
                },
                VpcId=ServiceCreation.vpc_creation.vpc
            )
        except ClientError as e:
            print(e)
            sys.exit()

    def create_internet_gateway(self):
        # Create and Attach the Internet Gateway
        ig = ec2.create_internet_gateway(TagSpecifications=[
            {
                'ResourceType': 'internet-gateway',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': args.ig_tag
                    },
                ]
            },
        ],)
        ServiceCreation.create_internet_gateway.internet_gateway = ig[
            "InternetGateway"]["InternetGatewayId"]
        print("Attaching IGW to VPC...")

        ec2.attach_internet_gateway(
            InternetGatewayId=ServiceCreation.create_internet_gateway.internet_gateway, VpcId=ServiceCreation.vpc_creation.vpc)
        print("Internet GatewayID:  ",
              ServiceCreation.create_internet_gateway.internet_gateway)

        #------------------ creating multiple subnets----------------------#

    def subnet_creation(self):
        # Create a public Subnet in 1a(AZ)
        try:
            public_subnet_1a = ec2.create_subnet(TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': args.subnetpublic1a_tag
                        },
                    ]
                },
            ],
                CidrBlock=args.subnetpublic1a_cidr,
                AvailabilityZone='ap-south-1a',
                VpcId=ServiceCreation.vpc_creation.vpc
            )
            ServiceCreation.subnet_creation.subnet_id1 = (
                public_subnet_1a["Subnet"]["SubnetId"])
            print("Public subnet on AZ ap-south-1a:  ",
                  ServiceCreation.subnet_creation.subnet_id1)

            # Create a private Subnet in 1a(AZ)
            private_subnet_1a = ec2.create_subnet(TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': args.subnetprivate1a_tag
                        },
                    ]
                },
            ],
                CidrBlock=args.subnetprivate1a_cidr,
                AvailabilityZone='ap-south-1a',
                VpcId=ServiceCreation.vpc_creation.vpc
            )
            ServiceCreation.subnet_creation.subnet_id2 = (
                private_subnet_1a["Subnet"]["SubnetId"])
            print("Private Subnet on AZ ap-south-1a:  ",
                  ServiceCreation.subnet_creation.subnet_id2)

            # Create a public Subnet in 1b(AZ)
            public_subnet_1b = ec2.create_subnet(TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': args.subnetpublic1b_tag
                        },
                    ]
                },
            ],
                CidrBlock=args.subnetpublic1b_cidr,
                AvailabilityZone='ap-south-1b',
                VpcId=ServiceCreation.vpc_creation.vpc
            )
            ServiceCreation.subnet_creation.subnet_id3 = (
                public_subnet_1b["Subnet"]["SubnetId"])
            print("Public Subnet on AZ ap-south-1b:  ",
                  ServiceCreation.subnet_creation.subnet_id3)

            # Create a private Subnet in 1b(AZ)
            private_subnet_1b = ec2.create_subnet(TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': args.subnetprivate1b_tag
                        },
                    ]
                },
            ],
                CidrBlock=args.subnetprivate1b_cidr,
                AvailabilityZone='ap-south-1b',
                VpcId=ServiceCreation.vpc_creation.vpc
            )
            ServiceCreation.subnet_creation.subnet_id4 = (
                private_subnet_1b["Subnet"]["SubnetId"])
            print("Private subnet on AZ ap-south-1b:  ",
                  ServiceCreation.subnet_creation.subnet_id4)
            sleep(1)
        except ClientError as e:
            print(e)
        # Create a route table and a public route to Internet Gateway

    def route_table_creation(self):
        # Creating route table for public subnets
        try:
            public_route_table = ec2.create_route_table(VpcId=ServiceCreation.vpc_creation.vpc,
                                                        TagSpecifications=[
                                                            {
                                                                'ResourceType': 'route-table',
                                                                'Tags': [
                                                                    {
                                                                        'Key': 'Name',
                                                                        'Value': args.publicrtb_tag
                                                                    },
                                                                ]
                                                            },
                                                        ])

            ServiceCreation.route_table_creation.public_rtb = public_route_table[
                "RouteTable"]["RouteTableId"]

            # creates route to attach Internet gateway to VPC
            ec2.create_route(
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=ServiceCreation.create_internet_gateway.internet_gateway,
                RouteTableId=ServiceCreation.route_table_creation.public_rtb
            )

            # Associates public route table with public subnets
            subnets = [ServiceCreation.subnet_creation.subnet_id1,
                       ServiceCreation.subnet_creation.subnet_id3]
            for associate_with_route_table in subnets:
                ec2.associate_route_table(
                    RouteTableId=ServiceCreation.route_table_creation.public_rtb,
                    SubnetId=associate_with_route_table,
                )
            print("Public route table of AZ ap-south-1a & ap-south-1b:  ",
                  ServiceCreation.route_table_creation.public_rtb)
            sleep(1)

            # Creating route table for private subnet-1a
            private_1a_route_table = ec2.create_route_table(VpcId=ServiceCreation.vpc_creation.vpc,
                                                            TagSpecifications=[
                                                                {
                                                                    'ResourceType': 'route-table',
                                                                    'Tags': [
                                                                        {
                                                                            'Key': 'Name',
                                                                            'Value': args.privatertb1a_tag
                                                                        },
                                                                    ]
                                                                },
                                                            ])

            ServiceCreation.route_table_creation.private_1a_rtb = private_1a_route_table[
                "RouteTable"]["RouteTableId"]
            print("Private route table for AZ ap-south-1a:  ",
                  ServiceCreation.route_table_creation.private_1a_rtb)

            sleep(1)

            # Creating route table for private subnet-1b
            private_1b_route_table = ec2.create_route_table(VpcId=ServiceCreation.vpc_creation.vpc,
                                                            TagSpecifications=[
                                                                {
                                                                    'ResourceType': 'route-table',
                                                                    'Tags': [
                                                                        {
                                                                            'Key': 'Name',
                                                                            'Value': args.privatertb1b_tag
                                                                        },
                                                                    ]
                                                                },
                                                            ])

            ServiceCreation.route_table_creation.private_1b_rtb = private_1b_route_table[
                "RouteTable"]["RouteTableId"]
            print("Private route table for AZ ap-south-1b:  ",
                  ServiceCreation.route_table_creation.private_1b_rtb)

            subnetids = [ServiceCreation.subnet_creation.subnet_id2,
                         ServiceCreation.subnet_creation.subnet_id4]
            routeIds = [ServiceCreation.route_table_creation.private_1a_rtb,
                        ServiceCreation.route_table_creation.private_1b_rtb]
            index = 0
            while index < len(routeIds) and index < len(subnetids):
                element = routeIds[index]
                element2 = subnetids[index]
                ec2.associate_route_table(
                    RouteTableId=element,
                    SubnetId=element2,
                )
                index += 1
        except ClientError as e:
            print(e)

        # Create VPC endpoint(S3)
    def vpc_endpoint_for_s3(self):
        try:
            create_endpoint_S3 = ec2.create_vpc_endpoint(
                VpcEndpointType='Gateway',
                VpcId=ServiceCreation.vpc_creation.vpc,
                ServiceName='com.amazonaws.ap-south-1.s3',
                RouteTableIds=[ServiceCreation.route_table_creation.private_1a_rtb,
                               ServiceCreation.route_table_creation.private_1b_rtb],
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc-endpoint',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': args.endpoint_tag
                            },
                        ]
                    },
                ]
            )
            s3endpoint = create_endpoint_S3['VpcEndpoint']['VpcEndpointId']
            print("Vpc endpoint:  ", s3endpoint)

            sleep(1)
        except ClientError as e:
            print(e)

        # Allocate Elastic I.P address
    def elastic_ip_creation(self):
        try:
            allocate_eip_address = ec2.allocate_address(
                Domain='vpc',
                TagSpecifications=[
                    {
                        'ResourceType': 'elastic-ip',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': args.eip_tag
                            },
                        ]
                    },
                ]
            )
            ServiceCreation.elastic_ip_creation.eip_allocationId = allocate_eip_address[
                'AllocationId']

            print("Elastic public I.P is:  ", allocate_eip_address['PublicIp'])
            sleep(1)
            print("Elastic I.P allocationID:  ",
                  ServiceCreation.elastic_ip_creation.eip_allocationId)

        except ClientError as e:
            print(e)

        # Create NAT gateway
    def nat_gateway_creation(self):
        try:
            response = ec2.create_nat_gateway(
                AllocationId=ServiceCreation.elastic_ip_creation.eip_allocationId,
                SubnetId=ServiceCreation.subnet_creation.subnet_id1,
                TagSpecifications=[
                    {
                        'ResourceType': 'natgateway',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': args.nat_tag
                            },
                        ]
                    },
                ],
                ConnectivityType=args.nattype
            )
            natgwid = response['NatGateway']['NatGatewayId']

            ec2.get_waiter('nat_gateway_available').wait(
                NatGatewayIds=[natgwid])

            print("NAT gatewayID:  ", natgwid)

            routeIds = [ServiceCreation.route_table_creation.private_1a_rtb,
                        ServiceCreation.route_table_creation.private_1b_rtb]
            index = 0
            while index < len(routeIds):
                element = routeIds[index]
                ec2.create_route(
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=natgwid,
                    RouteTableId=element
                )
                index += 1
        except ClientError as e:
            print(e)


class ServiceExecution(ServiceCreation):
    def __init__(self):
        print("Creating VPC to your AWS account...")
        self.vpc_creation()
        sleep(2)
        print("Creating and attaching Internet gateway to VPC...")
        self.create_internet_gateway()
        sleep(2)
        print(
            "Creating Public subnet and private subnet to choosen availability zone(s)...")
        self.subnet_creation()
        sleep(2)
        print(
            "Creating Route tables and creating associating route with internet gateway...")
        self.route_table_creation()
        sleep(2)
        print("Creating S3 endpoint...")
        self.vpc_endpoint_for_s3()
        sleep(2)
        print("Allocating Elastic I.P")
        self.elastic_ip_creation()
        sleep(1)
        sleep(1)
        print("Creating NAT gateway, this may take few minutes...")
        self.nat_gateway_creation()
        print("Associating Elastic I.P to NAT gateway")
        sleep(2)
        print("Thanks for using AWS service creation tools")


if __name__ == '__main__':
    ec2 = boto3.client('ec2')
    parser = argparse.ArgumentParser()
    parser.add_argument('--cidr', type=str, default='10.0.0.0/16',
                        help='Insert valid vpc i.p address, default is 10.0.0.0/16')

    parser.add_argument('--vpc_tag', type=str, default='Samyojaka_vpc',
                        help='Insert valid VPC name, default is Samyojaka_vpc')

    parser.add_argument('--ig_tag', type=str, default='Samyojaka_igw',
                        help='Insert valid internet gateway name, default is Samyojaka_igw')

    parser.add_argument('--subnetpublic1a_tag', type=str, default='Samyojaka_public_subnet_1a',
                        help='Insert valid subnet name, default is Samyojaka_public_subnet_1a')

    parser.add_argument('--subnetpublic1a_cidr', type=str, default='10.0.0.0/20',
                        help='Insert valid subnet ip, default is 10.0.0.0/20')

    parser.add_argument('--subnetprivate1a_tag', type=str, default='Samyojaka_private_subnet_1a',
                        help='Insert valid subnet name, default is Samyojaka_private_subnet_1a')

    parser.add_argument('--subnetprivate1a_cidr', type=str, default='10.0.128.0/20',
                        help='Insert valid subnet ip, default is 10.0.128.0/20')

    parser.add_argument('--subnetpublic1b_tag', type=str, default='Samyojaka_public_subnet_1b',
                        help='Insert valid subnet name, default is Samyojaka_public_subnet_1b')

    parser.add_argument('--subnetpublic1b_cidr', type=str, default='10.0.16.0/20',
                        help='Insert valid subnet ip, default is 10.0.16.0/20')

    parser.add_argument('--subnetprivate1b_tag', type=str, default='Samyojaka-private_subnet_1b',
                        help='Insert valid subnet name, default is Samyojaka-private_subnet_1b')

    parser.add_argument('--subnetprivate1b_cidr', type=str, default='10.0.144.0/20',
                        help='Insert valid subnet ip, default is 10.0.144.0/20')

    parser.add_argument('--publicrtb_tag', type=str, default='Samyojaka_public_rtb',
                        help='Insert valid route table name, default is Samyojaka_public_rtb')

    parser.add_argument('--privatertb1a_tag', type=str, default='Samyojaka_private-1a_rtb',
                        help='Insert valid route table name, default is Samyojaka_private-1a_rtb')

    parser.add_argument('--privatertb1b_tag', type=str, default='Samyojaka_private-1b_rtb',
                        help='Insert valid route table name, default is Samyojaka_private-1b_rtb')

    parser.add_argument('--endpoint_tag', type=str, default='Samyojaka_endpoint_S3',
                        help='Insert valid endpoint name, default is Samyojaka_endpoint_S3')

    parser.add_argument('--eip_tag', type=str, default='Samyojaka_E-I.P_address',
                        help='Insert valid Elastic I.P name, default is Samyojaka_E-I.P_address')

    parser.add_argument('--nat_tag', type=str, default='Samyojaka_nat_gw',
                        help='Insert valid NAT gateway name, default is Samyojaka_nat_gw')

    parser.add_argument('--nattype', type=str, default='public',
                        help='Insert valid NAT gateway connectivity type, default is public')

    args = parser.parse_args()
    sys.stdout.write(str(ServiceExecution()))



# # Creates VPC on AWS in logged account
# class ServiceCreation():
#     def vpc_creation(self):
#         try:    
#             create_vpc = ec2.create_vpc(
#                 CidrBlock='10.0.0.0/16',
#                 InstanceTenancy='default',
#                 TagSpecifications=[
#                     {
#                         'ResourceType': 'vpc',
#                         'Tags': [
#                             {
#                                 'Key': 'Name',
#                                 'Value': 'Samyojaka2_test_vpc'
#                             },
#                         ]
#                     },
#                 ]
#             )
#             ServiceCreation.vpc_creation.vpc = create_vpc["Vpc"]["VpcId"]

#             print("VPC ID:  ", ServiceCreation.vpc_creation.vpc)

#             # Enables DNS hostnames in VPC
#             ec2.modify_vpc_attribute(
#                 EnableDnsHostnames={
#                     'Value': True
#                 },
#                 VpcId=ServiceCreation.vpc_creation.vpc
#             )

#             # Enables DNS Resolution
#             ec2.modify_vpc_attribute(
#                 EnableDnsSupport={
#                     'Value': True
#                 },
#                 VpcId=ServiceCreation.vpc_creation.vpc        
#                 )
#         except ClientError as e:
#             print(e)
#             sys.exit()
#     def create_internet_gateway(self):
#         # Create and Attach the Internet Gateway
#         ig = ec2.create_internet_gateway(TagSpecifications=[
#             {
#                 'ResourceType': 'internet-gateway',
#                 'Tags': [
#                     {
#                         'Key': 'Name',
#                         'Value': 'Samyojaka2_test-igw'
#                     },
#                 ]
#             },
#         ],)
#         ServiceCreation.create_internet_gateway.internet_gateway = ig["InternetGateway"]["InternetGatewayId"]
#         print("Attaching IGW to VPC...")

#         ec2.attach_internet_gateway(InternetGatewayId=ServiceCreation.create_internet_gateway.internet_gateway, VpcId=ServiceCreation.vpc_creation.vpc)
#         print("Internet GatewayID:  ", ServiceCreation.create_internet_gateway.internet_gateway)


#         #------------------ creating multiple subnets----------------------#
#     def subnet_creation(self):
#         # Create a public Subnet in 1a(AZ)
#         try:
#             public_subnet_1a = ec2.create_subnet(TagSpecifications=[
#                 {
#                     'ResourceType': 'subnet',
#                     'Tags': [
#                         {
#                             'Key': 'Name',
#                             'Value': 'Samyojaka2_test-public_subnet-1a'
#                         },
#                     ]
#                 },
#             ],
#                 CidrBlock='10.0.0.0/20',
#                 AvailabilityZone='ap-south-1a',
#                 VpcId=ServiceCreation.vpc_creation.vpc
#             )
#             ServiceCreation.subnet_creation.subnet_id1 = (public_subnet_1a["Subnet"]["SubnetId"])
#             print("Public subnet on AZ ap-south-1a:  ", ServiceCreation.subnet_creation.subnet_id1)


#             # Create a private Subnet in 1a(AZ)
#             private_subnet_1a = ec2.create_subnet(TagSpecifications=[
#                 {
#                     'ResourceType': 'subnet',
#                     'Tags': [
#                         {
#                             'Key': 'Name',
#                             'Value': 'Samyojaka2_test-private_subnet-1a'
#                         },
#                     ]
#                 },
#             ],
#                 CidrBlock='10.0.128.0/20',
#                 AvailabilityZone='ap-south-1a',
#                 VpcId=ServiceCreation.vpc_creation.vpc
#             )
#             ServiceCreation.subnet_creation.subnet_id2 = (private_subnet_1a["Subnet"]["SubnetId"])
#             print("Private Subnet on AZ ap-south-1a:  ", ServiceCreation.subnet_creation.subnet_id2)

#             # Create a public Subnet in 1b(AZ)
#             public_subnet_1b = ec2.create_subnet(TagSpecifications=[
#                 {
#                     'ResourceType': 'subnet',
#                     'Tags': [
#                         {
#                             'Key': 'Name',
#                             'Value': 'Samyojaka2_test-public_subnet-1b'
#                         },
#                     ]
#                 },
#             ],
#                 CidrBlock='10.0.16.0/20',
#                 AvailabilityZone='ap-south-1b',
#                 VpcId=ServiceCreation.vpc_creation.vpc
#             )
#             ServiceCreation.subnet_creation.subnet_id3 = (public_subnet_1b["Subnet"]["SubnetId"])
#             print("Public Subnet on AZ ap-south-1b:  ", ServiceCreation.subnet_creation.subnet_id3)

#             # Create a private Subnet in 1b(AZ)
#             private_subnet_1b = ec2.create_subnet(TagSpecifications=[
#                 {
#                     'ResourceType': 'subnet',
#                     'Tags': [
#                         {
#                             'Key': 'Name',
#                             'Value': 'Samyojaka2_test-private_subnet-1b'
#                         },
#                     ]
#                 },
#             ],
#                 CidrBlock='10.0.144.0/20',
#                 AvailabilityZone='ap-south-1b',
#                 VpcId=ServiceCreation.vpc_creation.vpc
#             )
#             ServiceCreation.subnet_creation.subnet_id4 = (private_subnet_1b["Subnet"]["SubnetId"])
#             print("Private subnet on AZ ap-south-1b:  ", ServiceCreation.subnet_creation.subnet_id4)
#             sleep(1)
#         except ClientError as e:
#             print(e)
#         # Create a route table and a public route to Internet Gateway
#     def route_table_creation(self):
#         # Creating route table for public subnets
#         try:
#             public_route_table = ec2.create_route_table(VpcId=ServiceCreation.vpc_creation.vpc,
#                                                         TagSpecifications=[
#                                                             {
#                                                                 'ResourceType': 'route-table',
#                                                                 'Tags': [
#                                                                     {
#                                                                         'Key': 'Name',
#                                                                         'Value': 'Samyojaka2_test_public_rtb'
#                                                                     },
#                                                                 ]
#                                                             },
#                                                         ])

#             ServiceCreation.route_table_creation.public_rtb = public_route_table["RouteTable"]["RouteTableId"]

#             # creates route to attach Internet gateway to VPC
#             ec2.create_route(
#                 DestinationCidrBlock='0.0.0.0/0',
#                 GatewayId=ServiceCreation.create_internet_gateway.internet_gateway,
#                 RouteTableId=ServiceCreation.route_table_creation.public_rtb
#             )

#             # Associates public route table with public subnets
#             subnets =[ServiceCreation.subnet_creation.subnet_id1,ServiceCreation.subnet_creation.subnet_id3]
#             for associate_with_route_table in subnets:
#                 ec2.associate_route_table(
#                     RouteTableId=ServiceCreation.route_table_creation.public_rtb,
#                     SubnetId=associate_with_route_table,
#                 )
#             print("Public route table of AZ ap-south-1a & ap-south-1b:  ", ServiceCreation.route_table_creation.public_rtb)
#             sleep(1)

#             # Creating route table for private subnet-1a
#             private_1a_route_table = ec2.create_route_table(VpcId=ServiceCreation.vpc_creation.vpc,
#                                                             TagSpecifications=[
#                                                                 {
#                                                                     'ResourceType': 'route-table',
#                                                                     'Tags': [
#                                                                         {
#                                                                             'Key': 'Name',
#                                                                             'Value': 'Samyojaka2_test_private-1a_rtb'
#                                                                         },
#                                                                     ]
#                                                                 },
#                                                             ])

#             ServiceCreation.route_table_creation.private_1a_rtb = private_1a_route_table["RouteTable"]["RouteTableId"]
#             print("Private route table for AZ ap-south-1a:  ", ServiceCreation.route_table_creation.private_1a_rtb)

#             sleep(1)

#             # Creating route table for private subnet-1b
#             private_1b_route_table = ec2.create_route_table(VpcId=ServiceCreation.vpc_creation.vpc,
#                                                             TagSpecifications=[
#                                                                 {
#                                                                     'ResourceType': 'route-table',
#                                                                     'Tags': [
#                                                                         {
#                                                                             'Key': 'Name',
#                                                                             'Value': 'Samyojaka2_test_private-1b_rtb'
#                                                                         },
#                                                                     ]
#                                                                 },
#                                                             ])

#             ServiceCreation.route_table_creation.private_1b_rtb = private_1b_route_table["RouteTable"]["RouteTableId"]
#             print("Private route table for AZ ap-south-1b:  ", ServiceCreation.route_table_creation.private_1b_rtb)


#             subnetids = [ServiceCreation.subnet_creation.subnet_id2,ServiceCreation.subnet_creation.subnet_id4]
#             routeIds = [ServiceCreation.route_table_creation.private_1a_rtb,ServiceCreation.route_table_creation.private_1b_rtb]
#             index = 0
#             while index < len(routeIds) and index < len(subnetids):
#                 element = routeIds[index]
#                 element2 = subnetids[index]           
#                 ec2.associate_route_table(
#                     RouteTableId=element,
#                     SubnetId=element2,
#                 )
#                 index += 1
#         except ClientError as e:
#             print(e)

#         # Create VPC endpoint(S3)
#     def vpc_endpoint_for_s3(self):
#         try:
#             create_endpoint_S3 = ec2.create_vpc_endpoint(
#                 VpcEndpointType='Gateway',
#                 VpcId=ServiceCreation.vpc_creation.vpc,
#                 ServiceName='com.amazonaws.ap-south-1.s3',
#                 RouteTableIds=[ServiceCreation.route_table_creation.private_1a_rtb,ServiceCreation.route_table_creation.private_1b_rtb],
#                 TagSpecifications=[
#                     {
#                         'ResourceType': 'vpc-endpoint',
#                         'Tags': [
#                             {
#                                 'Key': 'Name',
#                                 'Value': 'Samyojaka2_test_endpoint_S3'
#                             },
#                         ]
#                     },
#                 ]
#             )
#             s3endpoint = create_endpoint_S3['VpcEndpoint']['VpcEndpointId']
#             print("Vpc endpoint:  ", s3endpoint)


#             sleep(1)
#         except ClientError as e:
#             print(e)

#         # Allocate Elastic I.P address
#     def elastic_ip_creation(self):
#         try:
#             allocate_eip_address = ec2.allocate_address(
#                 Domain='vpc',
#                 TagSpecifications=[
#                     {
#                         'ResourceType': 'elastic-ip',
#                         'Tags': [
#                             {
#                                 'Key': 'Name',
#                                 'Value': 'Samyojaka2_test-E-I.P_address'
#                             },
#                         ]
#                     },
#                 ]
#             )
#             ServiceCreation.elastic_ip_creation.eip_allocationId = allocate_eip_address['AllocationId']

#             print("Elastic public I.P is:  ", allocate_eip_address['PublicIp'])
#             sleep(1)
#             print("Elastic I.P allocationID:  ", ServiceCreation.elastic_ip_creation.eip_allocationId)
            
#         except ClientError as e:
#             print(e)

#         # Create NAT gateway
#     def nat_gateway_creation(self):
#         try:
#             response = ec2.create_nat_gateway(
#                 AllocationId=ServiceCreation.elastic_ip_creation.eip_allocationId,
#                 SubnetId=ServiceCreation.subnet_creation.subnet_id1,
#                 TagSpecifications=[
#                     {
#                         'ResourceType': 'natgateway',
#                         'Tags': [
#                             {
#                                 'Key': 'Name',
#                                 'Value': 'Samyojaka2_test_nat_gw'
#                             },
#                         ]
#                     },
#                 ],
#                 ConnectivityType='public'
#             )
#             natgwid = response['NatGateway']['NatGatewayId']

#             ec2.get_waiter('nat_gateway_available').wait(NatGatewayIds=[natgwid])

#             print("NAT gatewayID:  ", natgwid)

#             routeIds = [ServiceCreation.route_table_creation.private_1a_rtb, ServiceCreation.route_table_creation.private_1b_rtb]
#             index = 0
#             while index < len(routeIds):
#                 element = routeIds[index]
#                 ec2.create_route(
#                     DestinationCidrBlock='0.0.0.0/0',
#                     GatewayId=natgwid,
#                     RouteTableId=element
#                 )
#                 index += 1
#         except ClientError as e:
#             print(e)

# class ServiceExecution(ServiceCreation):
#     def __init__(self):
#         print("Creating VPC to your AWS account...")
#         self.vpc_creation()
#         sleep(2)
#         print("Creating and attaching Internet gateway to VPC...")
#         self.create_internet_gateway()
#         sleep(2)
#         print("Creating Public subnet and private subnet to choosen availability zone(s)...")
#         self.subnet_creation()
#         sleep(2)
#         print("Creating Route tables and creating associating route with internet gateway...")
#         self.route_table_creation()
#         sleep(2)
#         print("Creating S3 endpoint...")
#         self.vpc_endpoint_for_s3()
#         sleep(2)
#         print("Allocating Elastic I.P")
#         self.elastic_ip_creation()
#         sleep(1)
#         sleep(1)
#         print("Creating NAT gateway, this may take few minutes...")
#         self.nat_gateway_creation()
#         print("Associating Elastic I.P to NAT gateway")
#         sleep(2)
#         print("Thanks for using AWS service creation tools")

# if __name__ == '__main__':
#     ec2 = boto3.client('ec2')
#     ServiceExecution()
