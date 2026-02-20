import boto3

s3 = boto3.client("s3")

def upload_file_to_s3(file_path: str, bucket: str, object_name: str):
    s3.upload_file(file_path, bucket, object_name)
    return f"https://{bucket}.s3.amazonaws.com/{object_name}"
