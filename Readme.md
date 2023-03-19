Cloud Computing Project 1
=========================
The aim of this project is to build an elastic web application, which utilizes cloud computing services
Amazon Web Services (AWS), with objectives of reliability, system elasticity, cost-effectiveness and
real-time usage. An image-recognition application has been created as a REST service on the Cloud for
the clients to easily access. The application takes images as inputs and returns the correct outputs through
a deep learning model using AWS resources for all the processes. The basic tasks included in the system
are the RESTful API, an implemented load balancer that scales in and scales out EC2 instances at App
tier according to the demand of the user.

Setup
++++++

● Web Tier
	○ Create and start an EC2 instance using the ubuntu image.
	○ Download the code of the flask and ec2_instantiate code in the instance.
	○ Install the dependencies using requirements.txt
	○ Install python memcache using pip command.
	○ Assign an IAM role to it with permissions to SQS and EC2.
● App Tier
	○ Create an EC2 instance using the image given by the professor.
	○ Download init.sh and execute it.
	○ Create an AMI from this app-tier and set the ami-id in ec2_instantiate.py
	○ Assign an IAM role to it with permissions to S3, SQS and EC2.
● S3
	○ Create a bucket with an ‘input’ and ‘output’ folder
● SQS
	○ Create two queues, one for request and one for response


Execution
++++++++++
● Web Tier
	○ Start the flask server using ```python3 main.py```.
	○ Also start the ec2_instantiate script using ```nohup python3 ec2_instantiate.py &``` or in another EC2 instance by running ``` python3 ec2_instantiate.py ```
● Workload generator
	○ Execution command from local:
	```python3 multithread_workload_generator_verify_results_updated.py
	--num_request NUM_REQUEST --url URL --image_folder IMAGE_PATH```
