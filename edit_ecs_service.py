# cpu_size, memory_size,
# , 1024, 1024
from time import sleep
import boto3

class ECS():
    def create_cluster(self, clusterName):
        self.clusterName = clusterName

        response = client.create_cluster(clusterName=clusterName)
        global cluster_Name
        cluster_Name = response['cluster']['clusterName']
        # print(cluster_Name)
        print(f"Cluster successfully created on AWS service named as :  {cluster_Name}")
        sleep(1)

    def register_task_definition(self, taskdfn_name, container_name, container_port_number,
                                 host_port_number, protocol_type, taskdfn_cpu_memory, taskdfn_memory):
        self.taskdfn_name = taskdfn_name
        self.container_name = container_name
        self.container_port_number = container_port_number
        self.host_port_number = host_port_number
        self.protocol_type = protocol_type
        self.taskdfn_cpu_memory = taskdfn_cpu_memory
        self.taskdfn_memory = taskdfn_memory

        response = client.register_task_definition(
            family=taskdfn_name,
            executionRoleArn=f'arn:aws:iam::{aws_account_id}:role/ecsTaskExecutionRole',
            networkMode='awsvpc',
            containerDefinitions=[
                {
                    'name': container_name,
                    'image': f'{aws_account_id}.dkr.ecr.ap-south-1.amazonaws.com/{repo_name}:{repo_tag}',
                    # 'cpu': cpu_size,
                    # 'memory': memory_size,
                    'portMappings': [
                        {
                            'containerPort': container_port_number,
                            'hostPort': host_port_number,
                            'protocol': protocol_type,
                        },
                    ],
                    'essential': True,
                    'environment': [],
                    'mountPoints': [],
                    'volumesFrom': [],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            "awslogs-group": f"/ecs/{taskdfn_name}",
                            "awslogs-region": "ap-south-1",
                            "awslogs-stream-prefix": "ecs",
                            'awslogs-create-group': 'true'
                        }
                    }
                },
            ],
            requiresCompatibilities=[
                'FARGATE',
            ],
            cpu=taskdfn_cpu_memory,
            memory=taskdfn_memory,
            tags=[
                {
                    'key': 'ecs:taskDefinition:createdFromAPI',
                    'value': 'Samyojaka-test-service-creation'
                },
            ],
            runtimePlatform={
                'cpuArchitecture': 'X86_64',
                'operatingSystemFamily': 'Linux'
            }
        )
        global taskdefinition_arn
        taskdefinition_arn = response['taskDefinition']['taskDefinitionArn']
        print(
            f"Task definition successfully created with task Definition Arn:  {taskdefinition_arn}")
    
        sleep(1)
        # print(json.dumps(response, indent=4, default=str))

    def register_service_with_ecs(self,service_name,subnet1,subnet2,service_service_group):
        self.service_name = service_name
        self.subnet1 = subnet1
        self.subnet2 = subnet2
        self.service_service_group = service_service_group

        response = client.create_service(
            cluster=cluster_Name,
            serviceName=service_name,
            taskDefinition=taskdefinition_arn,
                # loadBalancers=[
                #     {
                #         'targetGroupArn': 'string',
                #         'loadBalancerName': 'string',
                #         'containerName': 'string',
                #         'containerPort': 123
                #     },
                # ],
            # serviceRegistries=[
            #     {
            #         'registryArn': 'string',
            #         'port': 123,
            #         'containerName': 'string',
            #         'containerPort': 123
            #     },
            # ],
            desiredCount=1,
            # clientToken='string',
            launchType= 'FARGATE',
            # capacityProviderStrategy=[
            #     {
            #         'capacityProvider': 'string',
            #         'weight': 123,
            #         'base': 123
            #     },
            # ],
            platformVersion='LATEST',
            # role='string',
            deploymentConfiguration={
                'deploymentCircuitBreaker': {
                    'enable': False,
                    'rollback': False
                },
                'maximumPercent': 200,
                'minimumHealthyPercent': 100
            },
            # placementConstraints=[
            #     {
            #         'type': 'distinctInstance'|'memberOf',
            #         'expression': 'string'
            #     },
            # ],
            # placementStrategy=[
            #     {
            #         'type': 'random'|'spread'|'binpack',
            #         'field': 'string'
            #     },
            # ],
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        subnet1,
                        subnet2
                    ],
                    'securityGroups': [
                        service_service_group,
                    ],
                    'assignPublicIp': 'ENABLED'
                }
            },
            # healthCheckGracePeriodSeconds=123,
            schedulingStrategy='REPLICA',
            deploymentController={
                'type': 'ECS'
            },
            tags=[
                {
                    'key': 'Name',
                    'value': 'Samyojaka1-test-service-creation'
                },
            ],
            # enableECSManagedTags=True|False,
            propagateTags='NONE',
            # enableExecuteCommand=True|False
        )
        # print(json.dumps(response, indent=4, default=str))


class AwsEcs(ECS):
    def __init__(self):
        print("Initiating Cluster creation...")
        sleep(1)
        self.create_cluster("Samyojaka-New-service")

        print("Registering task definition...")
        sleep(1)

        self.register_task_definition(
            "Samyojaka-software", "Samyojaka-container", 8000, 8000, 'tcp', '1 vCPU', '2GB')
        sleep(5)
        print("Registering Service on defined cluster...")
        sleep(1)
        self.register_service_with_ecs('Samyojaka1-test-service','subnet-083c9c0f5369bcf0e	','subnet-0ecd709b1501a86f4','sg-00fd582e6d2593a5b')

        sleep(2)
        print("Please wait we are running task...")

        sleep(5)
        print("Thanks for using the service")


if __name__ == "__main__":
    client = boto3.client("ecs", region_name="ap-south-1")
    aws_account_id = 886125330179
    repo_name = "new_repo"
    repo_tag = "latest"
    call_service = AwsEcs()
