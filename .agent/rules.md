# Agent Execution & Engineering Rules

This document establishes the binding technical constraints, operational boundaries, and security rules for all agents and developers working on **Denira Desktop**.

---

## 1. Execution Boundaries & Serverless Isolation
To ensure adherence to the non-negotiable **$0 / ₹0 permanent tier** constraint, traditional server infrastructure is forbidden.

- **No Persistent Server Daemons**:
  - Do NOT introduce, configure, or execute persistent background processes such as **Redis**, **Celery**, **RabbitMQ**, or **PM2**.
  - No background worker processes that run indefinitely awaiting jobs.
  - No long-running stateful HTTP daemon listeners (e.g., persistent Flask/FastAPI servers hosted on un-metered compute).
- **Ephemeral Pipeline Architecture**:
  - Ingestion, scraping, parsing, summarization, and database seeding must run as **ephemeral CLI commands / scripts**.
  - Scheduled execution is powered exclusively by **GitHub Actions cron workflows** (`.github/workflows/`), terminating immediately upon cycle completion.
  - Frontend and API read paths run on **Vercel Serverless / Edge Functions**.
- **State Management**:
  - All shared state and persistence must reside within **Supabase PostgreSQL** via stateless network transactions.
  - Local disk storage must only be used for ephemeral temp files (`/tmp`) that are cleaned up before process exit.

---

## 2. Asynchronous Network & I/O Rule
Blocking synchronous network calls introduce bottlenecks, trigger timeout failures in GitHub Actions, and waste compute quotas.

- **Mandatory Async Client**:
  - Enforce `httpx.AsyncClient` for all outbound HTTP requests across RSS ingestion, HTML extraction, and Groq API communication.
  - **Banned Libraries for Network I/O**: Do NOT use `requests`, `urllib`, `urllib3`, or `aiohttp` (standardize strictly on `httpx`).
- **Concurrency & Rate Limit Management**:
  - Bound concurrent tasks using `asyncio.Semaphore` (e.g., maximum 5–10 concurrent requests) to prevent hammering upstream RSS feeds and hitting GroqCloud free rate limits.
  - Implement exponential backoff jitter with `tenacity` or custom async retry loops for transient network or 429 errors.
- **Connection Lifecycle & Timeouts**:
  - Always use `async with httpx.AsyncClient(...)` context managers to ensure socket cleanup and connection pool recycling.
  - Explicit timeouts are mandatory on every outbound call (e.g., `httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)`). Infinite blocking timeouts are strictly banned.

---

## 3. Security & Secret Governance
- **Zero Hardcoded Secrets**:
  - Never hardcode API keys, database connection URIs, passwords, service role keys, or personal tokens into source code, config files, migration scripts, or git commits.
- **Environment Variable Abstraction**:
  - All credentials must be loaded exclusively via environment variables using validated configuration schemas (e.g., `pydantic-settings` or Python `os.getenv` with validation):
    - `GROQ_API_KEY`: GroqCloud authentication token.
    - `DATABASE_URL`: Supabase Transaction/Session pooled PostgreSQL URI.
    - `NEXT_PUBLIC_SUPABASE_URL`: Supabase project URL for frontend client queries.
    - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anonymous public API key.
- **Source Control Hygiene**:
  - Ensure `.env`, `.env.local`, `*.pem`, and credentials are listed in `.gitignore`.
  - Only `.env.example` with non-sensitive template values may be checked into version control.

---

## 4. Idempotency & Data Deduplication Guardrails
- **Deduplication Key**:
  - Every ingested article must calculate a SHA-256 hash of its canonical URL (`url_hash`).
- **Upsert / Conflict Handling**:
  - Database write operations must use `ON CONFLICT (url_hash) DO NOTHING` or PostgreSQL upsert logic to ensure zero duplicate cards across repeated cron executions.
- **Idempotent Migrations**:
  - All SQL files, table alterations, and index scripts must be idempotent using `IF NOT EXISTS`.

---

## 5. Architectural Quality Standards
- **Modularity**:
  - Keep ingestion sources (`backend/ingestion/`), summarization engines (`backend/summarizer/`), and database clients (`backend/db/`) decoupled with explicit typed interfaces.
- **Error Resilience**:
  - Failures in a single RSS feed or article parse must never abort the entire ingestion run. Log the error and continue processing remaining items in the cycle.
