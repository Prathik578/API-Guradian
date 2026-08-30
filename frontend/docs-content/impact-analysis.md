# Impact Analysis: Calculating the Blast Radius

When a third-party API provider announces a breaking change, the first and most critical question an engineering team asks is: "How much of our code is going to break?" In traditional software development, answering this question requires days of manual `grep` searches, reading documentation, and holding stressful alignment meetings. 

API Guardian answers this question deterministically, autonomously, and within seconds through its advanced **Impact Analysis** engine. 

## Moving Beyond Text Search
Simple text searches (like looking for `stripe.charges.create`) are fundamentally flawed for impact analysis. They suffer from:
- **False Positives:** A string might exist in a comment, a test fixture, or a completely unrelated module.
- **False Negatives:** The API call might be wrapped in a generic helper function (`makePayment(payload)`), masking the direct dependency from a simple text search.

API Guardian does not use text search. Instead, it relies on deep Abstract Syntax Tree (AST) parsing. 

## The AST Graph Construction
When you connect a repository to API Guardian, our ingestion engine clones the code and parses it into a massive, multi-dimensional AST graph. This graph maps every file, class, function, and variable assignment. Crucially, it traces data flow and module imports. 

If you have a file `utils/payment.js` that imports the `stripe` SDK, and then a file `controllers/checkout.js` that imports a function from `utils/payment.js`, our AST graph understands that `checkout.js` has a transitive dependency on the Stripe API.

## Calculating the Blast Radius
When a Provider Notice is ingested, our NLP models extract the specific API endpoints and methods that are changing. The Impact Analysis engine then queries your repository's AST graph against these specific endpoints. 

The engine calculates the **Blast Radius**, tracing the impact from the specific line of code that makes the HTTP request, all the way up through the call stack to the top-level controllers or API routes in your application.

## Actionable Intelligence
The result of this analysis is presented in the dashboard as a highly visual, actionable report. Before a single line of migration code is generated, you can see exactly which files and functions are affected. This deterministic mapping guarantees that the subsequent LLM generation phase knows exactly where to apply patches, eliminating the risk of missed dependencies or incomplete migrations.
