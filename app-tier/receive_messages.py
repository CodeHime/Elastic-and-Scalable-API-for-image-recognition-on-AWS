################### receive_messages.py ###################
import numpy
import boto3
import os
import requests
import time
# Create session to aws
region_name='us-east-1'

#s3 connection
s3 = session.resource('s3')
bucket = s3.Bucket('cc-2022-proj-1')

# sqs connection
sqs = session.resource('sqs', region_name=region_name)
queue_request = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-request')
queue_respond = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-response')

# wfile_name = '/home/ec2-user/{client_id}.jpg'
wfile_name = '/home/ec2-user/{client_id}.jpg'
s3_inpath = 'input/{client_id}.jpg'
s3_outpath = 'output/{client_id}'
out_path = '/home/ec2-user/out.txt'

while int(queue_request.attributes["ApproximateNumberOfMessages"])>0:
	try:
		if os.path.exists("/home/ec2-user/face_recognition.py"):
			queue_request = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-request')
			message= queue_request.receive_messages(MessageAttributeNames=['Client_Id'], MaxNumberOfMessages=1)[0]
			#print(message.message_attributes)
			# Get the custom author message attribute if it was set

			if message.message_attributes is not None:
				byte = message.message_attributes.get('Client_Id').get('BinaryValue')
				client_id = message.body
				print('Request received, {0}!'.format(client_id))
				if byte:
					with open(wfile_name.format(client_id=client_id),'wb') as f:
						f.write(byte)
					with open(wfile_name.format(client_id=client_id),'rb') as f:
						bucket.upload_fileobj(f,s3_inpath.format(client_id=client_id))
					# os.system("su ec2-user")
					os.chdir("/home/ec2-user")
					# os.getcwd()
					os.system("python3 /home/ec2-user/face_recognition.py {img_path} > {out_path}".format(img_path=wfile_name.format(client_id=client_id), out_path=out_path))
		  
					with open(out_path,'rb') as f:
						bucket.upload_fileobj(f,s3_outpath.format(client_id=client_id))
					with open(out_path,'rb') as f:
						answer = f.read()
					print(answer)
					answer = 'NaN' if not answer else answer
					queue_respond.send_message(MessageBody=client_id, MessageAttributes={
					  'Client_Id': {
						  'StringValue':  answer,
						  'DataType': 'String'
					  }
					})
					# Let the queue_request queue know that the message is processed
					message.delete()	
					time.sleep(5)
				else:
					print("Error in getting BinaryValue in message")
			else:
				print("EC2 still initializing.")
	except Exception as e: 
		print(e)
		time.sleep(10)
			
        
# Get current ec2 instance id and stop current instance
response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = response.text
boto3.client('ec2', region_name=region_name).stop_instances(InstanceIds=[instance_id])