import os
import json

from flask import Flask, redirect, request, render_template
import apsw
import boto3
import sqlite_s3vfs

from jinja2 import evalcontextfilter
from markupsafe import Markup, escape

app = Flask(__name__, template_folder=os.path.dirname(__file__))

s3_credentials = json.loads(os.environ['VCAP_SERVICES'])['aws-s3-bucket'][0]['credentials']
bucket = boto3.Session(
    aws_access_key_id=s3_credentials['aws_access_key_id'],
    aws_secret_access_key=s3_credentials['aws_secret_access_key'],
    region_name=s3_credentials['aws_region']
).resource('s3').Bucket(s3_credentials['bucket_name'])
s3vfs = sqlite_s3vfs.S3VFS(bucket=bucket)

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = escape(value).replace('\n', Markup('<br>'))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.route('/', methods=['GET', 'POST'])
def handle_request():
    return \
        handle_get() if request.method == 'GET' else \
        handle_post()


def handle_get():
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


def handle_post():
    with apsw.Connection('guestbook.sqlite', vfs=s3vfs.name) as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO messages(message, author, posted)
            VALUES (?, ?, datetime('now'))
        ''', (request.form['your-message'], request.form['your-name']))

    return redirect('/')
