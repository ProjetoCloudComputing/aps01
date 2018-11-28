#Run this file to upload load balancer to aws and prepare all the enviroment
from pprint import pprint
import boto3
import random
from threading import Thread
import time
import createInstance
import requests
import sys
import json
import createKeyPair, createSecurityGroup

try:
    with open('credentials.json') as f:
        data = json.load(f)
        ACCESS_KEY = data["ACCESS_KEY"]
        SECRET_KEY = data["SECRET_KEY"]
        keyPairName = data["KeyPairName"]
        securityGroupName = data["SecurityGroupName"]
        regionName = data["RegionName"]
except:
    print("Wrong args, review your credentials file")

ec2 = boto3.client(
                'ec2', 
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name = regionName)

ec2_resource = boto3.resource(
                'ec2', 
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name = regionName)

#Image ID
ubuntu18 = "ami-0ac019f4fcb7cb7e6"

#Creating Keypair and .pem file
keyName = createKeyPair.createKeyPair(ec2, keyPairName)

#Creating security group
security_group_id = createSecurityGroup.create(ec2, securityGroupName)

instance_res = ec2_resource.create_instances(
    ImageId=ubuntu18,
    InstanceType='t2.micro',
    KeyName=keyName,
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[
        security_group_id,
    ],
    SecurityGroups=[
        securityGroupName,
    ],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Owner',
                    'Value': 'LoadBalancer'
                },
            ]
        },
    ],
    UserData=
            f"""#!/bin/bash
            git clone https://github.com/ProjetoCloudComputing/aps01.git
            cd aps01
            cd aps01
            chmod +x install.sh
            ./install.sh
            python3 webaps4.py {ACCESS_KEY} {SECRET_KEY} {keyPairName} {securityGroupName} {regionName}"""
)
print("Load Balancer created, waiting for request being ready")
waiter = ec2.get_waiter('instance_exists')
waiter.wait(
    InstanceIds=[instance_res[0].id],
    WaiterConfig={
        'Delay': 15,
        'MaxAttempts': 40
    }
)

print("Request ready, waiting for instance being ready")
waiter = ec2.get_waiter('instance_running')
waiter.wait(
    InstanceIds=[instance_res[0].id],
    WaiterConfig={
        'Delay': 15,
        'MaxAttempts': 40
    }
)

#finding Load Balancer
print("Finding Load balancer, instance id: ", instance_res[0].id)
publicIp = None
response = ec2.describe_instances()
for group in response["Reservations"]:
    for instance in group["Instances"]:
        instanceId = instance["InstanceId"]
        print("Instance id: ", instanceId)
        if(instanceId == instance_res[0].id):
            publicIp = instance["NetworkInterfaces"][0]["Association"]["PublicIp"]
            print("Found load balander in aws: ", publicIp, instanceId)
            break
            
if(publicIp):
    #Waiting for load balancer is ready
    print("Waiting for load balancer is ready")
    while True:
        try:
            req = requests.get(url=f"http://{publicIp}:5000/loadbalancer", timeout=5)               
            if(req.text == "200"):
                print(f"Load Balancer is ready")
                break
        except:
            print("Load Balancer is not ready yet")

    print(f"Load Balancer Running on IP: {publicIp}, ready for use")
else:
    print("Couldn't find lb")
