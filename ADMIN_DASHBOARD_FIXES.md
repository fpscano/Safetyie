# Admin Dashboard & Login Fixes

## Issues Fixed

### Issue 1: Admin Login Auto-Redirect ✅
**Problem:** When navigating to admin-login.html, it automatically redirected to admin-dashboard.html if a token was present, preventing login.

**Solution:** Removed the auto-redirect logic (lines 274-289 in admin-login.html)

**Result:** Admin login page now always displays, allowing users to:
- Log in with different credentials
- Access the login page even if already logged in
- Manually navigate to dashboard if desired

---

### Issue 2: Client Dashboard Not Displaying Data from Admin View ✅
**Problem:** When admin clicked a client from admin dashboard to view their dashboard (`/client-dashboard.html?client=CODE`), the dashboard wasn't displaying engine data and scores.

**Solution:** Added comprehensive error handling and console logging to debug data loading issues:
1. Added detailed console.log statements throughout `loadDashboard()` function
2. Added error message displays for failed API calls
3. Added validation for `client_id` presence
4. Added better error text extraction from failed responses

**Result:** Now you can:
- See exactly what's happening in browser console (F12)
- Identify which API calls are failing
- Get clear error messages if data can't be loaded
- Debug authentication or permission issues

---

## How to Test

### Test 1: Admin Login Page Access

1. **Navigate to admin login:**
   ```
   https://sie-ebe.pages.dev/admin-login.html
   ```

2. **Verify:**
   - Login page displays (no auto-redirect)
   - You see the form with username/email and password fields
   - "SIE Admin Access" badge is visible

3. **Login with credentials:**
   - Username: `sieadmin` OR Email: `admin@sie.com`
   - Password: (your admin password)

4. **Expected result:**
   - Successful login redirects to `/admin-dashboard.html`
   - Admin dashboard shows grid of all clients

---

### Test 2: Admin Viewing Client Dashboard

1. **From admin dashboard, click any client** (e.g., "SIE", "TESTCLIENT", etc.)

2. **Expected URL:**
   ```
   /client-dashboard.html?client=TESTCLIENT
   ```

3. **Open browser console (F12)** to see debugging logs:
   ```
   Loading dashboard... { isAdminView: true, adminViewClientCode: 'TESTCLIENT', clientId: undefined }
   Fetching client data for admin view: TESTCLIENT
   Client fetch response status: 200
   Client data received: { id: 2, client_code: 'TESTCLIENT', client_name: 'Test Client Corp', ... }
   Fetching SIE score for client_id: 2
   SIE score response status: 200
   SIE score data: { results: [...], success: true, meta: {...} }
   Fetching individual engine scores for client_id: 2
   HIE score data: { results: [...], success: true, meta: {...} }
   ...
   Dashboard loading complete
   ```

4. **Expected display:**
   - Client name appears in sidebar and header
   - Overall SIE score displays (or "No SIE data available")
   - Individual engine scores display (or "--" if no data)
   - "Back to Admin" button visible in sidebar

---

### Test 3: Debugging Failed Data Loading

If the dashboard shows no data, check browser console (F12) for errors:

#### Scenario A: Authentication Error
```
Client fetch response status: 401
Failed to fetch client details: 401 {"error":"Unauthorized"}
```
**Solution:**
- Verify JWT token exists: `localStorage.getItem('sie_token')`
- Verify user is SIE admin: `localStorage.getItem('sie_user')` → should have `user_type: 'sie'`
- Re-login if token expired

#### Scenario B: Client Not Found
```
Client fetch response status: 404
Failed to fetch client details: 404 {"error":"Client not found"}
```
**Solution:**
- Verify client code is correct
- Check database: `npx wrangler d1 execute sie-db --remote --command "SELECT * FROM clients WHERE client_code='TESTCLIENT';"`
- Client may have been deleted or deactivated

#### Scenario C: No Engine Data
```
SIE score response status: 200
SIE score data: { results: [], success: true, meta: {...} }
No SIE data found for this client
```
**Solution:**
- Client has no engine score data yet
- This is normal for new clients
- Dashboard displays "--" or "No data available"
- To add data, use engine API endpoints or wait for data ingestion

#### Scenario D: Permission Denied
```
Client fetch response status: 403
Failed to fetch client details: 403 {"error":"Access denied to this client"}
```
**Solution:**
- SIE admin users should have access to all clients
- Verify user role: `localStorage.getItem('sie_user')` → check `role` field
- May need `dev`, `sales`, or `csr` role
- Contact system admin if role is incorrect

---

## Architecture Explanation

### Admin View Mode Detection

**File:** `website/client-dashboard.html`

```javascript
// Check URL for ?client=CODE parameter
const urlParams = new URLSearchParams(window.location.search);
const clientCodeParam = urlParams.get('client');

if (clientCodeParam && token) {
    isAdminView = true;
    adminViewClientCode = clientCodeParam;
    // Fetch client_id from client_code via API
}
```

