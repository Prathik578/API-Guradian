# API Reference

Welcome to the API Guardian Developer API. While our platform is designed to be fully autonomous, we understand that power users and large enterprises often need to integrate our capabilities directly into their own internal developer portals, CI/CD pipelines, or custom dashboards. 

## RESTful Architecture
Our API follows strict RESTful conventions. It uses standard HTTP verbs (GET, POST, PUT, DELETE, PATCH), returns predictable JSON-encoded responses, and utilizes standard HTTP response codes to indicate success or failure.

## Authentication
To interact with the API, you must authenticate using a Personal Access Token (PAT) or an Organization Service Token. 
Tokens must be included in the header of every request:
`Authorization: Bearer <your_token_here>`

## Rate Limiting
To ensure high availability for all users, API Guardian implements a sliding-window rate limit. By default, API requests are limited to 1,000 requests per minute per IP address, and 10,000 requests per minute per Organization. 

If you exceed this limit, the API will respond with a `429 Too Many Requests` status code. The response headers will include `X-RateLimit-Reset`, indicating the Unix timestamp when your quota will be replenished.

## Core Resources
The API exposes full CRUD access to the following core resources:
- `/api/v1/repositories`: Manage your connected source code repositories.
- `/api/v1/integrations`: Configure and monitor third-party connections like GitHub and Slack.
- `/api/v1/guarded-apis`: Add, remove, or configure the APIs you want to monitor.
- `/api/v1/cases`: Query the status of ongoing autonomous maintenance operations.

For detailed endpoint specifications, request schemas, and response examples, please refer to our interactive OpenAPI (Swagger) documentation available in your dashboard under the Developer Settings tab.
