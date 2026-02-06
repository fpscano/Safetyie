# API Key Management Strategy

This document outlines the secure strategy for managing API keys within the project. It is crucial to understand that **API keys should never be committed directly into the codebase or stored in plain text files within the project directory due to severe security risks.**

## Why Not Store API Keys in Files?

Storing API keys directly in files poses several significant risks:
-   **Accidental Exposure:** They can easily be exposed through version control systems (e.g., Git repositories), misconfigured servers, or during deployment.
-   **Security Breaches:** If the codebase is compromised, all hardcoded API keys become immediately vulnerable.
-   **Lack of Flexibility:** Changing an API key requires code modification and redeployment across all environments.

## Recommended Secure Storage Methods

For this project, given its likely deployment on Cloudflare Workers, the following secure methods are recommended for managing API keys:

1.  **Environment Variables:**
    -   For local development, API keys can be stored as environment variables on your local machine.
    -   When deploying to Cloudflare Workers, environment variables (or "Secrets") can be configured directly through the Cloudflare dashboard or `wrangler.toml` file without exposing their values in your source code.

2.  **Cloudflare Secrets (using `wrangler.toml`):**
    -   Cloudflare Workers allow you to bind "secrets" (sensitive environment variables) to your worker. These are stored securely by Cloudflare and injected at runtime.
    -   You define the *name* of the secret in `wrangler.toml` (e.g., `vars = { API_KEY = "VALUE_FROM_CLOUDFLARE_DASHBOARD" }`) and then set its actual value securely via the Cloudflare dashboard or `wrangler secret put API_KEY`.

3.  **Dedicated Secret Management Services:**
    -   For more complex needs or multi-cloud environments, consider using dedicated secret management services such as AWS Secrets Manager, Google Secret Manager, Azure Key Vault, or HashiCorp Vault.

## How to Access and Use API Keys in the Project

Developers should access API keys through the environment variables provided by the runtime environment.

### In Cloudflare Workers (JavaScript/TypeScript):

```javascript
// Access an API key set as an environment variable (or secret)
const myApiKey = env.MY_API_KEY;

// Use the API key in your code
fetch('https://api.example.com/data', {
    headers: {
        'Authorization': `Bearer ${myApiKey}`
    }
});
```

Here, `env` is the `Env` object passed to your Worker's `fetch` handler, which contains the configured environment variables/secrets.

### During Local Development:

-   Ensure your local development setup emulates the Cloudflare Worker environment or provides a mechanism to load environment variables (e.g., using a `.env` file with a tool like `dotenv` for Node.js projects, ensuring `.env` is in `.gitignore`).
-   For `wrangler` local development, you can define `vars` in your `wrangler.toml` under a `[vars]` section for local testing, or use `--env` flags when running `wrangler dev`.

**Example `wrangler.toml` (for local development variables):**

```toml
name = "my-worker"
main = "src/index.js"
compatibility_date = "2023-01-01"

[vars]
MY_API_KEY = "local_dev_api_key_12345"
```

**Remember:** Always treat API keys as highly sensitive information and follow these guidelines rigorously.

---

## NOTE: Setting up a Client and SIE Admin User for Testing

Since the admin pages have been removed, you will need to manually set up a client and a client user to test the new `client_login.html` flow. This can be done via direct database interaction or by utilizing existing API endpoints (if available for client/client user creation by platform admins).

**Recommended Setup Steps for Testing:**

1.  **Create a Client:**
    *   You'll need an entry in the `clients` table. You can use a tool like `wrangler d1 execute <YOUR_DB_NAME> --command "INSERT INTO clients (client_code, client_name, is_active) VALUES ('YOUR_COMPANY_CODE', 'Your Company Name', 1);"`
    *   Replace `<YOUR_DB_NAME>` with your D1 database name and `YOUR_COMPANY_CODE` with your desired company code (e.g., 'SIE123').

2.  **Create an SIE Admin User (Client User):**
    *   Once you have a `client_id` (from the client you just created), you'll need to create a `client_user` for it. This user will act as your "SIE Admin" for that specific company.
    *   You can create a `client_user` with the `manager` role using a command similar to:
        `wrangler d1 execute <YOUR_DB_NAME> --command "INSERT INTO client_users (client_id, email, password_hash, first_name, last_name, role, is_active) VALUES (<CLIENT_ID>, 'admin@yourcompany.com', '<HASHED_PASSWORD>', 'Admin', 'User', 'manager', 1);"`
    *   Replace `<CLIENT_ID>` with the `id` of the client you created.
    *   For `<HASHED_PASSWORD>`, you'll need to generate a PBKDF2 hash of your desired password (e.g., "securepassword123"). You could potentially use a small script using the `password.js` functions locally to generate this hash if direct D1 insertion is done manually.
    *   Alternatively, if you have other ways to create clients/client users (e.g., an existing platform admin API endpoint), use those.

**After these steps, you can use the `YOUR_COMPANY_CODE` and `admin@yourcompany.com` with `securepassword123` (or whatever you set) to test the new `client_login.html` page.**