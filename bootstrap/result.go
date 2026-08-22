package main

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type VerificationResult struct {
	AttemptID              string   `json:"attempt_id"`
	Nonce                  string   `json:"nonce"`
	SnapshotHash           string   `json:"snapshot_hash"`
	PatchHash              string   `json:"patch_hash"`
	BaselineExitCode       int      `json:"baseline_exit_code"`
	PatchedExitCode        int      `json:"patched_exit_code"`
	PatchedTestCount       int      `json:"patched_test_count"`
	PatchedSkipCount       int      `json:"patched_skip_count"`
	AuditPassed            bool     `json:"audit_passed"`
	AuditFailureReasons    []string `json:"audit_failure_reasons"`
	ResultClassification   string   `json:"result_classification"`
	StdoutHash             string   `json:"stdout_hash"`
	StderrHash             string   `json:"stderr_hash"`
	Timestamp              string   `json:"timestamp"`
}

func SignAndUploadResult(result *VerificationResult, resultURL string, signingSecret string) error {
	data, err := json.Marshal(result)
	if err != nil {
		return err
	}

	mac := hmac.New(sha256.New, []byte(signingSecret))
	mac.Write(data)
	signature := hex.EncodeToString(mac.Sum(nil))

	req, err := http.NewRequest("PUT", resultURL, bytes.NewBuffer(data))
	if err != nil {
		return err
	}
	
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Guardian-Signature", signature)
	req.Header.Set("X-Guardian-Timestamp", time.Now().UTC().Format(time.RFC3339))

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("failed to upload result, status code: %d", resp.StatusCode)
	}

	return nil
}