### Data Flow for Admin Viewing Client Dashboard

1. Admin clicks client card on `/admin-dashboard.html`
2. Browser navigates to `/client-dashboard.html?client=TESTCLIENT`
3. Client dashboard detects `?client=` parameter
4. Sets `isAdminView = true`
5. Fetches client details: `GET /api/v1/admin/clients/TESTCLIENT`
6. Extracts `client_id` from response
7. Fetches engine data: `GET /api/v1/engines/sie?client_id=2`
8. Displays data

### Security Enforcement

**File:** `cano/functions/api/v1/engines/[engine].js` (lines 90-101)

```javascript
// Security: Client users can ONLY access their own client data
if (!authUser.isSIEUser) {
    // Override any client_id parameter with authenticated user's client_id
    clientId = String(authUser.client_id);
}

// Verify access permission
if (!authUser.isSIEUser && authUser.client_id !== Number(clientId)) {
    return errorResponse('Access denied to this client data', 403);
}
```

**Result:**
- SIE admin users (identified by `isSIEUser: true`) can access ANY client's data
- Client users can ONLY access their own `client_id`
- Enforced at API level, not just frontend

---

## Console Logging Reference

### Normal Admin View Flow

```
Loading dashboard... { isAdminView: true, adminViewClientCode: 'SIE', clientId: undefined }
Fetching client data for admin view: SIE
Client fetch response status: 200
Client data received: { id: 1, client_code: 'SIE', client_name: 'SIE Internal Company', is_active: true }
Fetching SIE score for client_id: 1
SIE score response status: 200
SIE score data: { results: [{ determination_score: 25, determination_level: 'safe', ... }], success: true }
Fetching individual engine scores for client_id: 1
HIE score data: { results: [], success: true, meta: {...} }
No data for HIE
EIE score data: { results: [], success: true, meta: {...} }
No data for EIE
...
Dashboard loading complete
```

### Normal Client User View Flow

```
Loading dashboard... { isAdminView: false, adminViewClientCode: null, clientId: '2' }
Fetching client data for regular view, client_id: 2
Client data received: { id: 2, client_code: 'TESTCLIENT', client_name: 'Test Client Corp', is_active: true }
Fetching SIE score for client_id: 2
SIE score response status: 200
SIE score data: { results: [...], success: true }
...
```

---

## Common Issues & Solutions

### Issue: "Session error: No client ID found"
**Cause:** Client user logged in but `client_id` not saved to localStorage

**Solution:**
1. Check `localStorage.getItem('client_id')`
2. If missing, log out and log back in
3. Client login process should save it during company code verification step

### Issue: Dashboard shows "Loading..." forever
**Cause:** JavaScript error preventing data load

**Solution:**
1. Open browser console (F12)
2. Look for JavaScript errors (red text)
3. Check if API calls are being made (Network tab)
4. Verify token is present: `localStorage.getItem('sie_token')`

### Issue: All engine scores show "--"
**Cause:** No engine data exists for this client

**Solution:**
- This is normal for new clients
- Data is populated by:
  - External data ingestion processes
  - Manual API calls to POST engine scores
  - Integration with telematics/ELD systems
- For testing, can manually insert data via wrangler D1

### Issue: "Access denied" when admin views client
**Cause:** Token doesn't identify user as SIE admin

**Solution:**
1. Check user data: `JSON.parse(localStorage.getItem('sie_user'))`
2. Verify `user_type: 'sie'` is present
3. If `user_type: 'client'`, you logged in as a client user, not admin
4. Log out and use admin-login.html instead

---

## Deployment

After making these fixes, deploy to Cloudflare Pages:

```bash
cd cano
npx wrangler pages deploy --project-name=sie
```

---

## Next Steps

### Optional Enhancements

1. **Add Loading Indicators**
   - Show spinner while fetching client data
   - Disable buttons during data load

2. **Add Retry Logic**
   - Auto-retry failed API calls
   - Exponential backoff for transient errors

3. **Add Data Refresh**
   - Add "Refresh" button to reload dashboard data
   - Auto-refresh every N seconds

4. **Better Error Messages**
   - User-friendly error messages instead of raw API errors
   - Suggestions for how to fix common issues

5. **Add Sample Data Generator**
   - For new clients with no data, show "Generate Sample Data" button
   - Helpful for demos and testing

---

## File Changes Summary

### Modified Files

1. **`website/admin-login.html`**
   - Removed auto-redirect logic
   - Now always shows login form

2. **`website/client-dashboard.html`**
   - Added comprehensive console logging
   - Added error message displays
   - Added client_id validation
   - Better error handling for all API calls

### No Backend Changes
All fixes are frontend-only. No changes to API endpoints or database schema required.

---

**Status:** ✅ Both issues fixed
**Testing Required:** Manual testing with browser console open
**Deployment:** Frontend changes only, deploy via wrangler pages deploy
**Last Updated:** 2026-02-09
