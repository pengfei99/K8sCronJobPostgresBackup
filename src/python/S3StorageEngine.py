import os

import boto3
from botocore.config import Config
from boto3 import exceptions
import logging

log = logging.getLogger(__name__)


class S3IO:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, session_token: str, region_name='us-east-1'):
        if session_token:
            self.s3_client = boto3.resource('s3', endpoint_url=endpoint, aws_access_key_id=access_key,
                                            aws_secret_access_key=secret_key,
                                            aws_session_token=session_token,
                                            config=Config(signature_version='s3v4'),
                                            region_name=region_name)
        else:
            self.s3_client = boto3.resource('s3', endpoint_url=endpoint, aws_access_key_id=access_key,
                                            aws_secret_access_key=secret_key,
                                            config=Config(signature_version='s3v4'),
                                            region_name=region_name)

    def write_byte_to_s3(self, bucket_name: str, bucket_key: str, data):
        """
        It writes input data in byte to a s3 bucket with given bucket name and key

        :param bucket_name: The name of the bucket that you want to write
        :param bucket_key: The destination path of the data relative to the bucket name
        :param data: The data in byte that you want to write to s3
        :return: None
        """
        # # set the path of where you want to put the object
        # s3_object = self.s3_client.Object(bucket_name, bucket_key)
        # # set the content which you want to write
        # s3_object.put(Body=data)
        self.s3_client.put_object(Bucket=bucket_name, Key=bucket_key, Body=data)

    def upload_file_to_s3(self, bucket_name: str, bucket_key: str, source_file_path, delete_origin=False):
        """
        Upload a file to an AWS S3 bucket.

        :param bucket_name: The name of the bucket that you want to write
        :param bucket_key: The destination path of the data relative to the bucket name
        :param source_file_path: indicates the source file path, all files under the path will be uploaded to s3
        :param delete_origin: default value is False. If set to True, after upload, the source file will be deleted.
        :return: None
        """
        try:
            self.s3_client.upload_file(source_file_path, bucket_name, bucket_key)
            if delete_origin:
                os.remove(source_file_path)
        except exceptions.S3UploadFailedError as e:
            log.exception(e)
            exit(1)

    def download_file_from_s3(self, bucket_name: str, bucket_key: str, dest_path):
        """
        Download a file to an AWS S3 bucket.

        :param bucket_name: The name of the bucket that you want to write
        :param bucket_key: The destination path of the data relative to the bucket name
        :param dest_path: indicates the destination file path.
        :return: None
        """
        try:
            self.s3_client.meta.client.download_file(bucket_name, bucket_key, dest_path)
        except Exception as e:
            log.exception(e)
            exit(1)

# The difference between upload-file and put_object in boto3
#
# The upload_file method is handled by the S3 Transfer Manager, this means that it will automatically handle
# multipart uploads behind the scenes for you, if necessary.
#
# The put_object method maps directly to the low-level S3 API request. It does not handle multipart uploads for you.
# It will attempt to send the entire body in one request.
