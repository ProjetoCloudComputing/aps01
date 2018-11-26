import boto3
from pprint import pprint

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
# instancesToTerminate = []
# for group in response["Reservations"]:
#     for instance in group["Instances"]:
#         pprint(instance)
        # # pprint(instance)
        # key = instance["Tags"][0]["Key"]
        # value = instance["Tags"][0]["Value"]
        # state = instance["State"]["Name"] 
        # instanceId = instance["InstanceId"]
        # if(key == "Owner" and value == "Raphael"):
        #     if (state == "running"):
        #         publicIp = instance["NetworkInterfaces"][0]["Association"]["PublicIp"]
        #         print("instance: ", key, value, state, instanceId, publicIp)

response = ec2.describe_instance_status(
    InstanceIds=[
        'i-0027a5aacc43cba6b',
    ],
)
pprint(response)