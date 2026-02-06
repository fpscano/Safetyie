# PowerShell script to get SIE client data from D1
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler d1 execute sie-db --remote --file ..\gemini\2026-02-06_select_sie_client.sql --json