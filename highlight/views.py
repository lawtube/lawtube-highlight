from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from moviepy.editor import VideoFileClip, concatenate_videoclips
import json, base64, os, boto3, sys, uuid, django, pika, requests
from dotenv import load_dotenv
from .models import *

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawtubehighlight.settings')
django.setup()

def rabbitmq(message,queue):
    credentials = pika.PlainCredentials('test', 'test')
    parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ))
    print(" [x] Sent %r" % message)
    connection.close()

def process(request,queue):
    data = json.loads(request.body)
    video_file = data['link']
    timestamp = data['timestamp']
    video = Highlight.objects.create(link = video_file, timestamp = json.dumps(timestamp), progress = 0)
    print(video)
    message_data = {
        "token": str(video.token)
    }
    message = json.dumps(message_data)
    rabbitmq(message,queue)
    return str(video.token)

@api_view(['POST'])
def create_highlight(request):
    deserialize = json.loads(request.body)
    link = deserialize['link']
    timestamp = deserialize['timestamp']

    link_isvalid = validate_link(link)
    if not link_isvalid:
        return JsonResponse({'message': 'Video cannot be accessed'}, status=status.HTTP_400_BAD_REQUEST)
    timestamp_isvalid = validate_timestamp(timestamp)
    if not timestamp_isvalid:
        return JsonResponse({'message': 'Invalid timestamp'}, status=status.HTTP_400_BAD_REQUEST)
    
    token = process(request,'task_acc')
    return JsonResponse({'token': token}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_result(request, token):
    video = Highlight.objects.get(token=token)
    if video.highlight_link is None:
        highlight_link = ""
    else:
        highlight_link = video.highlight_link
    result = {
        'progress': video.progress,
        'highlight_link': highlight_link
    }
    return JsonResponse(result, status=status.HTTP_200_OK)

def validate_timestamp(timestamp):
    valid = True
    for time in timestamp:
        if len(time) != 2 or time[0] > time[1] or time[0] < 0 or time[1] < 0:
            valid = False
            break
    return valid

def validate_link(link):
    try:
        response = requests.head(link)
        if response.status_code == requests.codes.ok or response.status_code == 201:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

