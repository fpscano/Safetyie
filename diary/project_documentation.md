# Project Documentation

This document serves as a comprehensive overview of every aspect and element within the project, detailing their functions, interdependencies, and operational mechanics.

## Table of Contents

*   [Overall Project Structure](#overall-project-structure)
*   [Frontend Components](#frontend-components)
*   [Backend Functions (Cloudflare Workers)](#backend-functions-cloudflare-workers)
*   [Database (Cloudflare D1)](#database-cloudflare-d1)
*   [Authentication](#authentication)
*   [API Endpoints](#api-endpoints)
*   [Migration Scripts](#migration-scripts)
*   [Utility/Shared Modules](#utilityshared-modules)

---

## Overall Project Structure

The project "Cano" is structured to support a full-stack application, likely deployed on Cloudflare Workers, given the presence of `wrangler.toml` and a `functions` directory.

-   **Root Directory**: Contains static assets (`.html`, `styles.css`), project configuration (`package.json`, `wrangler.toml`, `_headers`), and documentation (`README.md`).
-   **`.claude/`**: Appears to be related to Claude AI agent configurations.
-   **`.git/`**: Standard Git version control directory.
-   **`.wrangler/`**: Cloudflare Wrangler's local development and build artifacts.
-   **`admin/`**: Contains administrative frontend components (`.html`, `.js`, `.css`) for managing clients and users.
-   **`dairy/`**: Holds project documentation, currently `project_documentation.md`.
-   **`functions/`**: Houses Cloudflare Worker functions, organized into shared modules and API endpoints.
    -   `_shared/`: Common utility modules like `audit.js`, `auth.js`, `password.js`.
    -   `api/v1/`: Versioned API endpoints, further categorized by domain (e.g., `engines`, `admin`, `auth`, `fleet`).
-   **`gemini/`**: Contains `init` file, likely for Gemini CLI initialization.
-   **`images/`**: Stores various image assets for the application.
-   **`migrations/`**: Contains SQL migration scripts for database schema management.
-   **`node_modules/`**: Standard Node.js dependency directory.
-   **`proc/`**: Appears to be a temporary or system-related directory.
-   **`tst/`**: Contains test-related files, potentially for development or temporary testing.

---

## Frontend Components

The project includes several static HTML files, CSS stylesheets, and JavaScript files that constitute the user-facing and administrative interfaces.

-   **`index.html`**: The main landing page of the application.
-   **`about.html`**: Provides information about the project or organization.
-   **`contact.html`**: A page for users to get in touch.
-   **`login.html`**: Handles user authentication and login processes.
-   **`styles.css`**: The main stylesheet for the general application.
-   **`admin/`**: A dedicated section for administrative functionalities.
    -   **`admin/index.html`**: The main dashboard or entry point for the admin panel.
    -   **`admin/clients.html`**: Page for managing client information.
    -   **`admin/users.html`**: Page for managing user accounts.
    -   **`admin/app.js`**: JavaScript logic for the admin panel's functionalities.
    -   **`admin/styles.css`**: Stylesheet specific to the admin interface.
-   **`tst/`**: Contains testing-related frontend files, possibly for isolated component testing or temporary development.
    -   **`tst/app.js`**: JavaScript file.
    -   **`tst/index.html`**: HTML file.
    -   **`tst/styles.css`**: CSS file.

---

## Backend Functions (Cloudflare Workers)

The backend logic is implemented using Cloudflare Workers, organized within the `functions/` directory. This structure suggests a serverless architecture where each JavaScript file within `api/v1` likely represents an individual API endpoint or a collection of related endpoints handled by a single worker.

-   **`functions/_shared/`**: Contains common utility modules or middleware that can be shared across different worker functions.
    -   **`audit.js`**: Likely handles logging or auditing of requests and actions.
    -   **`auth.js`**: Provides authentication related utilities, such as token validation or user session management.
    -   **`password.js`**: Likely contains functions for password hashing, validation, or other security-related password operations.
-   **`functions/api/v1/`**: Houses the version 1 of the application's API endpoints.
    -   **`engines.js`**: API routes related to managing engines.
    -   **`admin/`**: API routes specifically for administrative tasks.
        -   **`audit-log.js`**: Endpoints for accessing audit trails.
        -   **`client-users.js`**: Endpoints for managing users associated with specific clients.
        -   **`clients.js`**: Endpoints for managing client entities.
        -   **`users.js`**: Endpoints for general user management.
        -   **`client-users/[id].js`**: Dynamic routes for specific client users, likely by ID.
        -   **`clients/[code].js`**: Dynamic routes for specific clients, likely by a unique code.
        -   **`users/[id].js`**: Dynamic routes for specific users, likely by ID.
    -   **`auth/`**: API routes dedicated to user authentication flows.
        -   **`login.js`**: Handles user login requests.
        -   **`me.js`**: Endpoint to retrieve information about the currently authenticated user.
        -   **`ping.js`**: A simple endpoint to check API availability or session validity.
    -   **`engines/`**: Further organization for engine-related API routes.
        -   **`[engine].js`**: Dynamic routes for specific engines.
    -   **`fleet/`**: API routes for managing fleet-related entities.
        -   **`drivers.js`**: Endpoints for managing drivers.
        -   **`events.js`**: Endpoints for fleet-related events.
        -   **`vehicles.js`**: Endpoints for managing vehicles.

---

## Database (Cloudflare D1)

The project utilizes Cloudflare D1 as its database solution, evident from the presence of `wrangler.toml` (which configures Cloudflare resources) and the `migrations/` directory.

-   **Cloudflare D1**: A serverless SQL database provided by Cloudflare, offering SQLite compatibility. It's designed for global applications with low latency.
-   **`migrations/`**: Contains SQL scripts responsible for defining and evolving the database schema. These scripts ensure that the database structure is consistent across different environments and can be updated systematically.
    -   `0001_platform_tables.sql`: Initial migration for core platform-related tables.
    -   `0002_fleet_tables.sql`: Migration for tables related to fleet management.
    -   `0003_client_users.sql`: Migration for tables storing client and user relationships.
    -   `0004_engine_tables.sql`: Migration for tables related to engines.

---

## Authentication

Authentication in the project is handled by dedicated modules and API endpoints, centralizing login mechanisms and user session management.

-   **`functions/_shared/auth.js`**: This module likely contains core authentication logic, such as token validation, session creation, authorization checks, and utility functions for securing routes.
-   **`functions/api/v1/auth/`**: This directory exposes API endpoints related to authentication processes:
    -   **`login.js`**: An endpoint responsible for authenticating user credentials and issuing authentication tokens or sessions upon successful login.
    -   **`me.js`**: An endpoint allowing authenticated users to retrieve their own profile information, typically by validating their current session or token.
    -   **`ping.js`**: A utility endpoint often used to check the validity of an authentication token or session without retrieving full user data, or to simply verify the availability of the authentication service.

---

## API Endpoints

The project exposes a RESTful API under the `/api/v1/` path, implemented using Cloudflare Workers. Endpoints are organized by resource and provide various functionalities for managing the application's data and operations.

-   **Authentication Endpoints (`/api/v1/auth`)**:
    -   `POST /api/v1/auth/login`: Authenticates a user and returns a session token.
    -   `GET /api/v1/auth/me`: Retrieves the profile of the authenticated user.
    -   `GET /api/v1/auth/ping`: Checks the status of the authentication service or validates a token.
-   **Engine Endpoints (`/api/v1/engines`)**:
    -   `GET /api/v1/engines`: Retrieves a list of all engines.
    -   `GET /api/v1/engines/{engine}`: Retrieves details for a specific engine.
    -   `POST /api/v1/engines`: Creates a new engine (implied by `engines.js`).
    -   `PUT /api/v1/engines/{engine}`: Updates an existing engine (implied by `[engine].js`).
    -   `DELETE /api/v1/engines/{engine}`: Deletes an engine (implied by `[engine].js`).
-   **Admin Endpoints (`/api/v1/admin`)**:
    -   **Client Management (`/api/v1/admin/clients`)**:
        -   `GET /api/v1/admin/clients`: Retrieves a list of all clients.
        -   `GET /api/v1/admin/clients/{code}`: Retrieves details for a specific client by its code.
        -   `POST /api/v1/admin/clients`: Creates a new client.
        -   `PUT /api/v1/admin/clients/{code}`: Updates an existing client.
        -   `DELETE /api/v1/admin/clients/{code}`: Deletes a client.
    -   **User Management (`/api/v1/admin/users`)**:
        -   `GET /api/v1/admin/users`: Retrieves a list of all users.
        -   `GET /api/v1/admin/users/{id}`: Retrieves details for a specific user by ID.
        -   `POST /api/v1/admin/users`: Creates a new user.
        -   `PUT /api/v1/admin/users/{id}`: Updates an existing user.
        -   `DELETE /api/v1/admin/users/{id}`: Deletes a user.
    -   **Client-User Management (`/api/v1/admin/client-users`)**:
        -   `GET /api/v1/admin/client-users`: Retrieves a list of client-user associations.
        -   `GET /api/v1/admin/client-users/{id}`: Retrieves details for a specific client-user association by ID.
        -   `POST /api/v1/admin/client-users`: Creates a new client-user association.
        -   `PUT /api/v1/admin/client-users/{id}`: Updates an existing client-user association.
        -   `DELETE /api/v1/admin/client-users/{id}`: Deletes a client-user association.
    -   **Audit Log (`/api/v1/admin/audit-log`)**:
        -   `GET /api/v1/admin/audit-log`: Retrieves the audit trail or logs.
-   **Fleet Endpoints (`/api/v1/fleet`)**:
    -   `GET /api/v1/fleet/drivers`: Retrieves a list of drivers.
    -   `POST /api/v1/fleet/drivers`: Creates a new driver.
    -   `GET /api/v1/fleet/events`: Retrieves a list of fleet events.
    -   `POST /api/v1/fleet/events`: Creates a new fleet event.
    -   `GET /api/v1/fleet/vehicles`: Retrieves a list of vehicles.
    -   `POST /api/v1/fleet/vehicles`: Creates a new vehicle.

---

## Migration Scripts

The `migrations/` directory contains SQL scripts used for managing and versioning the database schema. These scripts are executed in order to apply changes to the database, ensuring consistency and allowing for schema evolution.

-   **`0001_platform_tables.sql`**: This script likely initializes the core tables required for the application's main platform functionalities.
-   **`0002_fleet_tables.sql`**: This script sets up tables specifically designed to store data related to fleet management, such as vehicles, drivers, or routes.
-   **`0003_client_users.sql`**: This script creates tables for managing clients and their associated users, defining relationships and user-specific data.
-   **`0004_engine_tables.sql`**: This script is responsible for creating tables that hold information about engines, possibly including specifications, status, or historical data.

---

## Utility/Shared Modules

The `functions/_shared/` directory contains JavaScript modules designed for reusability across different Cloudflare Worker functions. These modules encapsulate common logic, helping to maintain a DRY (Don't Repeat Yourself) principle and improve code organization.

-   **`audit.js`**: This module likely provides functions for logging events, actions, or changes within the application. It could be used to create an audit trail for security, compliance, or debugging purposes.
-   **`auth.js`**: This module centralizes authentication-related utilities. It might include functions for validating user tokens, handling session management, generating authentication responses, or providing helpers for protecting routes.
-   **`password.js`**: This module probably contains functions dedicated to secure password handling, such as hashing passwords before storage, verifying passwords during login, or generating secure random passwords.
