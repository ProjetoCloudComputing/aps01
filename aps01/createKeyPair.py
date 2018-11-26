import boto3
import os

def checkIfKeyPairExists(ec2, newKeyName):
    response = ec2.describe_key_pairs()
    for key in response['KeyPairs']:
        if key['KeyName'] == newKeyName:
            print("Key found")
            return True
    return False

def deleteKeyPair(ec2, keyPairName):
    response = ec2.describe_key_pairs()
    for key in response['KeyPairs']:
        if key['KeyName'] == keyPairName:
            print("Existent key, deleting...")
            deleted = ec2.delete_key_pair(KeyName=keyPairName)
            print("Deleted")       
            return True
    return False

def createPemFile(created, newKeyName):
    try:
        os.remove(f"{newKeyName}.pem")
        
    except:
        print("File .pem Doesn't exist yet")

    file = open(f"{newKeyName}.pem", 'w+')
    file.write(created['KeyMaterial'])
    file.close()
    os.chmod(f"{newKeyName}.pem", 0o400)

def createKeyPair(ec2, keyPairName):
    if(checkIfKeyPairExists(ec2, keyPairName)):
        print("Key Pair already exists, won't delete")
    else:
        print("Creating KeyPair...")
        ec2.create_key_pair(KeyName=keyPairName)
        createPemFile(keyPairName, keyPairName)

    return keyPairName



# createBotoKeyPair(keyName)