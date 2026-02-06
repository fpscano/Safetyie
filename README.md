# Secret Sauce - SIE Project Organization

This folder contains the complete SIE (Safety Intelligence Engine) project, organized into logical components.

## 📁 Folder Structure

### 🌐 website/
**Frontend - Public-facing web pages**
- HTML pages (login, admin dashboard, about, contact, etc.)
- CSS styling (styles.css)
- Images and assets
- Static configuration (_headers)

**Use for:** Making changes to the UI, adding new pages, updating styles

---

### ⚙️ cano/
**Backend - The SIE Engine**
- `functions/` - Cloudflare Functions (API endpoints)
- `migrations/` - Database schema migrations
- `scripts/` - Utility scripts (seeding, password generation)
- Configuration files (wrangler.toml, package.json)
- Git repository (.git)

**Use for:**
- API development
- Database operations
- Deployment configuration
- Backend logic

**Deploy from here:**
```bash
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler pages deploy ./ --project-name=sie
```

---

### 📔 diary/
**Your personal notes and development log**
- Keep your thoughts, ideas, and progress notes here
- Track changes, decisions, and learnings

---

### 🤖 claude/
**Claude AI Configuration**
- Contains .claude folder with AI agent configurations
- Custom agents for database engineering, deployment, etc.

---

## 🔗 How Website & Cano Work Together

The `website/` folder contains the frontend that users see.
The `cano/` folder contains the backend that powers it.

### For Local Development:
```bash
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
.\test-local.ps1
```
This runs the backend and serves the website together.

### For Deployment:
You need to combine them:
1. Copy website files into cano folder root
2. Deploy from cano folder

Or use the provided deployment script (see below).

---

## 🚀 Quick Start

### Test Locally
```powershell
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
.\test-local.ps1
```

### Deploy to Cloudflare
```powershell
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler pages deploy ./ --project-name=sie
```

### Access Database
```powershell
cd "C:\Users\FpsCa\OneDrive\Desktop\secret sauce\cano"
npx wrangler d1 execute sie-db --remote --command "SELECT * FROM clients;"
```

---

## 📝 Important Notes

- **Git repository** is in the `cano/` folder
- **Database migrations** are in `cano/migrations/`
- **API endpoints** are in `cano/functions/`
- **Frontend files** are in `website/`

---

## 🔑 Login Credentials

**Company Code:** SIE (any case)
**Email:** admin@sie.com
**Password:** admin123

---

**Created:** 2026-02-06
**Structure:** secret sauce/{website, cano, diary, claude}
