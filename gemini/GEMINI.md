# Project: Safety Intelligence Engine (SIE)

## Project Overview

This project is the Safety Intelligence Engine (SIE), a full-stack web application. It consists of a public-facing frontend and a Cloudflare Workers/Pages backend with a D1 database. The `website/` directory contains the static HTML, CSS, and image assets for the user interface, while the `cano/` directory houses the backend logic, including Cloudflare Functions (API endpoints), database migrations, and utility scripts.

## Building and Running

The project leverages Cloudflare Pages and Workers for deployment and local development.

### Local Development

To run the backend and serve the website locally:

```bash
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
.\test-local.ps1
```

### Deployment

To deploy the application to Cloudflare Pages:

```bash
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler pages deploy ./ --project-name=sie
```

### Database Access

To interact with the remote D1 database:

```bash
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler d1 execute sie-db --remote --command "SELECT * FROM clients;"
```

## Development Conventions

*   **Frontend Development:** Frontend files (HTML, CSS, images) are located in the `website/` directory. Changes to the UI or new pages should be made here.
*   **Backend Development:** Backend logic, including API endpoints, database operations, and deployment configurations, is managed within the `cano/` directory.
    *   API endpoints are defined in `cano/functions/`.
    *   Database schema changes are handled via migrations in `cano/migrations/`.
*   **Version Control:** The primary Git repository is located within the `cano/` directory.
*   **Personal Notes:** The `diary/` directory is intended for personal development notes, ideas, and progress tracking.
*   **AI Agent Configurations:** The `.claude/` directory contains configurations for Claude AI agents, including those for database engineering and deployment.

## Login Credentials (for development/testing)

*   **Company Code:** SIE (case-insensitive)
*   **Email:** admin@sie.com
*   **Password:** admin123
