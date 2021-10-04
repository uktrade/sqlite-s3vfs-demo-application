import os

import apsw
import boto3
import sqlite_s3vfs

bucket_name = os.environ['BUCKET_NAME']
bucket = boto3.Session(profile_name='sqlite-s3vfs-demo-application').resource('s3').Bucket(bucket_name)
s3vfs = sqlite_s3vfs.S3VFS(bucket=bucket)

# sql = '''
#     CREATE TABLE messages(
#         message text not null,
#         author text not null,
#         posted datetime not null
#     );
# '''
# sql = '''
#     CREATE INDEX posted_idx ON messages(posted DESC);
# '''
sql = '''
    INSERT INTO messages(message, author, posted)
    VALUES ('This is great!', 'Bob the Builder', datetime('now'))
'''

with apsw.Connection('guestbook.sqlite', vfs=s3vfs.name) as db:
    cursor = db.cursor()
    cursor.execute(sql)
