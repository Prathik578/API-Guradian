# Known Limitations and Boundaries

Transparency is a core value at API Guardian. While our platform represents a massive leap forward in autonomous software engineering, it is not magic. It relies on deterministic parsing, statistical language models, and robust sandboxing. Therefore, there are specific boundaries and limitations you must be aware of when deploying API Guardian in production.

## 1. Complex State Mutations
API Guardian excels at translating API calls (e.g., changing a payload structure from `user.first_name` to `user.details.firstName`). However, if an upstream provider fundamentally redesigns their architecture—for example, moving from a synchronous REST endpoint to an asynchronous Webhook-driven event system—the LLM cannot redesign your entire application architecture. 

In these scenarios of fundamental architectural shifts, API Guardian will successfully identify the breaking change, calculate the blast radius, and generate the Provider Notice alert, but it will flag the Maintenance Case for "Manual Intervention," recognizing that human architectural decisions are required.

## 2. Incomplete Test Coverage
Our verification sandbox guarantees that the *existing* test suite passes against the new code. If your application has 15% code coverage, and the API interaction logic is untested, API Guardian cannot mathematically prove that the new logic won't break edge cases in production. 

**Garbage in, garbage out.** The platform is highly dependent on the quality of your existing unit and integration tests. We highly recommend maintaining at least 80% coverage on modules that interact with Guarded APIs.

## 3. Highly Obfuscated or Dynamic Code
Our impact analysis engine uses Abstract Syntax Tree (AST) parsing. While incredibly powerful, it struggles with highly dynamic language features (like extreme metaprogramming in Ruby or dynamic `eval()` calls in JavaScript). If an API endpoint URL is constructed dynamically at runtime by concatenating unpredictable strings from a database, the AST parser may fail to detect the dependency.

## 4. Proprietary or Undocumented APIs
API Guardian's mocking engine relies on publicly available OpenAPI specifications (Swagger). If an upstream provider relies on undocumented, proprietary endpoints, we cannot generate a deterministic mock server, which means the Verification Sandbox will fail to validate the patch.
