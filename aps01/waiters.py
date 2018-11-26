import boto3

ec2 = boto3.client('ec2')

waiter = ec2.get_waiter('instance_running')
waiter.wait(
    # instanceIds=instancesToTerminate,
    Filters=[
        {
            'Name': 'tag:Owner',
            'Values': ['Raphael']
        },
    ],
    WaiterConfig={
        'Delay': 5,
        'MaxAttempts': 18
    }
)
# waiter.wait(
#     Filters=[
#         {
#             'Name': 'string',
#             'Values': [
#                 'string',
#             ]
#         },
#     ],
#     InstanceIds=[
#         'string',
#     ],
#     DryRun=True|False,
#     MaxResults=123,
#     NextToken='string',
#     WaiterConfig={
#         'Delay': 123,
#         'MaxAttempts': 123
#     }
# )

