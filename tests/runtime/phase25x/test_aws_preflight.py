import os
import subprocess

import boto3
import pytest
from botocore.exceptions import ClientError, NoCredentialsError


@pytest.mark.real_aws
def test_aws_preflight():
    """AWS PREFLIGHT VALIDATOR."""
    
    print("\n\nAWS PRECHECK\n")
    
    # 1. Check CLI availability
    try:
        res = subprocess.run(["aws", "--version"], capture_output=True, text=True)
        if res.returncode == 0:
            print("CLI             = AVAILABLE")
        else:
            print("CLI             = UNAVAILABLE")
    except FileNotFoundError:
        print("CLI             = UNAVAILABLE")
        
    # 2. Check Credentials
    sts = boto3.client("sts", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    try:
        identity = sts.get_caller_identity()
        print("Credentials     = AVAILABLE")
        print(f"Account         = {identity.get('Account')}")
        print(f"Region          = {sts.meta.region_name}")
        
        # 3. Check Service Access (Lightweight)
        s3 = boto3.client("s3", region_name=sts.meta.region_name)
        s3.list_buckets()
        print("S3              = ACCESSIBLE")
        
        ecs = boto3.client("ecs", region_name=sts.meta.region_name)
        ecs.list_clusters()
        print("ECS             = ACCESSIBLE")
        
        iam = boto3.client("iam")
        iam.get_user()
        print("IAM             = ACCESSIBLE")
        
        print("\nREAL AWS TESTS = READY\n")
        
    except (NoCredentialsError, ClientError) as e:
        print("Credentials     = UNKNOWN/UNAVAILABLE")
        print("Account         = UNKNOWN")
        print("Region          = UNKNOWN")
        print("\nREAL AWS TESTS = BLOCKED")
        pytest.skip(f"AWS credentials unavailable or lacking permissions: {e}")
