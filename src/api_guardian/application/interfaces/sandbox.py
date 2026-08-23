"""Sandbox Orchestrator interface (Port)."""

import uuid
from abc import ABC, abstractmethod


class SandboxOrchestrator(ABC):
    @abstractmethod
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
        """Launches a Fargate sandbox task with capabilities.

        Returns:
            task_id (str): The execution platform's identifier for the task.
        """
