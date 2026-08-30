# AWS Runtime Environment

To provide the highest level of security and deterministic isolation during the verification process, API Guardian relies heavily on specialized AWS infrastructure. This document outlines how our AWS Runtime Environment is structured and secured.

## AWS Fargate for Serverless Compute
The backbone of our verification engine is AWS Fargate. Unlike traditional EC2 instances where multiple tenants might share a virtual machine, Fargate provides true serverless containers. 

When a test suite needs to be run against a generated patch, we define a Fargate Task Definition on the fly. This task specifies the exact Docker image required for your repository's runtime (e.g., Node.js 20, Python 3.12, or Go 1.21). Fargate provisions the compute resources instantly, executes the task, and tears down the infrastructure the second the task completes.

## Network Isolation (VPC Architecture)
Our Fargate tasks run in a highly restricted Virtual Private Cloud (VPC). 
- **Private Subnets Only:** Verification tasks are launched in private subnets with no Route to an Internet Gateway (IGW).
- **No NAT Gateway:** There is no NAT Gateway attached to these subnets. This guarantees that the executing code physically cannot establish an outbound connection to the public internet, preventing data exfiltration.
- **Strict Security Groups:** The Security Groups attached to the tasks deny all inbound traffic and only permit outbound traffic to specific, internal VPC Endpoints required for logging (CloudWatch) and artifact retrieval (S3).

## IAM Least Privilege
Every Fargate task assumes an AWS Identity and Access Management (IAM) Task Role. This role is dynamically generated and strictly scoped following the principle of least privilege. The task can only read from the specific S3 bucket prefix containing your repository clone and can only write to the specific S3 bucket prefix designated for its verification logs. It has absolutely zero access to the control plane database or any other tenant's resources.

By leveraging the deepest layers of AWS security, API Guardian guarantees that your code is evaluated in an environment that is both pristine and impenetrable.
