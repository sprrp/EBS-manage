import boto3
import datetime
import smtplib
from email.mime.text import MIMEText

# Set the AWS region where the EBS volumes are located
region = 'us-east-1'

# Set the number of days to filter by
age_in_days = 30

# Set the email address for the owner of the EBS volumes
owner_email = 'owner@example.com'

# Set the email address and password for the sender
sender_email = 'sender@example.com'
sender_password = 'password'

# Set the SMTP server and port for sending emails
smtp_server = 'smtp.example.com'
smtp_port = 587

# Create a Boto3 client for the EC2 service
client = boto3.client('ec2', region_name=region)

# Get the current time
now = datetime.datetime.utcnow()

# Filter the EBS volumes by age and attachment status
filters = [
    {'Name': 'status', 'Values': ['available']},
    {'Name': 'create-time', 'Values': [f'{age_in_days}+']}
]
volumes = client.describe_volumes(Filters=filters)['Volumes']

# Loop through the EBS volumes and shut them down
for volume in volumes:
    # Get the age of the volume
    volume_time = volume['CreateTime'].replace(tzinfo=None)
    age = now - volume_time

    # Shut down the volume if it's older than 30 days
    if age.days > age_in_days:
        print(f'Shutting down EBS volume {volume["VolumeId"]}')
        client.update_volume(VolumeId=volume['VolumeId'], State='available')

# Set the expiration date for the EBS volumes
expiration_date = now + datetime.timedelta(days=30)

# Set the EBS volumes to expire in 30 days
for volume in volumes:
    volume_time = volume['CreateTime'].replace(tzinfo=None)
    age = now - volume_time
    if age.days > age_in_days:
        client.modify_volume_attribute(
            VolumeId=volume['VolumeId'],
            Attribute='expiration',
            OperationType='add',
            ExpireOn=expiration_date.strftime('%Y-%m-%d')
        )

# Send an email to the owner warning them that the EBS volumes will be deleted in 30 days
subject = 'EBS volume deletion warning'
body = f'Your EBS volumes will be deleted in 30 days. Please take action to prevent data
