# AI-First CRM — HCP Module: Log Interaction Screen
## Architecture
```
frontend/   React 18 + Redux Toolkit (Vite) — split-screen UI
backend/    FastAPI + LangGraph + Groq — chat + persistence API
```
- **Frontend → Backend**: `POST /api/chat` sends the rep's message plus the
  current form state; the response contains the assistant's reply, the
  updated form fields, and which tool "badges" fired.
- **Backend**: FastAPI exposes `/api/chat` (talks to the LangGraph agent)
  and `/api/interactions` (persists a finished log to Postgres via
  `Save to DB`).
- **Agent**: a LangGraph `StateGraph` with two nodes — `agent` (Groq LLM
  with tools bound) and `tools` (executes whichever tools the LLM decided
  to call) — looping until the LLM responds with plain text instead of a
  tool call.

:

- `GROQ_MODEL=llama-3.3-70b-versatile` drives the LangGraph agent's tool
  calls (entity extraction + routing).
- `GROQ_SUMMARY_MODEL=gemma2-9b-it` is still wired in and used inside the
  `log_interaction` tool to generate the short natural-language
  confirmation shown in chat — so the mandated model is genuinely part of
  the pipeline, just not the tool-calling brain.

Both are configurable via `backend/.env` if Groq adds tool-calling support
for `gemma2-9b-it` later — just flip `GROQ_MODEL`.

## The 5 LangGraph tools

1. **`log_interaction`** — Creates a new interaction log from a free-text
   message. The LLM extracts HCP name, interaction type, date/time,
   attendees, topics discussed, materials/samples, sentiment, outcomes, and
   follow-up actions as structured tool arguments, and the tool calls
   `gemma2-9b-it` to produce a one-line confirmation summary.
2. **`edit_interaction`** — Corrects/amends specific fields only (e.g. "it
   was actually Dr. Rao, not Dr. Smith"). Every other field already on the
   form is left untouched.
3. **`sentiment_analysis`** — Classifies the HCP's reaction (Positivgit adde /
   Neutral / Negative) from the wording of the message and sets the
   sentiment field + chip on the form.
4. **`competitor_mention_tracker`** — Scans the message for competitor
   product/company mentions and records them.
5. **`follow_up_reminder`** — Captures a next-step/reminder (with an
   optional due-in-N-days) and sets the follow-up field.

The LLM can call several of these tools for a single message (e.g. one
message that both logs the interaction and mentions a competitor).

## Data flow for a message

1. Rep types in the chat panel → frontend `POST /api/chat` with
   `{ session_id, message, form_data }`.
2. LangGraph `agent` node calls Groq with the system prompt (includes
   current form state) + the tools.
3. If the LLM emits tool calls, the `tools` node executes them, merges
   their `updates` into `form_data`, and records a badge; control returns
   to `agent` for a final natural-language reply.
4. FastAPI returns `{ reply, form_data, badges }`; Redux merges
   `form_data` into the form and appends the reply to the chat log.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```



### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the printed local URL (default `http://localhost:5173`). The backend
must be running on `http://localhost:8000` (configurable via
`frontend/.env` → `VITE_API_BASE_URL`).

## Try it

Type into the chat panel:

> Met Dr. Sarah Smith today, she showed positive interest in OncoBoost, we
> discussed efficacy data and Phase III results. Shared the clinical
> brochure. She wants a follow-up in 2 weeks.

Then a correction:

> Actually it was Dr. Rao, not Dr. Smith.

Only the `hcp_name` field changes — everything else stays as-is.

## Notes / assumptions

- Chat history is kept in-memory per `session_id` (a UUID generated per
  browser tab) — fine for a take-home assignment; swap for Redis/DB-backed
  history for production.
- `competitor_mention_tracker` uses a small illustrative keyword list;
  in a real CRM this would be backed by the product master data table.
- The form panel intentionally has **no editable inputs** — this mirrors
  the brief's requirement that the form can only be controlled through the
  AI assistant.
