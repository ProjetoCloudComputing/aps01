import boto3
from pprint import pprint

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
# instancesToTerminate = []
for group in response["Reservations"]:
    for instance in group["Instances"]:
        try:
            key = instance["Tags"][0]["Key"]
            value = instance["Tags"][0]["Value"]
            state = instance["State"]["Name"] 
            instanceId = instance["InstanceId"]
            if(key == "Owner" and value == "Raphael"):
                if (state == "running"):
        except:
            print("instances has no tag, pass")

# pprint(response)