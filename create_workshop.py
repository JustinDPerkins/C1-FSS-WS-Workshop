import argparse
import os.path
import time
import logging
import boto3
import json
from botocore.exceptions import ClientError
'''
Trend Micro Seller workshop to help better understand CloudOne Workload and File Storage Security.
For each workshop user this script will create 1. AWS User(console access) 2. S3 bucket(specific bucket console access) 3. EC2 t2.medium with KP and iam role(rdp client/decrypt pwd)
Workshop User needs rights to deploy FSS stacks(tm_user_workshop policy)
User needs own s3 bucket to deploy FSS to.
User need own EC2 w/ own keypair to deploy Workload Security
Ec2 needs role attached to talk to S3(1 ec2 to 1 bucket).

----Naming conventions----
Iam-User-Policy: tm_user_workshop_user                                             Iam-role: <name>_ec2_assume_role_workshop
Iam-User: <name>(from file read)   ex. (obi-wan)                                   Iam-Role-Policy: <name>_tm_workshop_ec2_rolepolicy
KeyPair: <name>-workshop-ec2-kp    ex.(obi-wan-workshop-ec2-kp)                    S3: <name>-tm-workshop-bucket      ex.(obi-wan-tm-workshop-bucket)
EC2: Key: Name Value: <name>       ex. (obi-wan)

!!!!In order to run:
./create_workshop.py --account 1111111111 --password password <path to file>
'''
parser = argparse.ArgumentParser(
    description='Creates Workshop for Cloud One WS and FSS.')
parser.add_argument('--account', type=str, required=True, help='Provide AWS Account ID')
parser.add_argument('--password', type=str, required=True,
                    help='AWS sign in console password')
parser.add_argument(dest="filename", help="specify file path")
args = parser.parse_args()

aws_id = args.account
set_console_password = args.password
filename = args.filename

if not os.path.isfile(filename):
    print('File does not exist.')
else:
# Open the file.
    with open(filename) as f:
        content = f.read().splitlines()

