import os
import json

from flask import Flask, render_template
import apsw
import boto3
import sqlite_s3vfs


app = Flask(__name__, template_folder=os.path.dirname(__file__))

s3_credentials = json.loads(os.environ['VCAP_SERVICES'])['aws-s3-bucket'][0]['credentials']
bucket = boto3.Session(
    aws_access_key_id=s3_credentials['aws_access_key_id'],
    aws_secret_access_key=s3_credentials['aws_secret_access_key'],
    region_name=s3_credentials['aws_region']
).resource('s3').Bucket(s3_credentials['bucket_name'])
s3vfs = sqlite_s3vfs.S3VFS(bucket=bucket)

@app.route('/', methods=['GET'])
def handle_request():
    with apsw.Connection('guestbook.sqlite', vfs=s3vfs.name) as db:
        cursor = db.cursor()
        cursor.execute('''
            SELECT
                message, author, posted
            FROM
                messages
            ORDER BY
                posted DESC, rowid DESC
            LIMIT 100;
        ''')
        messages = cursor.fetchall()

    return (render_template(
        'index.html',
        messages=messages,
    ), 200)
