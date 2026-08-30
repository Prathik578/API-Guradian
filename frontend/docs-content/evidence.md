# Cryptographic Evidence and Attestation

The primary barrier to adopting AI-generated code in enterprise environments is trust. How do you know the LLM didn't hallucinate a variable name? How do you know it didn't accidentally remove a critical security check? 

API Guardian overcomes this barrier by attaching **Cryptographic Evidence** to every single Pull Request it generates. We do not just ask for your trust; we provide mathematical proof.

## The Verification Payload
When the Verification Sandbox completes its execution of your test suite against the generated patch, it compiles a comprehensive "Verification Payload". This JSON document contains:
- The exact `git diff` that was applied.
- The standard output (stdout) and standard error (stderr) of the test runner.
- The exit code of the test suite (must be `0` for success).
- Memory and CPU consumption metrics collected via eBPF.
- The specific versions of the mocked APIs that were simulated.
- A precise timestamp of the execution.

## HSM-Backed Digital Signatures
Once the payload is compiled, it is cryptographically signed using a Hardware Security Module (HSM). API Guardian maintains a unique, rotating Private Key for your organization, securely locked inside AWS KMS (Key Management Service). 

The payload is hashed using SHA-256, and that hash is signed by the KMS key. The resulting digital signature is then attached to the Pull Request as a comment, along with the raw payload data.

## Verifying the Evidence
Anyone in your organization can take the Verification Payload and the public key provided in your dashboard to independently verify the signature. 

If even a single character in the patch was altered after the verification process, or if the test logs were tampered with, the cryptographic signature will fail validation. This ensures absolute integrity. When a reviewer sees the green checkmark indicating a valid API Guardian signature, they have mathematical certainty that the exact code in the PR passed the test suite in a clean, isolated environment.
