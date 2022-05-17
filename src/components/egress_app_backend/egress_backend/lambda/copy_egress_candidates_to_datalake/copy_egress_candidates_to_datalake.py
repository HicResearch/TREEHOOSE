# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

tracer = Tracer(service="EgressCopyToDatalake")
logger = Logger(service="EgressCopyToDatalake", sample_rate=0.1)
metrics = Metrics(service="EgressCopyToDatalake", namespace="EgressRequests")
s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

source_bucket = os.environ.get('EGRESS_STAGING_BUCKET')
target_bucket = os.environ.get('EGRESS_DATALAKE_BUCKET')
target_bucket_kms_key = os.environ.get('EGRESS_DATALAKE_BUCKET_KMS_KEY')
efs_mount_path = os.environ.get('EFS_MOUNT_PATH')


@metrics.log_metrics()
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    workspace_id = event['workspace_id']
    egress_request_id = event['egress_request_id']

    logger.info('Starting copy to datalake bucket with egress request ID: ' + egress_request_id)

    logger.debug('Staging bucket: ' + source_bucket)
    logger.debug('Datalake bucket: ' + target_bucket)

    s3_prefix = f"{workspace_id}/{egress_request_id}"

    copy_files_to_egress_datalake(
        source_bucket=source_bucket,
        s3_prefix=s3_prefix
    )
    metrics.add_metric(name="EgressRequestApproved", value=1, unit=MetricUnit.Count)
    return True


def copy_files_to_egress_datalake(source_bucket: str, s3_prefix: str):
    object_list = []
    downloaded_list = []
    get_objects_list(source_bucket, s3_prefix, object_list)
    if object_list:
        download_objects(object_list, source_bucket, downloaded_list)
        zip_and_upload(downloaded_list, target_bucket, s3_prefix)
        delete_staged_objects(object_list, source_bucket)
        delete_efs_objects(downloaded_list)
    else:
        logger.warn('No objects were found in the source bucket')


####################################################################
# get_object_list
# retrieves objects from bucket with specified prefix
####################################################################
def get_objects_list(bucket, prefix, object_list):
    """
    :param bucket: source bucket
    :type bucket: string
    :param prefix: s3 workspace prefix
    :type prefix: string
    :param object_list: list of objects
    :type object_list: []
    :return: []
    """
    # prepare args for retrieving items from a prefix (items from a certain prefix only)
    kwargs = {
        'Bucket': bucket,
        'Prefix': prefix
    }

    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(**kwargs)

    for page in pages:
        for obj in page['Contents']:
            object_k = obj['Key']
            if object_k.endswith("/"):
                # this is not an object
                continue
            else:
                object_list.append(object_k)

    logger.info('Retrieved list of objects')
    logger.debug('Object list: ' + str(object_list))
    return object_list


##################################################################
# zip objects and upload
# zip objects in temp dir and upload to datalake bucket
####################################################################
def zip_and_upload(downloaded_list, target_bucket, s3_prefix):

    # Static filename and top level prefix
    file_name = 'egress_data.zip'
    top_level_prefix = 'approved_egress'

    # Create zip file and load downloaded objects from /tmp
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', dir=efs_mount_path, delete=True) as f, \
         ZipFile(f.name, 'w', compression=ZIP_DEFLATED, allowZip64=True) as ziph:
        for _counter, object_f in enumerate(downloaded_list, start=1):
            logger.debug("WRITING FILE: " + object_f)
            # Write the file to the zip archive specifying the file name too instead of using the entire file path
            ziph.write(filename=object_f, arcname=get_file_name(object_f))

        # Close the zip file. If not done, archive archive may not be compatible with some zip management programs
        ziph.close()

        # Upload to target datalake bucket
        target_path = f"{top_level_prefix}/{s3_prefix}/{file_name}"
        s3_resource.meta.client.upload_file(
            f.name,
            target_bucket,
            target_path,
            ExtraArgs={
                'ServerSideEncryption': 'aws:kms',
                'SSEKMSKeyId': target_bucket_kms_key
            }
        )

        logger.info('%s object(s) zipped successfully and uploaded to datalake bucket', str(_counter))


####################################################################
# download objects
# download objects from S3 staging bucket and store in /temp dir
####################################################################
def download_objects(object_list, source_bucket, downloaded_list):
    """
    :param object_list: list of S3 objects
    :type List: []
    :param source_bucket: source S3 bucket
    :type object_list: string
    :return: bool
    """

    # retrieve objects in the list
    for _counter, obj in enumerate(object_list, start=1):
        # Get the file name from the object

        # split the object key into parts and get the file name
        file_name = get_file_name(obj)

        # Create download path in temp dir
        download_path = efs_mount_path + file_name

        # Download object into download path in tmp dir
        s3.download_file(source_bucket, obj, download_path)
        logger.debug('Downloaded %s from %s to %s', str(obj), source_bucket, download_path)

        downloaded_list.append(download_path)

    logger.info('Downloaded %s object(s) unto EFS storage', str(_counter))
    return downloaded_list


##########################################################################################################
# delete_staged_objects
# deletes egress objects from the staging bucket
##########################################################################################################
def delete_staged_objects(object_list, source_bucket):
    """
    :param object_list: list of objects to delete
    :type object_list: []

    :param source_bucket: S3 bucket containing the egress objects
    :type source_bucket: string

    :return: bool
    """
    # retrieve objects in the list
    for _counter, obj in enumerate(object_list, start=1):
        # create arguments for delete object call in staging bucket
        kwargs = {
            'Bucket': source_bucket,
            'Key': obj
        }

        # delete objects in staging bucket
        s3.delete_object(**kwargs)
        logger.debug('Deleted %s from %s', str(obj), source_bucket)

    logger.info('Deleted %s object/s from staging bucket', str(_counter))
    return True


##########################################################################################################
# delete_efs_objects
# deletes egress objects from the mounted EFS location
##########################################################################################################
def delete_efs_objects(downloaded_list):
    """
    :param downloaded_list: list of objects to delete
    :type object_list: []

    :return: bool
    """
    # retrieve objects in the list
    for _counter, obj in enumerate(downloaded_list, start=1):
        os.remove(obj)
        logger.debug('Deleted %s from EFS', str(obj))

    logger.info('Deleted %s object(s) from EFS', str(_counter))
    return True


##########################################################################################################
# Utility function to split an S3 object key into parts
##########################################################################################################
def get_file_name(path: str):
    # split the object key into parts and get the file name
    obj_parts = path.split('/')
    return obj_parts[-1]
