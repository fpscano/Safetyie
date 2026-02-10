# ✅ ARCHITECTURE CORRECTED - Single D1 Database Multi-Tenant Design

## Summary
The Safetyie platform uses a **SINGLE D1 database** (`sie-db`) for ALL clients. Each client's data is isolated using `client_id` filtering. This is the correct and efficient approach for a multi-tenant SaaS application.

---

## Current Configuration ✅

### Single D1 Database
**File:** `cano/wrangler.toml`
```toml
[[d1_databases]]
binding = "DB"
database_name = "sie-db"
database_id = "b3fe982e-d3d7-4cf9-8c6c-274ee5e4682a"
```

**Status:** ✅ CORRECT - Only ONE database configured

---

## How Multi-Tenancy Works

### Data Isolation by client_id

All client-specific data is filtered by `client_id`:

#### Example: Client Users Table
```sql
CREATE TABLE client_users (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,  -- ← This isolates each client
    email TEXT,
    role TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
```

#### Example: Vehicles Table
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,  -- ← This isolates each client
    vehicle_number TEXT,
    make TEXT,
    model TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
```

### Security Enforcement

**File:** `cano/functions/api/v1/engines/[engine].js` (lines 90-101)

```javascript
// Security: Client users can ONLY access their own client data
if (!authUser.isSIEUser) {
    // Override any client_id parameter with the authenticated user's client_id
    clientId = String(authUser.client_id);
}

// Verify access permission
if (!authUser.isSIEUser && authUser.client_id !== Number(clientId)) {
    return errorResponse('Access denied to this client data', 403);
}

// All queries filter by client_id
const rows = await env.DB.prepare(
    `SELECT * FROM ${table} WHERE client_id = ? ...`
).all(clientId);
```

**Result:**
- Client users see ONLY their own data
- SIE admin users can see ALL clients' data
- All enforced at the API level

---

## Authentication & Dashboard Flow

### 1. Client User Login Flow

**Endpoint:** `POST /api/v1/auth/login`

1. User enters company code (e.g., "TESTCLIENT")
2. System validates company code and returns `client_id`
3. User enters email/password
4. System validates credentials for that `client_id`
5. JWT token issued with `client_id` embedded
6. User redirected to `/client-dashboard.html`
7. Dashboard fetches data for their `client_id` only

**localStorage saved:**
- `sie_token` - JWT with client_id
- `sie_user` - User info
- `client_id` - Client ID for quick access

### 2. SIE Admin Login Flow

**Endpoint:** `POST /api/v1/auth/admin-login`

1. User enters username/email and password
2. System validates against `users` table (not `client_users`)
3. JWT token issued with `user_type: 'sie'`
4. User redirected to `/admin-dashboard.html`
5. Admin dashboard shows ALL clients
6. Admin can click any client to view their dashboard

### 3. Admin Viewing Client Dashboard

**URL Pattern:** `/client-dashboard.html?client=CLIENTCODE`

When admin clicks a client:
1. URL includes `?client=TESTCLIENT` query parameter
2. Client dashboard detects admin view mode
3. Fetches `client_id` from client code
4. Displays data for that specific client
5. Shows "Back to Admin" button

**Code:** `website/client-dashboard.html` (lines 372-389)
```javascript
const clientCodeParam = urlParams.get('client');

if (clientCodeParam && token) {
    isAdminView = true;
    // Fetch client data for admin
    const clientResponse = await fetch(`${API_BASE}/admin/clients/${clientCodeParam}`);
    clientId = clientData.id;
}
```

---

## Simplified Admin Dashboard

### Before (Complex)
- Multiple navigation sections
- Downloads section
- SIE Admin Control
- Static welcome message

### After (Bare Bones) ✅
- **Grid of all clients**
- **Click any client → View their dashboard**
- **Clean and focused**

**File:** `website/admin-dashboard.html`

The admin dashboard now:
1. Fetches all clients from `GET /api/v1/admin/clients`
2. Displays them in a clickable grid
3. Each click redirects to `client-dashboard.html?client=CODE`
4. Simple and efficient

---

## Engine Data Storage

### Engine Score Tables (All in Single D1)

All engine scores are stored in the **same database** with `client_id` filtering:

```sql
-- Hours of Service Intelligence Engine
CREATE TABLE hie_scores (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    driver_id INTEGER,
    score INTEGER,
    computed_at TEXT
);

-- Event Intelligence Engine
CREATE TABLE eie_scores (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    vehicle_id INTEGER,
    score INTEGER,
    computed_at TEXT
);

