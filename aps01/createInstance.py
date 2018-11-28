#bloco de notas
#check state 'State': {'Code': 16, 'Name': 'running'}
#Access Instances: response["Reservations"][0]["Instances"]
#terminanting instances ec2.instances.filter(InstanceIds=ids).terminate()
import createKeyPair, createSecurityGroup
import boto3
from pprint import pprint
import time

#Image ID
ubuntu18 = "ami-0ac019f4fcb7cb7e6"

def createNewInstances(ec2_client, ec2_resource, numOfInstances, keyPairName, sg_name):
    #Creating Keypair and .pem file
    keyName = createKeyPair.createKeyPair(ec2_client, keyPairName)

    #Creating security group
    security_group_id = createSecurityGroup.create(ec2_client, sg_name)

    instance = ec2_resource.create_instances(
        ImageId=ubuntu18,
        InstanceType='t2.micro',
        KeyName=keyName,
        MaxCount=numOfInstances,
        MinCount=numOfInstances,
        SecurityGroupIds=[
            security_group_id,
        ],
        SecurityGroups=[
            sg_name,
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Owner',
                        'Value': 'Raphael'
                    },
                ]
            },
        ],
        UserData=
                """#!/bin/bash
                git clone https://github.com/ProjetoCloudComputing/aps01.git
                cd aps01
                cd aps01
                chmod +x install.sh
                ./install.sh
                python3 firebaseWebServer.py"""

    )
    newInstancesIds = []
    for i in instance:
        newInstancesIds.append(i.id)

    print("List of new instances: ", newInstancesIds)        

    print("Instance created, waiting for request recognized by amazon")
    waiter = ec2_client.get_waiter('instance_exists')
    waiter.wait(
        InstanceIds=newInstancesIds,
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 40
        }
    )

    print("Request ready, waiting for instance being ready")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(
        InstanceIds=newInstancesIds,
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 40
        }
    )

    print("Done")
    return newInstancesIds

def checkIfExistsAndDeleteAll():
    response = ec2_client.describe_instances()
    instancesToTerminate = []
    for group in response["Reservations"]:
        for instance in group["Instances"]:
            key = instance["Tags"][0]["Key"]
            value = instance["Tags"][0]["Value"]
            state = instance["State"]["Name"] 
            instanceId = instance["InstanceId"]
            if(key == "Owner" and value == "Raphael"):
                if(state == 'running' or state == 'stopped'):
                    instancesToTerminate.append(instanceId)

    #TERMINATE THEM ALL
    if(len(instancesToTerminate) > 0):
        print(f"{len(instancesToTerminate)} Owner: Raphael found, deleting all and waiting...")
        ec2_resource.instances.filter(InstanceIds=instancesToTerminate).terminate()
        waitForInstanceStatus('instance_terminated')

    else:
        pprint("No Owner: Raphael instances Running")



def waitForInstanceStatus(status):
    # accetable status: ['instance_running', 'instance_terminated', 'instance_stopped', 'instance_exists']
    waiter = ec2_client.get_waiter(status)
    waiter.wait(
        Filters=[
            {
                'Name': 'tag:Owner',
                'Values': ['Raphael']
            },
        ],
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 40
        }
        #Wait for 600 seconds
    )
    return True

# def create(instances=3):
#     checkIfExistsAndDelete()
#     newInstanceId = createNewInstance(numOfInstances=instances)
#     # executeCommands(newInstanceId)

# create()


#AWS CONFIG FILE https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#aws-config-file