package main

import (
	"fmt"
	"os"
)

type Config struct {
	SnapshotURL          string
	PatchURL             string
	ResultURL            string
	ExpectedSnapshotHash string
	ExpectedPatchHash    string
	AttemptID            string
	Nonce                string
	SigningSecret        string
}

func LoadConfig() (*Config, error) {
	cfg := &Config{
		SnapshotURL:          os.Getenv("SNAPSHOT_URL"),
		PatchURL:             os.Getenv("PATCH_URL"),
		ResultURL:            os.Getenv("RESULT_URL"),
		ExpectedSnapshotHash: os.Getenv("EXPECTED_SNAPSHOT_HASH"),
		ExpectedPatchHash:    os.Getenv("EXPECTED_PATCH_HASH"),
		AttemptID:            os.Getenv("ATTEMPT_ID"),
		Nonce:                os.Getenv("NONCE"),
		SigningSecret:        os.Getenv("SIGNING_SECRET"),
	}

	if cfg.SnapshotURL == "" || cfg.ResultURL == "" {
		return nil, fmt.Errorf("missing required environment variables")
	}

	// Delete secrets from environment so child processes don't see them
	os.Unsetenv("SNAPSHOT_URL")
	os.Unsetenv("PATCH_URL")
	os.Unsetenv("RESULT_URL")
	os.Unsetenv("SIGNING_SECRET")

	return cfg, nil
}
