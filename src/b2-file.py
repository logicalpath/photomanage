'''
This is a utiity to upload and download files from Backblaze B2 Cloud Storage using
the B2 Python SDK.

API Refererence: https://b2-sdk-python.readthedocs.io/en/master/quick_start.html
'''

from b2sdk.v2 import *
import os
import sys
import argparse

# read these from environment variables
application_key_id = os.environ.get('B2_APPLICATION_KEY_ID')
application_key = os.environ.get('B2_APPLICATION_KEY')

# create a B2Api object
info = InMemoryAccountInfo()
b2_api = B2Api(info)

# authorize using application_key_id and application_key
b2_api.authorize_account("production", application_key_id, application_key) 

# get the bucket
bucket_name = "b2-snapshots-b00f0a6e6ad7"

bucket = b2_api.get_bucket_by_name(bucket_name)

for file_version, folder_name in bucket.ls(latest_only=True):

    print(file_version.file_name, file_version.upload_timestamp, folder_name)

