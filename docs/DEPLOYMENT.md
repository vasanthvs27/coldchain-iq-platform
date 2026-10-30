# ColdChain IQ — Deployment & Installation Guide

## 1. System Requirements

### Hardware Prerequisites
- **CPU**: 4 Cores recommended (Minimum: 2 Cores)
- **RAM**: 8 GB RAM recommended (Minimum: 4 GB)
- **Disk**: 5 GB free disk space

### Software Runtimes
- **Python**: 3.11, 3.12, or 3.13+
- **Node.js**: v18.0.0 or v20.0.0+ (Tested on v22.x)
- **Package Managers**: `pip` (Python) and `npm` (Node)
- **Database**: Managed Supabase PostgreSQL (or Supabase CLI local emulator)

---

## 2. Supabase Database Provisioning

ColdChain IQ is designed strictly for **Supabase PostgreSQL** and uses the Supabase Python SDK and `@supabase/supabase-js`.

### Step 1: Create Supabase Project
1. Log in to [Supabase Management Console](https://supabase.com).
2. Create a new organization and project (e.g. `coldchain-iq-prod`).
3. Note your project credentials from **Project Settings -> API**:
   - `Project URL` (e.g. `https://xyzcompany.supabase.co`)
   - `anon` / `public` API Key
   - `service_role` (Secret) API Key

### Step 2: Execute Schema Initialization Scripts
Navigate to the **SQL Editor** in your Supabase dashboard and execute the following 9 SQL scripts from `backend/database/` in sequential order:

```text
1. 001_create_core_tables.sql       -> 10 Core Entities
2. 002_create_supporting_tables.sql -> Supporting entities & audit tables
3. 003_create_relationships.sql     -> Foreign key constraints
4. 004_create_indexes.sql           -> High-performance query indexes
5. 005_create_constraints.sql       -> Range check constraints
6. 006_create_functions.sql         -> Duration calculation functions
7. 007_create_triggers.sql          -> Timestamp & audit triggers
8. 008_create_rls_policies.sql      -> Row Level Security (RLS) policies
9. 009_seed_master_data.sql         -> Baseline products, loggers, packaging, users
```

---

## 3. Local Development Installation

### 3.1 Backend Setup (Windows PowerShell)

```powershell
# 1. Clone repository and navigate to root
cd "d:\vs\COLDCHAIN IQ PLATFORM"

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install backend dependencies
cd backend
pip install -r requirements.txt

# 5. Configure environment variables
# Copy template and edit with your Supabase credentials
Copy-Item .env.example .env

# 6. Run test suite to verify installation (All 50 tests must pass)
pytest -v

# 7. Start Flask REST API server
python run.py
```
*The Flask REST API will start on `http://localhost:5000` with Swagger docs at `http://localhost:5000/api/v1/docs`.*

### 3.2 Backend Setup (Linux / macOS)

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env

# 4. Run test suite
pytest -v

# 5. Start Flask server
python run.py
```

---

### 3.3 Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install npm dependencies
npm install

# 3. Configure frontend environment variables
# Copy .env.example to .env
cp .env.example .env

# 4. Start Vite development server
npm run dev
```
*The React application will launch on `http://localhost:5173`.*

---

## 4. Environment Variables Reference

### Backend `.env` (`backend/.env`)
```ini
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=coldchain-iq-super-secret-production-key-2026
JWT_SECRET_KEY=coldchain-iq-jwt-signing-secret-key-2026
PORT=5000

# Supabase Credentials (Managed Database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-secret-key

# Generator & Compliance Configuration
DEFAULT_RANDOM_SEED=20261022
TELEMETRY_INTERVAL_MINUTES=10
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend `.env` (`frontend/.env`)
```ini
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key
```

---

## 5. Production Deployment Architectures

### Option A: Containerized Docker Deployment
Create a `Dockerfile` for the backend:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
```

Build and run:
```bash
docker build -t coldchain-iq-backend .
docker run -d -p 5000:5000 --env-file backend/.env coldchain-iq-backend
```

### Option B: Cloud Hosting (Vercel + Railway / Render)
1. **Frontend**:
   - Host on **Vercel** or **AWS Amplify**.
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Set Environment Variables: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
2. **Backend**:
   - Host on **Railway**, **Render**, or **AWS ECS**.
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`
   - Set Environment Variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET_KEY`.

---

## 6. Health & Connectivity Verification

Verify that the system is fully operational by querying the health endpoint:

```bash
curl http://localhost:5000/api/v1/health
```

Expected Response:
```json
{
  "success": true,
  "message": "ColdChain IQ API is healthy and operational",
  "data": {
    "status": "HEALTHY",
    "version": "1.0.0",
    "timestamp": "2026-10-30T09:30:00Z",
    "database": {
      "provider": "Supabase PostgreSQL",
      "connected": true,
      "rls_active": true
    }
  }
}
```
