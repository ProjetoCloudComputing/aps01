from flask import Flask, redirect, url_for, request
from pprint import pprint
import boto3
import random
from threading import Thread
import time
import createInstance
import requests
import sys

args = sys.argv
try:
    ACCESS_KEY = args[1]
    SECRET_KEY = args[2]
    REGION_NAME = args[3]
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


def checkInstancesRunning(currentInstances, numOfActives=3):
    while True:
        print("-------------")

        #Healthcheck for each instance
        instancesToTerminate = []
        if (len(list(currentInstances.items())) > 0):
            instancesToTerminate = []
            for instance_id, ip in list(currentInstances.items()):
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
                del currentInstances[inst]
                
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
        if(len(currentInstances.keys()) != numOfActives):
            numToUpdate = numOfActives - len(currentInstances.keys()) #Number of instances that are missing
            print(f"Creating {numToUpdate} instance(s), just {len(currentInstances.keys())} are running, we need {numOfActives}")
            newInstances = createInstance.createNewInstances(ec2, numToUpdate)
            testing = getIntancesRunning()
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

            currentInstances = getIntancesRunning()
        print("-------------")
        time.sleep(2)

def getIntancesRunning():
    instancesRunning = {}
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
                        instancesRunning[instanceId] = publicIp
            except:
                print("Not my instances, pass")

    print("Instances Running: ")                
    pprint(instancesRunning)
    return instancesRunning

app = Flask(__name__)

instancesRunning = getIntancesRunning() #Instances dictionary, key: instanceId, value: public ipv4

checkInstancesStatus = Thread(target=checkInstancesRunning,args=[instancesRunning, 3])
checkInstancesStatus.start()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'PUT', 'DELETE', 'POST'])
def catch_all(path):
    print(path)
    if(path == "loadbalancer"):
        return "200"
    _, randomIp = random.choice(list(instancesRunning.items()))
    print(randomIp)
    return redirect(f"http://{randomIp}:5000/{path}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)