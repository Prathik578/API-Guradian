# Architecture Overview

API Guardian is a highly distributed, resilient, and secure system designed to handle the massive computational load of continuously parsing thousands of ASTs, generating code via Large Language Models, and running thousands of parallel verification sandboxes.

## The Control Plane
At the heart of the system is the Control Plane, built on a high-performance ASGI Python framework (FastAPI). The Control Plane is responsible for:
- Managing the REST API and serving the frontend dashboard.
- Handling Authentication and Authorization (RBAC).
- Orchestrating asynchronous workflows via a distributed message queue (Redis/Celery).
- Persisting state in a highly available PostgreSQL cluster utilizing Row-Level Security (RLS) for absolute tenant isolation.

## The Intelligence Engine
The Intelligence Engine operates independently from the Control Plane. It consists of fleet of specialized worker nodes that continuously ingest data from upstream providers. These nodes utilize NLP models to parse changelogs, classify the severity of notices, and extract structured metadata from unstructured text.

## The Execution Plane (AWS Fargate)
When a migration patch needs to be generated and verified, the work is pushed to the Execution Plane. This is where API Guardian leverages serverless container technology (AWS Fargate). 

For every verification job, a pristine, ephemeral container is launched. This container is completely isolated from the internet (Zero-Network policy) and from other tenants. It clones your code, applies the patch, spins up a local mock server based on the provider's OpenAPI spec, runs your test suite, and then destroys itself entirely. 

## The Frontend Layer
The user interface is a modern, responsive Single Page Application (SPA) built with Next.js and React. It communicates entirely via the REST API and utilizes WebSockets for real-time updates regarding ongoing maintenance cases, verification statuses, and new provider notices.

This separation of concerns ensures that API Guardian can scale horizontally to meet the demands of any enterprise, while maintaining an impregnable security posture.
