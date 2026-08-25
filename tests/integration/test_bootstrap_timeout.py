"""Phase 23X: Subprocess Resource Safety Proof."""

import os
import subprocess
import uuid
from pathlib import Path

def test_real_bootstrap_hang_is_killed(tmp_path):
    """Prove that the Go bootstrap kills hanging child processes."""
    
    bootstrap_dir = Path("/home/prathik/Documents/Antigravity/bootstrap")
    go_bin = tmp_path / "bootstrap_bin"
    build_cmd = ["go", "build", "-o", str(go_bin), "."]
    res = subprocess.run(build_cmd, cwd=bootstrap_dir, capture_output=True, text=True)
    assert res.returncode == 0, f"Failed to build Go bootstrap: {res.stderr}"
    
    malicious_script = "import time\nwhile True:\n    time.sleep(1)\n"
    script_path = tmp_path / "hang.py"
    script_path.write_text(malicious_script)
    
    import sys
    test_cmd = f"{sys.executable} {script_path}"
    
    env = os.environ.copy()
    env["ATTEMPT_ID"] = str(uuid.uuid4())
    env["NONCE"] = "securenonce"
    env["EXPECTED_SNAPSHOT_HASH"] = "hash1"
    env["EXPECTED_PATCH_HASH"] = "hash2"
    env["RESULT_URL"] = "http://localhost:9999"
    env["TEST_COMMAND_OVERRIDE"] = test_cmd
    
    # We expect this to run for 2 seconds and be killed by context deadline in Go
    # We use a python timeout of 5 seconds to ensure it doesn't hang the test suite.
    try:
        res = subprocess.run([str(go_bin)], env=env, capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        assert False, "Go bootstrap failed to enforce its timeout; python test suite had to kill it!"
    
    # The Go bootstrap should exit with 1 because the upload to localhost:9999 fails,
    # but more importantly, we want to see it didn't hang.
    assert res.returncode != 0
