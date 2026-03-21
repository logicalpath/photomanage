"""
This is a utiity to upload and download files from Backblaze B2 Cloud Storage using
the B2 Python SDK.

API Refererence: https://b2-sdk-python.readthedocs.io/en/master/quick_start.html
"""

import os
import sys

from b2sdk.v2 import *  # noqa: F401, F403


def main():
    application_key_id = os.environ.get("B2_APPLICATION_KEY_ID")
    application_key = os.environ.get("B2_APPLICATION_KEY")

    if not application_key_id or not application_key:
        sys.exit("Error: B2_APPLICATION_KEY_ID and B2_APPLICATION_KEY must be set.")

    info = InMemoryAccountInfo()  # noqa: F405
    b2_api = B2Api(info)  # noqa: F405  # type: ignore[arg-type]
    b2_api.authorize_account("production", application_key_id, application_key)

    bucket_name = "b2-snapshots-b00f0a6e6ad7"
    bucket = b2_api.get_bucket_by_name(bucket_name)

    for file_version, folder_name in bucket.ls(latest_only=True):
        print(file_version.file_name, file_version.upload_timestamp, folder_name)


if __name__ == "__main__":
    main()
