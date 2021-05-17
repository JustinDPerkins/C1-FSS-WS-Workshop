import os.path
import boto3
import argparse
import logging
from botocore.exceptions import ClientError
'''
Trend Micro Seller workshop removal script. Run this script to delete all resources created for Trend Micro WS and FSS workshop.

!!!!In order to run:
./create_workshop.py --account 1111111111 <path to file>
'''
parser = argparse.ArgumentParser(
    description='Terminates resources for Cloud One WS and FSS workshop.')
parser.add_argument('--account', type=str, required=True, help='Provide AWS Account ID')
parser.add_argument(dest="filename", help="specify file path")
args = parser.parse_args()

account_id = args.account
filename = args.filename
policy_name = "tm_user_workshop_user"

if not os.path.isfile(filename):
    print('File does not exist.')
else:
# Open the file.
    with open(filename) as f:
        content = f.read().splitlines()

#deletes users
def delete_iam_user(file,account,policy):
    try:
        iam_client = boto3.client('iam')
        iam_client.delete_login_profile(UserName=file)
        iam_client.detach_user_policy(UserName=file, PolicyArn='arn:aws:iam::'+account+':policy/'+policy)
        iam_client.delete_user(UserName=file)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#list all workshop tagged instances
def list_instances_by_tag_value(tagkey, tagvalue):
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:'+tagkey,
                    'Values': [tagvalue]
                }
            ]
        )
        instancelist = []
        for reservation in (response["Reservations"]):
            for instance in reservation["Instances"]:
                instancelist.append(instance["InstanceId"])
        #return instancelist
    except ClientError as e:
        logging.error(e)
        return False
    return instancelist

#delete workshop tagged ec2
def delete_identified_instances(cattle):
    try:
        ec2_client = boto3.client('ec2')
        ec2_client.terminate_instances(InstanceIds=cattle)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#delete workshop user keypairs for ec2 access
def delete_kp(kpname):
    try:
        ec2_client = boto3.client('ec2')
        ec2_client.delete_key_pair(KeyName=kpname+'-workshop-ec2-kp')
    except ClientError as e:
        logging.error(e)
        return False
    return True

#delete workshop role policy and role
def delete_rp(rolename, account):
    try:
        iam_client = boto3.client('iam')
        iam_client.detach_role_policy(RoleName=rolename+'_ec2_assume_role_workshop', PolicyArn='arn:aws:iam::'+account+':policy/'+rolename+'_tm_workshop_ec2_rolepolicy')
        iam_client.delete_policy(PolicyArn='arn:aws:iam::'+account+':policy/'+rolename+'_tm_workshop_ec2_rolepolicy')
        iam_client.remove_role_from_instance_profile(InstanceProfileName= rolename+'_ec2_assume_role_workshop',RoleName=rolename+'_ec2_assume_role_workshop')
        iam_client.delete_instance_profile(InstanceProfileName=rolename+'_ec2_assume_role_workshop')
        iam_client.delete_role(RoleName=rolename+'_ec2_assume_role_workshop')
    except ClientError as e:
        logging.error(e)
        return False
    return True

#delete files uploaded by sellers into their specific buckets
def empty_s3objects(bucket):
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket+'-tm-workshop-bucket')
        if 'Contents' in response:
            for s3_object in response['Contents']:
                s3_client.delete_object(Bucket=bucket+'-tm-workshop-bucket', Key=s3_object['Key'])
    except ClientError as e:
        logging.error(e)
        return False
    return True

# delete the s3 bucket itself
def delete_bucket(bucket):
    try:
        s3_client = boto3.client('s3')
        s3_client.delete_bucket(Bucket=bucket+'-tm-workshop-bucket')
    except ClientError as e:
        logging.error(e)
        return False
    return True

#last delete the iam user policy
def delete_user_iampolicy(account, policy):
    try:
        iam_client = boto3.client('iam')
        iam_client.delete_policy(PolicyArn='arn:aws:iam::'+account+':policy/'+policy)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#main loop
for users in content:
    #kill workshop ec2
    kill_the_cattle = list_instances_by_tag_value(tagkey='Name', tagvalue=users)
    delete_identified_instances(cattle=kill_the_cattle)
    #kill workshop s3
    empty_s3objects(bucket=users)
    delete_bucket(bucket=users)
    #kill workshop keypairs
    delete_kp(kpname=users)
    #kill workshop console users
    delete_iam_user(file=users, account=account_id,policy=policy_name)
    #kill roles and role policies
    delete_rp(rolename=users, account=account_id)

#must wait for all users to be detached to kill user policy for console
delete_user_iampolicy(account=account_id,policy=policy_name)

