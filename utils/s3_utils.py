import os
from pathlib import Path
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from cloudpathlib import CloudPath
import logging
from constants import DEFAULT_REGION


cache_client = None
cache_resource = None


def _client_from_cache(region):
    global cache_client
    if cache_client is None:
        cache_client = {}

    if cache_client.get(region):
        s3_client = cache_client[region]
        if s3_client is None:
            s3_client = boto3.client('s3', config=Config(signature_version='s3v4'), region_name=region)
            cache_client[region] = s3_client
        else:
            pass
    else:
        s3_client = boto3.client('s3', config=Config(signature_version='s3v4'), region_name=region)
        cache_client[region] = s3_client

    return s3_client


def put_object_contents(source_contents, object_key, region=DEFAULT_REGION, bucket_name=None):
    logging.debug(
        f'region:{region}, bucket_name:{bucket_name}, source_key:{source_contents}, destination_key:{object_key}')
    try:
        s3_client = _client_from_cache(region)
        s3_client.put_object(Bucket=bucket_name, Body=source_contents, Key=object_key)
    except Exception as e:
        logging.error(f'put_object_contents: {e}')
        raise e

def get_object(object_key, region=DEFAULT_REGION, bucket_name=None):
    logging.debug(
        f'region:{region}, bucket_name:{bucket_name}, object_key:{object_key}')
    try:
        s3_client = _client_from_cache(region)
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response
    except Exception as e:
        logging.error(f'get_object: {e}')
        raise e
    
def download_dir(remote_dir, region=DEFAULT_REGION, bucket_name=None, local_root_dir=None):
    logging.debug(
        f'region:{region}, bucket_name:{bucket_name}, remote_dir:{remote_dir}')
    try:
        cp = CloudPath(f"s3://{bucket_name}/{remote_dir}/")
        local_dir = Path(local_root_dir + '/' + remote_dir)
        cp.download_to(local_dir)
    except Exception as e:
        logging.error(f'download_object: {e}')
        raise e
    return str(local_dir)