from flask import Flask, request
from werkzeug.utils import secure_filename
import matplotlib.image as img
import boto3
from flask import session
import time
from flask_session import Session
import asyncio
import threading
import concurrent.futures
sem = threading.Semaphore()
from werkzeug.contrib.cache import MemcachedCache

cache = MemcachedCache(['127.0.0.1:11211'])

app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# SESSION_TYPE = 'filesystem'
# app.config.from_object(__name__)
# Session(app)

request_dict = {}

session = boto3.Session(aws_access_key_id='ACCESS_ID', aws_secret_access_key='SECRET_KEY')
sqs = session.resource('sqs', region_name='us-east-1')

queue_request = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-request')
queue_respond = sqs.get_queue_by_name(QueueName='sqs-cc-proj1-response')


@app.route('/upload', methods = ['POST'])
def upload_image():
    # global request_dict
    print("IN request")
    if request.method == 'POST':
        # file_name = "/home/nisarg1499/assignments/spring22/cc/project/cloudflare.png"
        # byte = open(file_name, 'rb').read()
        # print(byte)
        # print(file)
        # img_data = img.imread(file)

        file = request.files["myfile"]
        file.save(secure_filename(file.filename))
        byte = open(file.filename, 'rb').read()

        # queue_url = "https://sqs.us-east-1.amazonaws.com/105917244222/sqs-cc-proj1-request"
        filename = file.filename.split('.')[0]
        print(filename)
        queue_request.send_message(
            MessageBody = filename,
            MessageAttributes = {
                'Client_Id': {
                    'BinaryValue': byte,
                    'DataType': 'Binary'
                }
            }
        )
        print("Message sent to queue")
        # request_dict[filename] = ""
        # session[filename] = ""
        print("Filename: ", filename)
        print("request_dict: ", request_dict)
        # time.sleep(5)
        while True:
            # if session.get(filename) is not None:
            # if request_dict.get(filename,"") != "":
            # if request_dict[filename] != "":
            dat = cache.get(filename)
            if dat is not None:
            # if filename in request_dict:
                break
            else:
                # asyncio.run(rec_message())
                continue
        # del request_dict
        # return session[filename]
        return cache.get(filename)
        # return request_dict[filename]

        # while request_dict[filename] == "":
        #     for message in queue_respond.receive_messages(MessageAttributeNames=['Client_Id']):
        #         if message.message_attributes is not None:
        #             img_label = message.message_attributes.get('Client_Id').get('StringValue')
        #             client_id = message.body
        #             print("Client: ", client_id)
        #             if img_label:
        #                 request_dict[client_id] = img_label
        #                 # print("Ans: ", request_dict[filename])
        #                 print("Ans: ", request_dict[client_id])
        #                 print(request_dict)
        #         message.delete()
        # while request_dict[filename] == "":
        #     print("In rec message")
        #     for message in queue_request.receive_messages(MessageAttributeNames=['Client_Id']):
        #         if message.message_attributes is not None:
        #             img_label = message.message_attributes.get('Client_Id').get('StringValue')
        #             client_id = message.body
        #             print("Client: ", client_id)
        #             # if img_label:
        #             request_dict[client_id] = client_id
        #             print("Ans: ", request_dict[client_id])
        #             print("Dictinoary: ", request_dict)
        #             message.delete()
        # answer = request_dict[filename]
        # ans = '%s answer of %s' % (filename, answer)
        # del request_dict[filename]

        # return request_dict[filename]
    return "Image has been uploaded!!"

def rec_message(request_dict):
    # global request_dict
    while True:
        # print("In rec message")
        # for message in queue_request.receive_messages(MessageAttributeNames=['Client_Id']):
        #     if message.message_attributes is not None:
        #         img_label = message.message_attributes.get('Client_Id').get('StringValue')
        #         client_id = message.body
        #         print("Client: ", client_id)
        #         # if img_label:
        #         request_dict[client_id] = client_id
        #         print("Ans: ", request_dict[client_id])
        #         print("Dictinoary: ", request_dict)
        #         time.sleep(5)
        #         message.delete()
        # time.sleep(5)
        print("In rec message")
        for message in queue_respond.receive_messages(MessageAttributeNames=['Client_Id']):
            if message.message_attributes is not None:
                img_label = message.message_attributes.get('Client_Id').get('StringValue')
                client_id = message.body
                print("Client: ", client_id)
                if img_label:
                    # sem.acquire()
                    # session[client_id] = img_label
                    # request_dict[client_id] = img_label
                    cache.set(client_id, img_label, timeout=10*60)
                    a = cache.get(client_id)
                    print("Ans: ", a)
                    print("Dictinoary: ", request_dict)
                    # sem.release()
                    # time.sleep(5)
                message.delete()
        time.sleep(1)


if __name__=="__main__":
    t = threading.Thread(target=rec_message, args=(request_dict,))
    t.start()
    # with concurrent.futures.ThreadPoolExecutor() as executor:
        # err_detect = executor.submit(rec_message, request_dict)
    app.run(debug=True, port=5000, host='0.0.0.0')
    # print("Flask")
