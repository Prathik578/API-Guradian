# Deployment

API Guardian's production deployment targets AWS utilizing managed services.

## Infrastructure Map
- **Compute**: API Backend and Celery workers are hosted on Amazon Elastic Container Service (ECS) with AWS Fargate.
- **Database**: Amazon Relational Database Service (RDS) for PostgreSQL.
- **Caching & Brokers**: Amazon ElastiCache (Redis) serves as the Celery message broker and application cache.
- **Storage**: Amazon S3 is utilized for storing large payload artifacts, verification plans, and evidence payloads.

## Deployment Pipeline
1. Docker images are built and pushed to Amazon ECR.
2. Infrastructure definitions (Terraform/CDK) deploy updates.
3. Database migrations (Alembic) are executed prior to new application tasks starting.
