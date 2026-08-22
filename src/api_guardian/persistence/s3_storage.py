"""S3 Storage Adapter."""
import boto3
from typing import BinaryIO


class S3StorageAdapter:
    def __init__(self, bucket_name: str, region_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region_name)

    def upload_artifact(self, object_key: str, data: BinaryIO) -> None:
        self.s3_client.upload_fileobj(data, self.bucket_name, object_key)

    def generate_presigned_get(self, object_key: str, expires_in: int = 600) -> str:
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': object_key},
            ExpiresIn=expires_in
        )

    def generate_presigned_put(self, object_key: str, expires_in: int = 1800) -> str:
        return self.s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': self.bucket_name, 'Key': object_key},
            ExpiresIn=expires_in
        )
