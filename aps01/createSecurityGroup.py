import boto3
from botocore.exceptions import ClientError
from pprint import pprint

def deleteSecurityGroup(ec2, name):
    try:
        response = ec2.delete_security_group(GroupName=name)
        print('Security Group Deleted')
    except ClientError as e:
        print("Security Group Doesn't exist or an instance is using it.")

def createSG(ec2, name):
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    try:
        response = ec2.create_security_group(GroupName=name,
                                             Description='SG created with boto3 API',
                                             VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 5000,
                 'ToPort': 5000,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])

        return security_group_id

    except ClientError as e:
        print(e)
        

def checkIfSecurityGroupExists(ec2, name):
    response = ec2.describe_security_groups()
    for sg in response["SecurityGroups"]:
        if (sg["GroupName"] == name):
            return True, sg["GroupId"]
    return False, 0


def create(ec2, sg_name):
    exists, groupId = checkIfSecurityGroupExists(ec2, sg_name)
    if(exists):
        print("Security group already exists")
        return groupId
    else:
        print("Creating...")
        return createSG(ec2, sg_name)

# create(ec2, sg_name)