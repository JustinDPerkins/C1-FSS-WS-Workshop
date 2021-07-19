# AWS Workshop - Cloud One File Storage and Workload Security  

This workshop was designed for Trend Micro sellers to have a hands-on experience with Cloud One File Storage and Workload Security. After completing this workshop you will have gained a further understanding of the Cloud One platform security protection.
I have provided step by step documentation to deploy the respective security solutions in addition to documentation to trigger detections. 

## Prerequisites
<details>
	
<summary>Install supporting tools</summary>
	
1. **Install AWS CLI**
    - Install the AWS command line interface (CLI). 
	See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.

2. **Install Python**
    - Install the python programming language.
	See [Installing Python](https://www.python.org/downloads/) for details.
	
3. **Install PIP**
    - Install the package installer for Python.
	See [Installing PIP](https://pypi.org/project/pip/) for details.

4. **Install Boto3**
	- Install the AWS SDK for Python(boto3).
	See [Installing Boto3](https://pypi.org/project/boto3/) for details.
</details>

## Deploy the Workshop

Ensure you have the following files:

- create_workshop.py
- delete_workshop.py

<details>
<summary>Create a text file</summary>

1. **Create a text file**
    - Open a text editor like **notepad**
    - **Add one name per line**.
    - Must follow AWS naming conventions(no spaces/duplicates).
    - save file(sample_users.txt)

</details>

<details>
<summary>Deploy Create Workshop</summary>

1. Gather AWS Account ID.
	- [Help find my Account ID](https://www.apn-portal.com/knowledgebase/articles/FAQ/Where-Can-I-Find-My-AWS-Account-ID#:~:text=Your%20AWS%20Account%20identification%20number,your%20account%20information%20with%20AWS.&text=Your%20AWS%20ID%20is%20the,underneath%20the%20Account%20Settings%20section.)

2. Determine Password for IAM Users.
	- The users will need access to AWS Console.
	- Ensure password follows [AWS password policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html#default-policy-details)

3. In a terminal/cmd window, navigate directories to the saved create_workshop.py script:

    ```bash
    create_workshop.py --account <YOUR_AWS_ACCOUNT_ID> --password <SET_PASSWORD_CONSOLE_USERS> <PATH TO .TXT FILE CREATED>
    ```
</details>

## Delete the Workshop

Ensure you have the following files:

- delete_workshop.py
- user .txt file created previously

<details>
<summary>Deploy Delete Workshop</summary>

1. Gather AWS Account ID.
	- [Help find my Account ID](https://www.apn-portal.com/knowledgebase/articles/FAQ/Where-Can-I-Find-My-AWS-Account-ID#:~:text=Your%20AWS%20Account%20identification%20number,your%20account%20information%20with%20AWS.&text=Your%20AWS%20ID%20is%20the,underneath%20the%20Account%20Settings%20section.)

2. Located user txt file created.

3. In a terminal/cmd window, navigate directories to the saved create_workshop.py script:

    ```bash
    delete_workshop.py --account <YOUR_AWS_ACCOUNT_ID> <PATH TO .TXT FILE CREATED>
    ```
</details>

## Info to Know
<details>
<summary>Workshop Users Prerequisites</summary>

Ensure the user attending the workshop has a Cloud One account

1. Navigate to https://cloudone.trendmicro.com/
	- Sign up for a 30-Day Trial

</details>
<details>
<summary>AWS Resource Naming Conventions Used</summary>

1. **S3**
	- `<name>-tm-workshop-bucket`
    - Users created by script do not have permissions to list S3.
    - You must provide console link to 'their' S3 bucket. 
    - Example: `https://s3.console.aws.amazon.com/s3/buckets/<bucket name>`

2. **EC2**
    - Instance will be tagged with name of IAM User**.
    - Example: `Key: Name Value: <IAM UserName>`
    - Avoid putty, use the RDP client provided by AWS.
    - Unique key pairs generated and private keys will be stored locally.
    - User will decrypt .pem file via AWS EC2 console
		- Key-Pair name: `<name>-workshop-ec2-kp`
    - IAM role is attached to EC2 to upload/get object to/from S3:
        
        - upload to s3:
		`aws s3 cp <file> s3://<name of bucket>`
		- download from s3:
		`aws s3 cp s3://<name of bucket>/<file name> <name of file>`
		
3. **IAM**
	- Provide workshop users AWS sign-in link:
	- `https://<account-id>.signin.aws.amazon.com/console`
	- Users have permissions to deploy File Storage Security Stack
	- Users have permissions to deploy Workload Security Stack
	- IAM naming conventions:
		- IAM-Role for EC2: `<name>_ec2_assume_role_workshop`
		- IAM-Role-Policy: `<name>_tm_workshop_ec2_rolepolicy`
		- IAM-User: `<name>`
        - IAM-User-Policy: `tm-users-workshop_user`
		

</details>
