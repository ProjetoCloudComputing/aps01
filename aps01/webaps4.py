from flask import Flask, redirect, url_for, request
from pprint import pprint
import queue
import boto3
import random
from threading import Thread
from queue import Queue
import time
import createInstance
import requests
import sys

args = sys.argv
try:
    ACCESS_KEY = args[1]
    SECRET_KEY = args[2]
    KEY_PAIR_NAME = args[3]
    SECURITY_GROUP_NAME = args[4]
    REGION_NAME = args[5]
except:
    print("Wrong args")

ec2 = boto3.client(
                'ec2', 
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name=REGION_NAME)


ec2_resource = boto3.resource(
                'ec2', 
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name=REGION_NAME)


def checkInstancesRunning(numOfActives=3):
    global instancesRunning
    while True:
        print("-------------")

        #Healthcheck for each instance
        instancesToTerminate = []
        if (len(list(instancesRunning.items())) > 0):
            instancesToTerminate = []
            for instance_id, ip in list(instancesRunning.items()):
                try:
                    req = requests.get(url=f"http://{ip}:5000/healthcheck", timeout=5)               
                    if(req.text == "200"):
                        print(f"Instance {instance_id} is ok")
                    else:
                        instancesToTerminate.append(instance_id)
                except:
                    print("Timeout")
                    instancesToTerminate.append(instance_id)
        
        #Terminate all instances that doesnt respond to healthcheck
        if (len(instancesToTerminate) > 0):

            #deleting from current dictionary
            for inst in instancesToTerminate:
                del instancesRunning[inst]
                
            print("Terminating instances")
            print(f"deleting {len(instancesToTerminate)} instance(s)")
            ec2_resource.instances.filter(InstanceIds=instancesToTerminate).terminate()
            print("Wait for them to be terminated")
            #Wait for them to be terminated
            waiter = ec2.get_waiter("instance_terminated")
            waiter.wait(
                InstanceIds=instancesToTerminate,
                WaiterConfig={
                    'Delay': 15,
                    'MaxAttempts': 40
                }
            )
            

        #Checking if we need to create more instances
        if(len(instancesRunning.keys()) != numOfActives):
            numToUpdate = numOfActives - len(instancesRunning.keys()) #Number of instances that are missing
            print(f"Creating {numToUpdate} instance(s), just {len(instancesRunning.keys())} are running, we need {numOfActives}")
            newInstances = createInstance.createNewInstances(ec2, ec2_resource, numToUpdate, KEY_PAIR_NAME, SECURITY_GROUP_NAME)
            testing = getInstancesRunning()
            testing_instances = newInstances
            #wait for instances servers to be ready
            while (len(testing_instances) > 0):
                for instance in testing_instances:
                    try:
                        print("Link: ", testing[instance])
                        req = requests.get(url=f"http://{testing[instance]}:5000/healthcheck", timeout=5)
                        print(req)               
                        if(req.text == "200"):
                            print(f"Instance {instance} is ready")
                            testing_instances.remove(instance)
                    except:
                        print(f"{instance} is not ready yet")
        print("-------------")
        instancesRunning = getInstancesRunning()
        time.sleep(2)

def getInstancesRunning():
    get_instances = {}
    response = ec2.describe_instances()
    for group in response["Reservations"]:
        for instance in group["Instances"]:
            try:
                key = instance["Tags"][0]["Key"]
                value = instance["Tags"][0]["Value"]
                state = instance["State"]["Name"] 
                instanceId = instance["InstanceId"]
                if(key == "Owner" and value == "Raphael"):
                    if (state == "running"):
                        publicIp = instance["NetworkInterfaces"][0]["Association"]["PublicIp"]
                        get_instances[instanceId] = publicIp
            except:
                print("Not my instances, pass")

    # print("Instances Running: ")                
    # pprint(get_instances)
    return get_instances

app = Flask(__name__)
instancesRunning = getInstancesRunning() #Instances dictionary, key: instanceId, value: public ipv4

checkInstancesStatus = Thread(target=checkInstancesRunning,args=[3])
checkInstancesStatus.start()



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'PUT', 'DELETE', 'POST'])
def catch_all(path):
    print(path)
    if(path == "loadbalancer"):
        return "200"
    if(len(list(instancesRunning.items())) > 0):
        pprint(instancesRunning)
        _, randomIp = random.choice(list(instancesRunning.items()))
        return redirect(f"http://{randomIp}:5000/{path}")
        return f"Running Instances, there's no instances running yet"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)