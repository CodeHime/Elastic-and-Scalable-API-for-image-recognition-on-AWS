import boto3
import time
# ec2s in process
ids = []
# AMI id to create from
ami_id = 'ami-0d8128819c6ecf857'
# Defining a tag for the ec2s
app_tag={'Key':'type', 'Value':'app'}
# Defining permissions
region_name='us-east-1'

#define maximum active ec2
max_ec2=19
# Filter for ec2 count
running_custom_filter = [{
		'Name':'tag:{key}'.format(key=app_tag['Key']), 
		'Values': [app_tag['Value']]
	},
	{
		'Name': 'instance-state-name',
		'Values': [
			'running', 'pending'
		]
	}
]
stopped_custom_filter = [{
		'Name':'tag:{key}'.format(key=app_tag['Key']), 
		'Values': [app_tag['Value']]
	},
	{
		'Name': 'instance-state-name',
		'Values': [
			'stopped',
			'stopping'
	  ]
	}
]

def create_and_initialize_new_instance(num=1):
	"""
	Function to create new app ec2
	"""
	USERDATA_SCRIPT='''
	#cloud-boothook
	#!/bin/bash
	cd /home/ec2-user
	echo $PWD
	aws s3 cp s3://cc-2022-proj-1/receive_messages.py /home/ec2-user/receive_messages.py
	python /home/ec2-user/receive_messages.py
	'''
	new_instance = ec2.create_instances(
		ImageId=ami_id, MinCount=num, MaxCount=num, 
		InstanceType='t2.micro',
		IamInstanceProfile={'Name':'cc-proj1-role'},
		SecurityGroupIds=['sg-0a3e959aa9197110c'],
		SecurityGroups=['launch-wizard-5'],
		KeyName='cc-proj1',
		UserData = USERDATA_SCRIPT
	)
	new_ids = [i.id for i in new_instance]
	ec2.create_tags(Resources=new_ids, 
		Tags=[app_tag])
	ids.append(new_ids)
	while True:
		instances = ec2.instances.filter(Filters=running_custom_filter,
			InstanceIds=new_ids)
		if len(list(instances))==num:
			break
	# new_instance[0].wait_until_running()
	return new_instance

# start ec2 session with permissions
# session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=region_name)
session = boto3.Session(region_name=region_name)

# connect to resources
ec2 = session.resource('ec2')
sqs = session.resource('sqs', region_name='us-east-1')
queue_request = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-request')

last_request=time.time()

while True:
	try:
		response = ec2.instances.filter(Filters=running_custom_filter)
		# stopped_response
		stopped_response = ec2.instances.filter(Filters=stopped_custom_filter)
		# length of SQS queue
		queue_request = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-request')
		queue_len = int(queue_request.attributes["ApproximateNumberOfMessages"]) + int(queue_request.attributes["ApproximateNumberOfMessagesDelayed"])
		#queue_len = len(queue_request.receive_messages(VisibilityTimeout=0, MaxNumberOfMessages=10))

		if len(list(response))<queue_len:
			if len(list(stopped_response))>0:
				for i in range(1, min(len(list(stopped_response)), queue_len-len(list(response)))):
					print("Starting ec2 resource ", i, " with id:",list(stopped_response)[i].id)
					list(stopped_response)[i].start()
			elif len(list(stopped_response))+len(list(response))<19:
				print("Creating new ec2 resources: {count}".format(count=min(queue_len,19) - len(list(stopped_response)) - len(list(response)))
				create_and_initialize_new_instance(num=min(queue_len,19) - len(list(stopped_response)) - len(list(response)))
			else:
				print("Maximum ec2 instances active")
			last_request=time.time()
		elif len(list(response))>=queue_len and time.time()-last_request>2*60 and len(list(stopped_response))>0:
			print("Deleting all stopped ec2 resources")
			for instance in stopped_response:
				instance.terminate()
		else:
			print("Nothing to do")
		time.sleep(2)
	except Exception as e: 
		print(e)
