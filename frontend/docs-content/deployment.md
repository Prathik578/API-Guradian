# Deployment Strategies

While API Guardian is primarily offered as a fully managed SaaS (Software as a Service) platform, we understand that highly regulated enterprises may have strict data residency and sovereignty requirements. Therefore, we offer multiple deployment models to accommodate different operational security postures.

## 1. Public Cloud SaaS (Standard)
This is the default and most popular deployment model. Your data resides securely within API Guardian's multi-tenant AWS infrastructure. We handle all patching, scaling, database maintenance, and uptime monitoring. You benefit from zero infrastructure overhead and instant access to the latest NLP models and AST parsing algorithms. Tenant isolation is strictly enforced via PostgreSQL Row-Level Security (RLS) and IAM boundaries.

## 2. Virtual Private Cloud (VPC) Peering
For organizations that require tighter network control but still want a managed experience, we offer VPC Peering. In this model, API Guardian is still hosted in our AWS accounts, but we establish a dedicated, private network connection (VPC Peer or AWS PrivateLink) directly to your AWS environment. 

This allows API Guardian's worker nodes to access internal, private GitHub Enterprise Server instances or self-hosted GitLab repositories without that traffic ever traversing the public internet.

## 3. Dedicated Single-Tenant Cluster (Enterprise)
For enterprises with extreme compliance requirements, we offer Dedicated Clusters. We deploy a completely isolated instance of the entire API Guardian control plane, intelligence engine, and execution sandbox into a dedicated AWS account. There is no shared database and no shared compute. You have total control over the region where the data resides, ensuring compliance with strict data localization laws.

## 4. On-Premises / Bring Your Own Cloud (BYOC)
In rare circumstances where code cannot leave your physical or logical perimeter under any circumstances, API Guardian can be deployed via Kubernetes Helm charts directly into your own AWS, GCP, or Azure environment. In this BYOC model, the NLP models and LLM generation still require outbound API calls to our secure AI gateways, but the source code, AST parsing, and verification sandboxes run entirely within your controlled infrastructure.

Contact our enterprise sales team to discuss which deployment model aligns best with your security architecture.
