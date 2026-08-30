# Replacement Mapping: The LLM Blueprint

When a third-party API introduces a breaking change, the migration is rarely a simple 1:1 string replacement. Data structures are nested differently, field names change from snake_case to camelCase, authentication tokens move from the body to the headers, and pagination mechanisms completely alter. 

API Guardian handles this complexity through a sophisticated intermediate step known as **Replacement Mapping**.

## The Abstraction Layer
Instead of asking the Large Language Model (LLM) to blindly "fix the code," API Guardian first asks the intelligence engine to generate a Replacement Map. This is a highly structured, machine-readable JSON document that maps the exact differences between the old OpenAPI schema and the new OpenAPI schema.

For example, a Replacement Map might dictate:
- `Request.Body.user_id` -> `Request.Path.userId`
- `Response.Data.created` (Unix Epoch Integer) -> `Response.Data.createdAt` (ISO 8601 String)
- `Endpoint.Method: POST` -> `Endpoint.Method: PUT`

## AST Transformation Integration
Once the Replacement Map is finalized, it is fed into the code generation engine alongside the Abstract Syntax Tree (AST) of your application code. 

Because the AST understands the semantic structure of your code—it knows what is a function call, what is a variable assignment, and what is a dictionary key—the LLM can apply the Replacement Map with surgical precision. It knows exactly where to change the key in a payload dictionary without accidentally modifying a similarly named variable elsewhere in the file.

## Handling Type Coercion and Logic Shifts
The true power of Replacement Mapping becomes apparent when data types change. If a provider changes a field from an Integer to a String, a simple regex replace would break your application at runtime. 

The Replacement Map explicitly declares this type shift. The LLM reads this and knows that it must insert type coercion logic (e.g., wrapping the variable in `String()` or `parseInt()`) into the generated patch. If the logic shift is more profound—such as moving from synchronous polling to asynchronous webhooks—the Replacement Map outlines the architectural delta, guiding the LLM to generate entirely new handler functions and router configurations.

By abstracting the migration strategy into a declarative Replacement Map before writing any code, API Guardian ensures that the resulting patches are logical, structurally sound, and syntactically flawless.
