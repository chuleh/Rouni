import os
import boto3

def sync_resources(bucket_name, resource_prefix, local_path):
    client = boto3.resource('s3')
    bucket = client.Bucket(bucket_name)
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    for obj in bucket.objects.filter(Prefix=resource_prefix):
        if obj.key[-1] != "/" and not os.path.exists(obj.key):  # Ignore S3 'folders'
            print(f'Rouni has become selfaware: downloading {obj.key}...')
            bucket.download_file(obj.key, obj.key)


def save_resource(bucket_name, local_file):
    client = boto3.client('s3')
    client.upload_file(
        local_file, bucket_name, local_file,
        ExtraArgs={'StorageClass': 'STANDARD'}
    )
    print(f'Rouni has become self aware: saving {local_file}')