#create a policy to be assign to workshop users(console access)
def create_user_basepolicy():
    try:
        iam_client = boto3.client('iam')
        tm_user_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                    "sqs:DeleteMessage",
                    "lambda:CreateFunction",
                    "cloudformation:ListExports",
                    "sqs:ReceiveMessage",
                    "cloudformation:ListStackInstances",
                    "iam:CreateRole",
                    "s3:CreateBucket",
                    "iam:AttachRolePolicy",
                    "cloudformation:DescribeStackResource",
                    "lambda:GetFunctionConfiguration",
                    "iam:PutRolePolicy",
                    "iam:DetachRolePolicy",
                    "cloudformation:DescribeStackEvents",
                    "sns:Subscribe",
                    "lambda:DeleteFunction",
                    "s3:PutObjectTagging",
                    "cloudformation:ListStackResources",
                    "iam:GetRole",
                    "sqs:GetQueueUrl",
                    "lambda:InvokeFunction",
                    "lambda:GetEventSourceMapping",
                    "cloudformation:DescribeStackInstance",
                    "sqs:SendMessage",
                    "sns:CreateTopic",
                    "iam:DeleteRole",
                    "sqs:GetQueueAttributes",
                    "logs:CreateLogGroup",
                    "cloudformation:DescribeStacks",
                    "s3:PutObject",
                    "s3:GetObject",
                    "sqs:AddPermission",
                    "cloudformation:GetTemplate",
                    "iam:GetRolePolicy",
                    "s3:GetBucketTagging",
                    "lambda:GetLayerVersion",
                    "lambda:PublishLayerVersion",
                    "lambda:GetFunction",
                    "sns:SetTopicAttributes",
                    "s3:ListBucket",
                    "sqs:ListQueueTags",
                    "lambda:CreateEventSourceMapping",
                    "s3:PutEncryptionConfiguration",
                    "iam:PassRole",
                    "sns:Publish",
                    "iam:DeleteRolePolicy",
                    "s3:GetObjectTagging",
                    "sqs:SetQueueAttributes",
                    "sqs:ListQueues",
                    "cloudformation:ListStacks",
                    "sns:GetTopicAttributes",
                    "logs:DescribeLogGroups",
                    "cloudformation:GetTemplateSummary",
                    "sqs:ListDeadLetterSourceQueues",
                    "lambda:AddPermission",
                    "s3:ListAllMyBuckets",
                    "cloudformation:CreateStack",
                    "sqs:CreateQueue",
                    "ec2:DescribeInstances",
                    "ec2:DescribeKeyPairs",
                    "logs:PutRetentionPolicy",
                    "ec2:GetPasswordData"
                    ],
                    "Resource": "*"
                }
            ]
        }
        iam_client.create_policy(
        PolicyName='tm_user_workshop_user',
        PolicyDocument=json.dumps(tm_user_policy)
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

#create workshop users
def workshop_user(ws_user, account, creds):
    try:
        iam_client = boto3.client('iam')
        iam_client.create_user(UserName=ws_user)
        iam_client.create_login_profile(UserName=ws_user, Password=creds, PasswordResetRequired=False)
        iam_client.attach_user_policy(UserName=ws_user, PolicyArn='arn:aws:iam::'+account+':policy/tm_user_workshop_user')
    except ClientError as e:
        logging.error(e)
        return False
    return True

#creates role, role policy, trust policy, and instance profile for ec2 role
def ec2_configs(tmuser):
    try:
        iam_client = boto3.client('iam')
        ec2_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                    "s3:PutObject",
                    "s3:GetObject"   
                    ],
                    "Resource": ["arn:aws:s3:::"+tmuser+"-tm-workshop-bucket","arn:aws:s3:::"+tmuser+"-tm-workshop-bucket/*"]
                }
            ]
        }
        iam_client.create_policy(
        PolicyName= tmuser+'_tm_workshop_ec2_rolepolicy',
        PolicyDocument=json.dumps(ec2_role_policy)
        )

        #create a trust policy to assume role
        trust_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal":{"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        })
        iam_client.create_role(
        RoleName=tmuser+'_ec2_assume_role_workshop',
        AssumeRolePolicyDocument=trust_policy
        )
        iam_client.attach_role_policy(PolicyArn='arn:aws:iam::'+aws_id+':policy/'+tmuser+'_tm_workshop_ec2_rolepolicy', RoleName=tmuser+'_ec2_assume_role_workshop')
        iam_client.create_instance_profile(InstanceProfileName=tmuser+'_ec2_assume_role_workshop')
        iam_client.add_role_to_instance_profile(InstanceProfileName=tmuser+'_ec2_assume_role_workshop',RoleName=tmuser+'_ec2_assume_role_workshop')
    except ClientError as e:
        logging.error(e)
        return False
    return True

#create s3 bucket; defaults to region us-east-1
def create_bucket(bucket_name, region=None):
    try:
        # if region left not defined
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        # any other specified region
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)

    except ClientError as e:
        logging.error(e)
        return False
    return True

#create a key pair, save private key locally
def create_a_kp(key_name):
    try:
        ec2_client = boto3.client('ec2')
        create_kp = ec2_client.create_key_pair(KeyName=key_name)
        pem_key = create_kp['KeyMaterial']
        open_new_file = open(key_name + '.pem', 'w')
        open_new_file.write(pem_key)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#create ec2 instance w/ tags and aws cli configured
def create_instance(inst_name, account):
    try:
        tags = [{'Key': 'Name', 'Value':inst_name}]
        ec2_client = boto3.client('ec2')
        ec2_client.run_instances(
            ImageId='ami-0f93c815788872c5d',
            KeyName=inst_name + "-workshop-ec2-kp",
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.medium',
            UserData='<powershell> msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi; Set-MpPreference -DisableRealtimeMonitoring $true; $AdminKey = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}"; $UserKey = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}"; Set-ItemProperty -Path $AdminKey -Name "IsInstalled" -Value 0; Set-ItemProperty -Path $UserKey -Name "IsInstalled" -Value 0 </powershell>',
            TagSpecifications=[{'ResourceType': 'instance', 'Tags': tags},],
            IamInstanceProfile={'Arn':'arn:aws:iam::'+account+':instance-profile/'+inst_name+'_ec2_assume_role_workshop'}
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

create_user_basepolicy()

#main loop
for users in content: 
    #create user policy for users
    workshop_user(ws_user=users,account=aws_id ,creds=set_console_password)
    ec2_configs(tmuser=users)
    create_a_kp(key_name=users + "-workshop-ec2-kp")
    create_bucket(bucket_name=users + "-tm-workshop-bucket", region=None)
    time.sleep(6)
    create_instance(inst_name=users, account=aws_id)


