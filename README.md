# API Guardian

Autonomous software maintenance platform for third-party API dependencies.

## Architecture & Design Specifications

- [System Architecture](./ARCHITECTURE.md)
- [Repository & Code Architecture](./CODE_ARCHITECTURE.md)

## Development Setup

```bash
# Set up Python virtual environment & dependencies
make setup

# Run local infrastructure (Postgres, Redis, LocalStack, Squid Proxy)
docker-compose up -d

# Run tests
make test
```
