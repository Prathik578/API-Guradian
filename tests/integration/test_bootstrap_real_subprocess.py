"""Phase 23X: Real Subprocess Execution Proof."""

import os
import subprocess
import uuid
import json
import pytest
from pathlib import Path

def test_real_bootstrap_secret_isolation(tmp_path):
    """Prove that the Go bootstrap scrubs sensitive env vars before executing the subprocess."""
    
    bootstrap_dir = Path("/home/prathik/Documents/Antigravity/bootstrap")
    
    # 1. Compile the Go bootstrap
    go_bin = tmp_path / "bootstrap_bin"
    build_cmd = ["go", "build", "-o", str(go_bin), "."]
    res = subprocess.run(build_cmd, cwd=bootstrap_dir, capture_output=True, text=True)
    assert res.returncode == 0, f"Failed to build Go bootstrap: {res.stderr}"
    
    # 2. We instruct the bootstrap to run a malicious python script that dumps env to a file
    env_dump_file = tmp_path / "env_dump.json"
    
    malicious_script = f"""
import os
import json
with open('{env_dump_file}', 'w') as f:
    json.dump(dict(os.environ), f)
"""
    script_path = tmp_path / "malicious.py"
    script_path.write_text(malicious_script)
    
    import sys
    # The command we want the bootstrap to execute:
    test_cmd = f"{sys.executable} {script_path}"
    
    # 3. Setup the parent environment with secrets
    env = os.environ.copy()
    env["SIGNING_SECRET"] = "super-secret-123"
    env["AWS_ACCESS_KEY_ID"] = "AKIAIOSFODNN7EXAMPLE"
    env["AWS_SECRET_ACCESS_KEY"] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    env["SNAPSHOT_URL"] = "https://s3.amazonaws.com/test/snap"
    env["PATCH_URL"] = "https://s3.amazonaws.com/test/patch"
    
    # Config for bootstrap itself so it doesn't fail parsing
    env["ATTEMPT_ID"] = str(uuid.uuid4())
    env["NONCE"] = "securenonce"
    env["EXPECTED_SNAPSHOT_HASH"] = "hash1"
    env["EXPECTED_PATCH_HASH"] = "hash2"
    env["RESULT_URL"] = "http://localhost:9999"
    
    # Instruct bootstrap to run this command
    env["TEST_COMMAND_OVERRIDE"] = test_cmd
    
    # 4. Run the bootstrap (it should error on HTTP upload, but the script runs first)
    res = subprocess.run([str(go_bin)], env=env, capture_output=True, text=True)
    
    # The HTTP call to localhost:9999 fails, but the subprocess ran!
    
    assert env_dump_file.exists(), f"Malicious script did not run or failed to write dump. stderr: {res.stderr}, stdout: {res.stdout}"
    
    # 5. Verify the actual child process environment
    dumped_env = json.loads(env_dump_file.read_text())
    
    assert "SIGNING_SECRET" not in dumped_env, "SIGNING_SECRET leaked to child!"
    assert "AWS_ACCESS_KEY_ID" not in dumped_env, "AWS_ACCESS_KEY_ID leaked to child!"
    assert "AWS_SECRET_ACCESS_KEY" not in dumped_env, "AWS_SECRET_ACCESS_KEY leaked to child!"
    assert "SNAPSHOT_URL" not in dumped_env, "SNAPSHOT_URL leaked to child!"
    assert "PATCH_URL" not in dumped_env, "PATCH_URL leaked to child!"
    
    # Also verify it got other benign vars (e.g., PATH)
    assert "PATH" in dumped_env
