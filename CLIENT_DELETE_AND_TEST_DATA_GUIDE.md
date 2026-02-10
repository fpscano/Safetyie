# Client Delete & Test Data Population Guide

**Date:** 2026-02-09
**Changes:** Added cascade delete functionality + instructions for populating varied test data

---

## ✅ PART 1: CASCADE DELETE FUNCTIONALITY

### What Was Added

**New Feature:** Admin users with `dev` role can now permanently delete clients and ALL associated data from the D1 database.

### Important Clarifications

**There is ONLY ONE D1 database** for the entire platform (`sie-db`).

When you delete a client, you are **NOT deleting a separate database**. You are deleting:
1. The client record from the `clients` table
2. ALL data associated with that `client_id` across ALL tables

### What Gets Deleted (CASCADE)

When you delete a client (e.g., "TESTCLIENT"), the system removes:

1. ✓ **All Engine Scores:**
   - `sie_scores` - Overall safety scores
   - `hie_scores` - Hours of Service Intelligence
   - `eie_scores` - Event Intelligence
   - `fie_scores` - Fault Intelligence
   - `tie_scores` - Telematics Intelligence
   - `dvirie_scores` - Inspection scores
   - `wie_scores` - Weather Intelligence
   - `pie_scores` - Predictive Intelligence

2. ✓ **All Vehicles:** Removes all vehicle records for that client

3. ✓ **All Drivers:** Removes all driver records for that client

4. ✓ **All Client Users:** Removes all users who belong to that client (they can no longer log in)

5. ✓ **All Audit Logs:** Removes audit trail for that client

6. ✓ **Client Record:** Finally, removes the client itself

### Security & Permissions

**Who Can Delete:**
- ✅ SIE users with **`dev`** role ONLY
- ❌ Sales and CSR roles CANNOT delete clients
- ❌ Client users CANNOT delete clients

### How to Delete a Client

#### Step 1: Login as Dev Admin
1. Go to `/admin-login.html`
2. Login with a `dev` role account (e.g., admin@sie.com)

#### Step 2: Navigate to Clients
1. Go to **Admin Dashboard** → **Clients** → **View Clients**
2. You'll see all clients in a grid

#### Step 3: Click Delete Button
1. Each client card now has a red **"Delete"** button
2. Click the Delete button for the client you want to remove

#### Step 4: Confirm Deletion
You'll see TWO confirmation prompts:

**First Prompt:** Type the client code to confirm
```
⚠️ WARNING: CASCADE DELETE ⚠️

Are you ABSOLUTELY SURE you want to delete "Test Client Co." (TESTCLIENT)?

This will PERMANENTLY DELETE:
• Client record
• ALL engine scores (SIE, HIE, EIE, FIE, TIE, DVIRIE, WIE, PIE)
• ALL vehicles
• ALL drivers
• ALL client users
• ALL audit logs

THIS CANNOT BE UNDONE!

Type the client code "TESTCLIENT" below to confirm:
```

**Second Prompt:** Final confirmation
```
FINAL CONFIRMATION:

You are about to PERMANENTLY DELETE "Test Client Co." and ALL associated data.

Click OK to proceed with deletion.
```

#### Step 5: Deletion Complete
You'll see a success message and the client will be removed from the list.

### API Endpoint

