package main

type VerificationPlan struct {
	TestCommand        string            `json:"test_command"`
	TestInventory      map[string]string `json:"test_inventory"`
	ConfigFileHashes   map[string]string `json:"config_file_hashes"`
	BaselineTestCount  int               `json:"baseline_test_count"`
	BaselineSkipCount  int               `json:"baseline_skip_count"`
}

func CaptureVerificationPlan(workspacePath string) (*VerificationPlan, error) {
	// TODO: Discover test command, hash configs, discover tests
	return &VerificationPlan{
		TestCommand:      "make test", // dummy
		TestInventory:    make(map[string]string),
		ConfigFileHashes: make(map[string]string),
	}, nil
}
