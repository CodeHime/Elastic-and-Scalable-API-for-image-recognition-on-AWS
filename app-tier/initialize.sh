# 1. Start EC2 from template
# 2. Run the below commands
# 3. Add user data to run `python receive_messages.py`
#!/bin/bash
# ssh -i ~/Downloads/cc-proj1-app-1.pem ec2-user@ec2-3-88-217-9.compute-1.amazonaws.com
# aws s3 cp s3://cc-2022-proj1/config ~/.aws/config
aws s3 cp s3://cc-2022-proj-1/startup.sh startup.sh
chmod +x startup.sh
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
sudo python2.7 get-pip.py --force-reinstall
sudo pip install boto3 numpy
mkdir -p temp
aws s3 cp s3://cc-2022-proj-1/receive_messages.py receive_messages.py
