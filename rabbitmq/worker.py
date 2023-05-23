import pika
import json
import boto3
from datetime import timedelta
import os
import sys
import django
import subprocess
import shutil
import requests
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, concatenate_videoclips
from django.db.models import F

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawtubehighlight.settings')
django.setup()
from highlight.models import Highlight

def main():
    # credentials = pika.PlainCredentials('test', 'test')
    parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='task_acc', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        message_data = json.loads(body)

        id_video = message_data['token']
        print("Processing Video: "+id_video)

        video = Highlight.objects.get(token=id_video)
        link = video.link
        timestamp = json.loads(video.timestamp)

        # video_path = concatenate_clip(id_video, link, timestamp)

        clips = []

        for time in timestamp:
            start = time[0]
            end = time[1]
            clip = VideoFileClip(link).subclip(start, end)
            clips.append(clip)

        final_clip = concatenate_videoclips(clips)

        output_folder = 'video'
        os.makedirs(output_folder, exist_ok=True)

        video_path = os.path.join(output_folder, id_video + ".mp4")
        final_clip.write_videofile(video_path)

        session = boto3.Session(
            aws_access_key_id= os.getenv('ACCESS_KEY_ID'),
            aws_secret_access_key= os.getenv('SECRET_ACCESS_KEY'),
        )

        s3_client = session.client('s3')

        bucket_name = "lawbagasbucket"
        file_path = video_path
        s3_key = "highlight/"+id_video+".mp4"

        # Upload the file to S3
        s3_client.upload_file(file_path, bucket_name, s3_key)

        video.highlight_link = f"https://lawbagasbucket.s3.amazonaws.com/highlight/{id_video}.mp4"
        video.progress = 100
        video.save()

        if message_data['is_orchest'] == True:
            url = os.getenv("CHOREO_URL")
            service_url = f"{url}/main/get-update"
            data = {
                "token": id_video,
                "video_url": video.highlight_link,
                "type": "highlight"
            }
            print("dikirim ke orchestra")
            requests.post(service_url, json=data)

        os.remove(file_path)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_acc', on_message_callback=callback)

    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
        
        
