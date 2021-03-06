from __future__ import print_function  # provides Python 3's print() with end=''
import sys
import os
import time
import boto
import boto.s3
from boto.s3.key import Key
import glob

def DeleteFilesOnS3(file_prefix, substring, actually_delete=False):
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    bucket_name = 'natural-interaction'

    result = []

    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY)
        location='EU'
        bucket = conn.get_bucket(bucket_name, validate=False)
        files = bucket.list(prefix=file_prefix)
        for key in files:
            result.append(key.key)
        for k in result:
            if substring in k:
                print(k)
                if actually_delete:
                    print('deleting')
                    bucket.delete_key(k)
    except:
        print ("delete files on S3 error")
        print((sys.exc_info()))

def UploadFileToS3(filename, group_filename):
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    bucket_name = 'natural-interaction'

    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY)
    
        location='EU'
        # bucket = conn.create_bucket(bucket_name, location = 'EU')
        bucket = conn.get_bucket(bucket_name, validate=False)
        print(filename)
        def percent_cb(complete, total):
            sys.stdout.write('.')
            sys.stdout.flush()

        k = Key(bucket)
        k.key = group_filename
        k.set_contents_from_filename(filename,
                                     cb=percent_cb,
                                     num_cb=10)
    except:
        print("upload to S3 error")
        print((sys.exc_info()))
        return False

    return True

def ListFilesOnS3(file_prefix):
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    bucket_name = 'natural-interaction'

    result = []

    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY)
        location='EU'
        bucket = conn.get_bucket(bucket_name, validate=False)
        files = bucket.list(prefix=file_prefix)
        for key in files: 
            result.append(key.key)
            
    except:
        print ("list files on S3 error")
        print((sys.exc_info()))
        return []

    return result

def DownloadFileFromS3(key, filename):
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    bucket_name = 'natural-interaction'
    
    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY)
        location='EU'
        bucket = conn.get_bucket(bucket_name, validate=False)
        k = Key(bucket)
        k.key = key
        k.get_contents_to_filename(filename)
    except:
        print("download from S3 error")
        print((sys.exc_info()))
        return False

    return True

def DownloadImagesFromS3(prefix, substring, group):
    files = ListFilesOnS3('images/' + prefix)
    downloaded = 0
    skipped = 0
    failed = 0
    # filter out based on substring
    if len(substring) > 0:
        files = list(filter(lambda x: substring in x, files))
    # filter out based on extension
    files = list(filter(lambda x: '.jpg' in x, files))
    for f in files:
        replaced = f.replace('images/', 'downloaded/')
        if os.path.isfile(replaced):
            # print('skipping download of %s' % f)
            # print('.', end='')
            skipped += 1
        else:
            print('attempting download of %s to %s' % (f, replaced))
            if DownloadFileFromS3(f, replaced):
                downloaded += 1
            else:
                failed += 1
    return skipped,downloaded,failed

def ListLocalImages(prefix, substring):
    local_files = glob.glob(prefix + '*.jpg')
    # optionally filter out those that do not contain given substring
    if len(substring) > 0:
        local_files = list(filter(lambda x: substring in x, local_files))
    return sorted(local_files)