**DELETE** `/api/v1/admin/clients/{client_code}`

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Client TESTCLIENT and all associated data have been permanently deleted",
  "client_id": 5,
  "client_code": "TESTCLIENT"
}
```

**Response (Error):**
```json
{
  "error": "Access denied" | "Client not found" | "Server error"
}
```

### Testing Delete Functionality

**Test with a safe client (one you don't need):**

1. Create a temporary test client first:
   ```sql
   INSERT INTO clients (id, client_code, client_name, is_active)
   VALUES (99, 'DELETEME', 'Test Delete Client', 1);
   ```

2. Delete it via admin dashboard

3. Verify it's gone:
   ```bash
   npx wrangler d1 execute sie-db --remote --command "SELECT * FROM clients WHERE client_code='DELETEME';"
   ```

Should return empty results.

---

## ✅ PART 2: VARIED TEST DATA POPULATION

### Why You See "--" in Engine Scores

**Current State:**
- ✅ Overall SIE scores exist (42, 18, 32, 52, 82)
- ❌ Individual engine score tables are EMPTY

**Why Individual Engines Show "--":**

The dashboard displays individual engine scores (HIE, EIE, FIE, TIE, DVIRIE, WIE, PIE) by fetching from their respective tables:
- `hie_scores`
- `eie_scores`
- `fie_scores`
- `tie_scores`
- `dvirie_scores`
- `wie_scores`
- `pie_scores`

These tables are currently empty, so the dashboard shows "--" for all of them.

### Database Schema Requirements

The engine score tables have **foreign key constraints:**

**HIE Scores (Hours Intelligence):**
```sql
CREATE TABLE hie_scores (
    driver_id TEXT NOT NULL REFERENCES drivers(id),  -- REQUIRED!
    client_id INTEGER NOT NULL REFERENCES clients(id),
    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
    ...
)
```

**Other Engine Scores (EIE, FIE, TIE, etc.):**
```sql
CREATE TABLE eie_scores (
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),  -- REQUIRED!
    client_id INTEGER NOT NULL REFERENCES clients(id),
    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
    ...
)
```

**This means:**
- HIE scores require a `driver_id` (from `drivers` table)
- Other engine scores require a `vehicle_id` (from `vehicles` table)
- You cannot insert engine scores without first having drivers/vehicles

### Current Vehicles & Drivers in Database

**Client 2 (WGL) has:**
- 3 vehicles: `vehicle-wgl-001`, `vehicle-wgl-002`, `vehicle-wgl-003`
- 3 drivers: `driver-wgl-001`, `driver-wgl-002`, `driver-wgl-003`

**Client 3 (FAST) has:**
- 1 vehicle: `vehicle-fast-001`
- 1 driver: `driver-fast-001`

**All other clients:**
- 0 vehicles
- 0 drivers

### Populating Test Data - Step by Step

#### Option 1: Simple Approach (Use Existing Vehicles/Drivers)

Add engine scores for WGL (client 2) using existing vehicle/driver IDs:

**Create file:** `add_wgl_engine_scores.sql`
```sql
-- HIE Score for WGL (uses driver)
INSERT INTO hie_scores (driver_id, client_id, score, hos_status, hours_driven_today, hours_remaining, computed_at)
VALUES ('driver-wgl-001', 2, 22, 'compliant', 7.0, 4.0, '2026-02-09 03:00:00');

-- EIE Score for WGL (uses vehicle)
INSERT INTO eie_scores (vehicle_id, client_id, score, event_count_24h, high_severity_count, trend, computed_at)
VALUES ('vehicle-wgl-001', 2, 18, 5, 0, 'decreasing', '2026-02-09 03:00:00');

-- FIE Score
INSERT INTO fie_scores (vehicle_id, client_id, score, active_fault_count, critical_fault_count, maintenance_due, computed_at)
VALUES ('vehicle-wgl-001', 2, 12, 1, 0, 0, '2026-02-09 03:00:00');

-- TIE Score
INSERT INTO tie_scores (vehicle_id, client_id, score, avg_speed_mph, max_speed_mph, computed_at)
VALUES ('vehicle-wgl-001', 2, 25, 62.0, 70.0, '2026-02-09 03:00:00');

-- DVIRIE Score
INSERT INTO dvirie_scores (vehicle_id, client_id, score, last_inspection_at, open_defect_count, is_road_safe, computed_at)
VALUES ('vehicle-wgl-001', 2, 15, '2026-02-08 10:30:00', 1, 1, '2026-02-09 03:00:00');

-- WIE Score
INSERT INTO wie_scores (vehicle_id, client_id, score, weather_condition, severity, advisory, computed_at)
VALUES ('vehicle-wgl-001', 2, 10, 'clear', 'low', 'Excellent conditions', '2026-02-09 03:00:00');

-- PIE Score
INSERT INTO pie_scores (vehicle_id, client_id, score, prediction_type, confidence, risk_factors, prediction_horizon_hours, computed_at)
VALUES ('vehicle-wgl-001', 2, 20, 'incident', 0.65, '{"speeding": false}', 24, '2026-02-09 03:00:00');
```

**Execute:**
```bash
cd cano
npx wrangler d1 execute sie-db --remote --file add_wgl_engine_scores.sql
```

**Result:** WGL dashboard will now show all engine scores!

#### Option 2: Full Approach (Add Vehicles/Drivers for Other Clients)

For clients that have SIE scores but no vehicles/drivers, you need to:

1. **Add vehicles**
2. **Add drivers**
3. **Add engine scores** (using the IDs from step 1 & 2)

**Example for SAFECLIENT (client_id 6):**

**Step 1: Add Vehicles**
```sql
INSERT INTO vehicles (id, client_id, name, license_plate, make, model, year, vin, vehicle_type, status)
VALUES
  ('safeclient-v01', 6, 'SAFE-001', 'SAF-123', 'Freightliner', 'Cascadia', 2023, '1FUJGHDV5NLAB9999', 'tractor', 'active'),
  ('safeclient-v02', 6, 'SAFE-002', 'SAF-124', 'Volvo', 'VNL 760', 2024, '4V4NC9EH7PN555555', 'tractor', 'active');
