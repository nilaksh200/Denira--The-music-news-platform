# AGENTS.md — Denira Desktop Agent & System Directives

## 1. System Identity & Mission
**Denira Desktop** is an autonomous, Inshorts-style music news and editorial delivery platform engineered specifically for desktop browser experiences. 
- **Target Cycle Throughput**: Ingests, filters, deduplicates, and synthesizes **10 curated cards per hourly cycle** (~240 cards/day, strictly within GroqCloud's 200k TPD / 1,000 RPD free tier limits).
- **User Experience Goal**: Powers a frictionless **1–2 hour deep browsing session** with rapid horizontal-split card navigation.
- **Content Focus**: High-signal global music journalism across diverse genres (Electronic, Hip-Hop, Indie/Rock, Pop, Jazz/Soul, Metal, Global/Regional), cutting through promotional spam and gossip.

---

## 2. Hard Cost Ceiling: Permanent Zero-Cost ($0 / ₹0)
Denira operates under a strict, non-negotiable **zero recurring cost architecture ($0 / ₹0 permanent tier)**. All automated agents and human contributors must design within these free cloud limits:

| Infrastructure Layer | Provider | Free Tier Allocation & Guardrails |
| :--- | :--- | :--- |
| **Orchestration & Cron** | **GitHub Actions** | Public repository unlimited minutes / private 2,000 min/month. Runs scheduled ephemeral cron jobs every hour. |
| **Inference & LLM** | **GroqCloud Hosted API** | Free hosted inference tier using `openai/gpt-oss-20b`. High token velocity, zero GPU hosting cost. |
| **Database & Storage** | **Supabase (PostgreSQL)** | Free tier (500MB database, pooled connections via Supavisor, up to 50,000 monthly active users). |
| **Frontend & Edge CDN** | **Vercel** | Hobby tier (100GB bandwidth, global Edge Network CDN, serverless functions). |

> **Violations**: Under no circumstances may any agent propose, configure, or introduce paid SaaS components, paid external proxy pools, paid vector databases, or persistent paid compute (e.g., AWS EC2, GCP Compute Engine, DigitalOcean Droplets).

---

## 3. LLM Engine & Inference Specification
- **Designated Model**: `openai/gpt-oss-20b` hosted exclusively on **GroqCloud**.
- **Connection Model**: Direct HTTPS invocation via Groq's OpenAI-compatible REST API endpoints.
- **Constraints**:
  - **No local GPU or hardware dependencies** (no Ollama, LocalAI, or Hugging Face self-hosted inference servers).
  - **No paid API providers** (no OpenAI GPT-4, Anthropic Claude, or Google Cloud Vertex AI billing accounts).
  - **Token Efficiency**: Prompts must utilize strict structured output formatting (JSON mode or deterministic prompt wrapping) to minimize token consumption and maximize throughput within Groq free rate limits (TPM/RPM).

---

## 4. Editorial Integrity & Card Content Standards
Every ingested article processed through the pipeline must adhere to strict editorial specifications prior to database persistence:

1. **Headline**:
   - Must be strictly **under 12 words** (`< 12 words`).
   - Punchy, factual, objective, and active-voice.
   - Clickbait, excessive punctuation, and sensationalism are strictly banned.
2. **Editorial Summary**:
   - Must be strictly **50 to 60 words**.
   - Balanced, objective synopsis answering: *What happened? Who is involved? What is the musical or industry impact?*
   - Written in polished, publication-grade journalistic prose.
3. **Genre Taxonomy**:
   - Every card must be classified into exactly one primary genre tag (e.g., `Electronic`, `Hip-Hop`, `Rock & Indie`, `Pop`, `Jazz & Soul`, `R&B`, `Metal`, `World/Global`).
4. **Attribution & Provenance**:
   - Clear attribution to the original source outlet (e.g., *Pitchfork*, *Resident Advisor*, *Billboard*, *NME*, *The Quietus*, *Bandcamp Daily*).
   - Full, verified outbound URL (`link`) to the original primary source.
5. **Visual Media**:
   - Valid high-resolution image URL (`image_url`) extracted or fallback artwork assigned.

---

## 5. Desktop-First UI & Architecture Constraints
Denira Desktop is **explicitly built for desktop displays** (monitors, laptops) and is not a conventional mobile-first responsive compromise.

- **Viewport Geometry**: Full viewport lock (`100vw` by `100vh` / `100dvh`), `overflow-hidden`.
- **Card Form Factor**: Fixed desktop aspect ratio card (**~900px width by ~520px height**), elevated with drop shadows and subtle border treatment.
- **50/50 Horizontal Split Deck**:
  - **Left Container (50%)**: Rich media cover art / photography with subtle ambient gradient overlay.
  - **Right Container (50%)**: Editorial panel housing genre badge, relative timestamp, source badge, bold headline, 50–60 word editorial summary, and interactive outbound source button.
- **Strict Prohibition**: **Never render as an unstyled single-column vertical feed** or an infinite document flow. Navigation occurs via discrete vertical deck snaps (Inshorts desktop paradigm).
- **Control Modalities**: Smooth transition between cards via mouse wheel scroll, precision trackpad gestures, and keyboard navigation (`ArrowDown`, `ArrowUp`, `Spacebar`, `j`, `k`).

---

## 6. Operational & Codebase Rules for Agents
All code contributions and automated developer agents operating on this repository must comply with:
- Rules defined in [`.agent/rules.md`](file:///c:/Users/Nilaksh/Desktop/denira/.agent/rules.md)
- Design tokens defined in [`.agent/design-system.md`](file:///c:/Users/Nilaksh/Desktop/denira/.agent/design-system.md)
- Database schema definitions in [`backend/db/schema.sql`](file:///c:/Users/Nilaksh/Desktop/denira/backend/db/schema.sql)