-- Same pattern for: fie_scores, tie_scores, dvirie_scores, wie_scores, pie_scores, sie_scores
```

### API Endpoints for Engines

**GET** `/api/v1/engines/{engine}?client_id=X`

**Supported engines:**
- `hie` - Hours of Service Intelligence
- `eie` - Event Intelligence Engine
- `fie` - Fault Intelligence Engine
- `tie` - Telematics Intelligence Engine
- `dvirie` - Driver Vehicle Inspection Reporting Intelligence Engine
- `wie` - Weather Intelligence Engine
- `pie` - Predictive Intelligence Engine
- `sie` - Safety Intelligence Engine (overall score)

**Example Request:**
```javascript
// Client dashboard fetches SIE score
const response = await fetch(`/api/v1/engines/sie?client_id=5`, {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

**Security:**
- Client users: `client_id` is automatically set from their JWT token (cannot access other clients)
- SIE admin users: Can specify any `client_id` to view

---

## What About Multiple D1 Databases?

### The Problem
If Gemini attempted to create separate D1 databases for each client, this would be:
- ❌ Inefficient (database per client)
- ❌ Expensive (D1 pricing per database)
- ❌ Complex (managing multiple database bindings)
- ❌ Difficult to maintain (schema changes across many DBs)

### The Solution ✅
**Single database with client_id filtering:**
- ✅ Efficient (one database for all clients)
- ✅ Cost-effective (one D1 database charge)
- ✅ Simple (single schema, single migration path)
- ✅ Scalable (can handle thousands of clients)
- ✅ Secure (row-level security via client_id)

### If Extra D1 Databases Exist

Check Cloudflare Dashboard:
1. Go to https://dash.cloudflare.com/
2. Navigate to **Workers & Pages** → **D1**
3. Look for databases other than `sie-db`
4. **Delete any client-specific databases** (e.g., "testclient-db", "safeclient-db")

**Only keep:**
- `sie-db` (ID: b3fe982e-d3d7-4cf9-8c6c-274ee5e4682a)

---

## Current Client Data in Single D1

All these clients exist in the **SAME DATABASE** (`sie-db`):

| client_id | client_code | client_name |
|-----------|-------------|-------------|
| 1 | SIE | SIE Internal Company |
| 2 | TESTCLIENT | Test Client Corp |
| 3 | SAFECLIENT | Safe Client Inc |
| 4 | FASTCLIENT | Fast Logistics |
| 5 | HORRIBLE | Horrible Transport |
| 6 | SIEMIX | SIE Mix Company |

**Verify with:**
```bash
cd cano
npx wrangler d1 execute sie-db --remote --command "SELECT id, client_code, client_name FROM clients;"
```

---

## Deployment Process

### 1. Verify Configuration
```bash
cd cano
cat wrangler.toml
# Should show ONLY one [[d1_databases]] section
```

### 2. Deploy to Cloudflare Pages
```bash
cd cano
npx wrangler pages deploy --project-name=sie
```

### 3. Verify D1 Binding in Dashboard
1. Go to Cloudflare Dashboard
2. **Workers & Pages** → **sie** → **Settings** → **Functions**
3. Verify D1 database binding exists:
   - **Variable name:** DB
   - **D1 database:** sie-db
4. If missing, add it and redeploy

---

## Testing the Architecture

### Test 1: Client User Login
1. Go to https://sie-ebe.pages.dev/client_login.html
2. Enter company code: **TESTCLIENT**
3. Enter email: **manager@testclient.com**
4. Enter password: **manager123**
5. Should redirect to client dashboard
6. Should see ONLY TESTCLIENT data

### Test 2: Admin Login
1. Go to https://sie-ebe.pages.dev/admin-login.html
2. Enter email: **admin@sie.com**
3. Enter password: **admin123**
4. Should redirect to admin dashboard
5. Should see grid of ALL clients

### Test 3: Admin Viewing Client Dashboard
1. From admin dashboard, click any client (e.g., TESTCLIENT)
2. Should redirect to `/client-dashboard.html?client=TESTCLIENT`
3. Should show TESTCLIENT dashboard
4. Should see "Back to Admin" button
5. Should display engines data for that client

### Test 4: Data Isolation
```bash
# Check that each client has their own vehicles
cd cano
npx wrangler d1 execute sie-db --remote --command \
  "SELECT client_id, COUNT(*) as vehicle_count FROM vehicles GROUP BY client_id;"
```

Expected:
```
client_id | vehicle_count
----------|---------------
2         | 5
3         | 3
4         | 4
```

Each client sees only their vehicles, but all stored in one database.

---

## Key Takeaways

1. ✅ **Single D1 Database** - `sie-db` is the ONLY database needed
2. ✅ **Multi-Tenant Architecture** - All clients share the database
3. ✅ **Row-Level Security** - `client_id` filtering enforces isolation
4. ✅ **Admin Dashboard Simplified** - Just shows client grid
5. ✅ **Client Dashboard** - Works for both direct access and admin view
6. ✅ **Engine Data** - All stored in same DB, filtered by `client_id`

---

## If Something Is Broken

### Symptom: Client dashboard shows no data
**Check:**
1. Is `client_id` saved in localStorage?
   - Open browser console (F12)
   - Run: `localStorage.getItem('client_id')`
   - Should show a number

2. Does the client have engine data?
   ```bash
   npx wrangler d1 execute sie-db --remote --command \
     "SELECT * FROM sie_scores WHERE client_id = 2 LIMIT 5;"
   ```

### Symptom: Admin can't view client dashboards
**Check:**
1. Is the admin logged in with SIE credentials?
2. Does the JWT token have `user_type: 'sie'`?
3. Is the client code correct in the URL?

### Symptom: "Database not available" error
**Check:**
1. Is D1 binding configured in Cloudflare Dashboard?
2. Is wrangler.toml correct?
3. Redeploy after fixing configuration

---

## Next Steps

1. ✅ **Verify** - Only one D1 database exists (sie-db)
2. ✅ **Delete** - Remove any extra client-specific D1 databases
3. ✅ **Deploy** - `npx wrangler pages deploy --project-name=sie`
4. ✅ **Test** - Login as client user and admin user
5. ✅ **Confirm** - Data isolation working correctly

---

**Status:** ✅ Architecture is correct and optimal for multi-tenant SaaS
**Last Updated:** 2026-02-09
**Configuration:** Single D1 database with client_id filtering
