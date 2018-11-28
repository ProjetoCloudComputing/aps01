import boto3
from pprint import pprint

ec2 = boto3.client('ec2')
# instancesToTerminate = []
test = "i-044f245c38471907f"
print("Finding Load balancer, instance id: ", instance)
publicIp = None
response = ec2.describe_instances()
# pprint(response)
for group in response["Reservations"]:
    for instance in group["Instances"]:
        instanceId = instance["InstanceId"]
        print("Instance id: ", instanceId)
        print(instanceId == instance)
        if(instanceId == test):
            publicIp = instance["NetworkInterfaces"][0]["Association"]["PublicIp"]
            print("Found load balander in aws: ", publicIp, instanceId)

# pprint(response)