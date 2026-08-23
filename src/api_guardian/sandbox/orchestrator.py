"""AWS ECS/Fargate Sandbox Orchestrator."""

import uuid

import boto3

from api_guardian.application.interfaces.sandbox import SandboxOrchestrator


class FargateSandboxOrchestrator(SandboxOrchestrator):
    """Launches secure, isolated Fargate tasks for untrusted execution."""

    def __init__(
        self,
        cluster_name: str,
        task_definition: str,
        subnets: list[str],
        security_groups: list[str],
    ):
        self.cluster_name = cluster_name
        self.task_definition = task_definition
        self.subnets = subnets
        self.security_groups = security_groups
        # The region should be configured via environment variables normally.
        self.ecs_client = boto3.client("ecs")

    def launch_verification_task(
        self,
        attempt_id: uuid.UUID,
        snapshot_url: str,
        patch_url: str,
        result_url: str,
        expected_snapshot_hash: str,
        expected_patch_hash: str,
        nonce: str,
        signing_secret: str,
    ) -> str:
        """Launches the bootstrap container with capabilities."""

        # Inject the capabilities strictly via environment overrides
        env_vars = [
            {"name": "SNAPSHOT_URL", "value": snapshot_url},
            {"name": "PATCH_URL", "value": patch_url},
            {"name": "RESULT_URL", "value": result_url},
            {"name": "EXPECTED_SNAPSHOT_HASH", "value": expected_snapshot_hash},
            {"name": "EXPECTED_PATCH_HASH", "value": expected_patch_hash},
            {"name": "ATTEMPT_ID", "value": str(attempt_id)},
            {"name": "NONCE", "value": nonce},
            {"name": "SIGNING_SECRET", "value": signing_secret},
        ]

        response = self.ecs_client.run_task(
            cluster=self.cluster_name,
            taskDefinition=self.task_definition,
            launchType="FARGATE",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": self.subnets,
                    "securityGroups": self.security_groups,
                    # Always disable public IP for strict egress isolation
                    "assignPublicIp": "DISABLED",
                }
            },
            overrides={
                "containerOverrides": [{"name": "api-guardian-bootstrap", "environment": env_vars}]
            },
        )

        if not response.get("tasks"):
            raise RuntimeError(f"Failed to launch ECS task: {response.get('failures')}")

        return str(response["tasks"][0]["taskArn"])
