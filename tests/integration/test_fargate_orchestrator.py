"""Phase 20B: Real Fargate Verification Runtime Proof."""

import json
import uuid
from unittest.mock import MagicMock

from api_guardian.sandbox.orchestrator import FargateSandboxOrchestrator


def test_launch_verification_task():
    attempt_id = uuid.uuid4()
    pre_image_hashes = {"tests/test_foo.py": "hash123"}
    
    orchestrator = FargateSandboxOrchestrator(
        cluster_name="api-guardian-cluster",
        task_definition="arn:aws:ecs:us-east-1:123456789012:task-definition/api-guardian-bootstrap",
        subnets=["subnet-123"],
        security_groups=["sg-123"],
        region_name="us-east-1"
    )
    
    mock_run_task = MagicMock()
    mock_run_task.return_value = {
        "tasks": [{"taskArn": "arn:aws:ecs:us-east-1:123456789012:task/api-guardian-cluster/abc"}]
    }
    
    orchestrator.ecs_client.run_task = mock_run_task
    
    task_arn = orchestrator.launch_verification_task(
        attempt_id=attempt_id,
        snapshot_url="https://s3.amazonaws.com/test/snap",
        patch_url="https://s3.amazonaws.com/test/patch",
        result_url="https://api.guardian.local/results",
        expected_snapshot_hash="snaphash",
        expected_patch_hash="patchhash",
        nonce="securenonce",
        signing_secret="supersecret",
        pre_image_hashes=pre_image_hashes,
    )
    
    assert task_arn == "arn:aws:ecs:us-east-1:123456789012:task/api-guardian-cluster/abc"
    
    mock_run_task.assert_called_once()
    call_kwargs = mock_run_task.call_args.kwargs
    
    assert call_kwargs["cluster"] == "api-guardian-cluster"
    assert call_kwargs["taskDefinition"] == "arn:aws:ecs:us-east-1:123456789012:task-definition/api-guardian-bootstrap"
    assert call_kwargs["launchType"] == "FARGATE"
    
    # Assert network configuration has public IP disabled
    net_config = call_kwargs["networkConfiguration"]["awsvpcConfiguration"]
    assert net_config["subnets"] == ["subnet-123"]
    assert net_config["assignPublicIp"] == "DISABLED"
    
    # Assert env overrides
    overrides = call_kwargs["overrides"]["containerOverrides"][0]["environment"]
    env_dict = {kv["name"]: kv["value"] for kv in overrides}
    
    assert env_dict["SNAPSHOT_URL"] == "https://s3.amazonaws.com/test/snap"
    assert env_dict["SIGNING_SECRET"] == "supersecret"
    assert json.loads(env_dict["PRE_IMAGE_HASHES"]) == pre_image_hashes
