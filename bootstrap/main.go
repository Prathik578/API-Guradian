package main

import (
	"fmt"
	"os"
)

func main() {
	fmt.Println("API Guardian Sandbox Bootstrap v0.1.0 starting...")

	cfg, err := LoadConfig()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Configuration error: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Executing verification attempt: %s\n", cfg.AttemptID)

	// Step 1: Download snapshot & patch
	// Step 2: Extract to /workspace/baseline
	// Step 3: Run baseline, capture plan
	plan, err := CaptureVerificationPlan("/workspace/baseline")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to capture baseline plan: %v\n", err)
		os.Exit(1)
	}

	// Step 4: Extract to /workspace/patched, apply patch
	// Step 5: Patch Audit
	audit, err := PerformPatchAudit(plan, "/workspace/patched")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Audit failed: %v\n", err)
		os.Exit(1)
	}

	// Step 6: Patched verification execution
	// Step 7: Gather result
	
	result := &VerificationResult{
		AttemptID:            cfg.AttemptID,
		Nonce:                cfg.Nonce,
		SnapshotHash:         cfg.ExpectedSnapshotHash,
		PatchHash:            cfg.ExpectedPatchHash,
		BaselineExitCode:     0,
		PatchedExitCode:      0,
		AuditPassed:          audit.Passed,
		AuditFailureReasons:  audit.Reasons,
		ResultClassification: "verified",
	}
	
	if !audit.Passed {
		result.ResultClassification = "audit_failed"
	}

	if err := SignAndUploadResult(result, cfg.ResultURL, cfg.SigningSecret); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to upload result: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Verification complete.")
	os.Exit(0)
}