```

**Step 2: Add Drivers**
```sql
INSERT INTO drivers (id, client_id, first_name, last_name, email, phone, license_number, license_state, license_expiration, status)
VALUES
  ('safeclient-d01', 6, 'Robert', 'SafeDriver', 'r.safe@safeclient.com', '555-0401', '555111', 'FL', '2028-12-31', 'active'),
  ('safeclient-d02', 6, 'Linda', 'Careful', 'l.careful@safeclient.com', '555-0402', '555222', 'FL', '2027-10-10', 'active');
```

**Step 3: Add Engine Scores (using IDs from above)**
```sql
-- HIE (uses driver)
INSERT INTO hie_scores (driver_id, client_id, score, hos_status, hours_driven_today, hours_remaining, computed_at)
VALUES ('safeclient-d01', 6, 12, 'compliant', 6.5, 4.5, '2026-02-09 03:00:00');

-- EIE (uses vehicle)
INSERT INTO eie_scores (vehicle_id, client_id, score, event_count_24h, high_severity_count, trend, computed_at)
VALUES ('safeclient-v01', 6, 8, 2, 0, 'decreasing', '2026-02-09 03:00:00');

-- Continue for all engines...
```

### Quick Win: Test with WGL First

**Recommended approach:**

1. Run the WGL engine scores SQL above (uses existing vehicles/drivers)
2. View WGL dashboard from admin
3. You should see all engine scores populated!
4. Once confirmed working, add data for other clients

---

## 📋 FILES MODIFIED

### Backend (API)
1. `/cano/functions/api/v1/admin/clients/[code].js`
   - Updated `handleDELETE()` function
   - Changed from soft delete (set is_active=0) to CASCADE DELETE
   - Deletes from 8 engine score tables + vehicles + drivers + client_users + audit_log + clients
   - Added detailed console logging
   - Returns success JSON instead of 204 No Content

### Frontend
1. `/website/admin-view-clients.html`
   - Added red "Delete" button to client cards
   - Added CSS for `.danger` button style
   - Added `deleteClient(clientCode, clientName)` JavaScript function
   - Implements two-step confirmation (type client code + final OK)
   - Shows detailed warning about cascade delete
   - Reloads client list after successful deletion

---

## 🧪 TESTING CHECKLIST

### Test Delete Functionality

- [ ] Login as dev admin
- [ ] Navigate to View Clients
- [ ] See red "Delete" button on each client card
- [ ] Click Delete on a test client
- [ ] See first confirmation prompt (type client code)
- [ ] Type incorrect code → deletion cancelled
- [ ] Type correct code → see second confirmation
- [ ] Click Cancel → deletion cancelled
- [ ] Click OK → client deleted
- [ ] Verify client removed from list
- [ ] Verify client removed from database

### Test Engine Scores Display

- [ ] Add engine scores for WGL using SQL above
- [ ] Login as dev admin
- [ ] Click WGL client from admin dashboard
- [ ] View WGL client dashboard
- [ ] Verify all engine scores display numbers (not "--")
- [ ] Verify overall SIE score displays
- [ ] Open browser console (F12) - should see successful API calls

---

## ⚠️ WARNINGS

### Delete Functionality

1. **PERMANENT DELETION** - Cannot be undone
2. **Only DEV role** can delete
3. **No backup** - data is permanently removed from D1
4. **Test first** with a dummy client before deleting real clients

### Test Data

1. **Foreign Key Constraints** - Must have vehicles/drivers before adding engine scores
2. **ID Format** - Use TEXT IDs like `'client-v01'` not numbers
3. **Client ID** - Must match existing client
4. **Scores** - Must be between 0-100

---

## 🚀 DEPLOYMENT

Files to deploy:

```bash
# Copy updated files to cano
cp website/admin-view-clients.html cano/

# Commit to cano submodule
cd cano
git add functions/api/v1/admin/clients/[code].js
git add admin-view-clients.html
git commit -m "Add cascade delete for clients with confirmation

- Delete client now removes ALL associated data (CASCADE)
- Added delete button to admin client cards
- Requires dev role permission
- Two-step confirmation to prevent accidents

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push

# Deploy to Cloudflare
npx wrangler pages deploy --project-name=sie

# Update parent repo
cd ..
git add cano
git commit -m "Update cano: cascade client delete functionality"
git push
```

---

**Last Updated:** 2026-02-09
**Status:** ✅ Complete and ready for deployment
**Next Steps:** Deploy changes, test delete functionality, populate engine score test data
