# PowerShell script to get audit log data from D1
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler d1 execute sie-db --remote --file ..\gemini\2026-02-06_audit_log_query.sql --json