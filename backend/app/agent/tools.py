"""
The 5 LangGraph tools for the HCP "Log Interaction" agent.

Each tool receives structured arguments that the LLM extracts from the
rep's natural-language message (entity extraction / summarization happens
inside the LLM's tool-call generation, per the task brief). Each tool
returns a small JSON-serializable dict describing which form fields to
update and which UI "badge" should light up on the chat panel.
"""

from typing import Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.agent.llm import summarize_text


@tool
def log_interaction(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[str] = None,
    samples_distributed: Optional[str] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
) -> dict:
    """Create/populate a NEW HCP interaction log from a free-text description.

    Extract every field you can find in the rep's message: the HCP's name,
    the type of interaction (Meeting, Call, Email, Conference), the date and
    time, attendees, topics discussed, materials shared, samples
    distributed, the rep's observed/inferred sentiment (Positive, Neutral,
    or Negative), and the outcome of the interaction. Only pass fields you
    can actually infer; leave the rest out. Do NOT pass follow-up
    information here — always use the separate follow_up_reminder tool for
    that, even in the same turn, so the due date gets computed correctly.
    """
    updates = {
        k: v
        for k, v in {
            "hcp_name": hcp_name,
            "interaction_type": interaction_type,
            "date": date,
            "time": time,
            "attendees": attendees,
            "topics_discussed": topics_discussed,
            "materials_shared": materials_shared,
            "samples_distributed": samples_distributed,
            "sentiment": sentiment,
            "outcomes": outcomes,
        }.items()
        if v not in (None, "")
    }

    summary_source = ", ".join(f"{k}: {v}" for k, v in updates.items())
    confirmation = (
        summarize_text(summary_source)
        if summary_source
        else "Logged a new interaction."
    )

    return {
        "updates": updates,
        "badge": "Updated",
        "message": f"Logged interaction. {confirmation}",
    }


@tool
def edit_interaction(fields: dict) -> dict:
    """Edit/correct SPECIFIC fields on an already-logged interaction.

    Use this when the rep is correcting or amending something they already
    told you (e.g. "actually it was Dr. Rao, not Dr. Smith" or "change the
    date to tomorrow"). Only include the fields that must change in
    `fields` (a dict of field_name -> new_value). Every other field already
    on the form must be left untouched — do not repeat unrelated fields.
    """
    fields = {k: v for k, v in (fields or {}).items() if v not in (None, "")}
    changed = ", ".join(fields.keys()) if fields else "no fields"
    return {
        "updates": fields,
        "badge": "Updated",
        "message": f"Updated {changed} on the interaction log.",
    }


@tool
def sentiment_analysis(text: str) -> dict:
    """Analyze the HCP's sentiment expressed in the rep's message.

    Classify the HCP's reaction as Positive, Neutral, or Negative based on
    the wording of the interaction (e.g. enthusiasm, hesitation, objection)
    and set it on the form's sentiment field.
    """
    lowered = text.lower()
    positive_words = ["interested", "positive", "great", "excited", "impressed", "keen"]
    negative_words = ["concerned", "negative", "declined", "not interested", "hesitant", "unhappy"]

    if any(w in lowered for w in negative_words):
        sentiment = "Negative"
    elif any(w in lowered for w in positive_words):
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    return {
        "updates": {"sentiment": sentiment},
        "badge": "Sentiment",
        "message": f"Detected {sentiment.lower()} sentiment from the HCP.",
    }


@tool
def competitor_mention_tracker(text: str) -> dict:
    """Detect any competitor products/companies mentioned in the rep's message.

    Scan the message for references to competing drugs, brands, or
    companies (anything the HCP compared the rep's product against) and
    record them on the competitors_mentioned field.
    """
    # A small illustrative keyword list — in production this would be a
    # real competitor product/brand list loaded from the CRM's master data.
    known_competitors = [
        "OncoRival", "MedCore", "Pharmatrix", "BioGenex", "TheraNova",
        "Zentek", "Novastat", "Curelex",
    ]
    found = [c for c in known_competitors if c.lower() in text.lower()]

    if not found:
        return {
            "updates": {},
            "badge": "Competitor",
            "message": "No competitor products detected in this message.",
        }

    joined = ", ".join(found)
    return {
        "updates": {"competitors_mentioned": joined},
        "badge": "Competitor",
        "message": f"Noted competitor mention(s): {joined}.",
    }


@tool
def follow_up_reminder(action: str, due_in_days: Optional[int] = None) -> dict:
    """Create a follow-up reminder/task tied to this interaction.

    Use this whenever the rep describes a next step, even a vague one
    (e.g. "follow up with her", "send the Phase III data", "follow up in 2
    weeks", "next month"). Convert any timeframe mentioned into
    `due_in_days` (e.g. "a week" -> 7, "2 weeks" -> 14, "next month" -> 30,
    "tomorrow" -> 1). If the rep does NOT mention any timeframe at all,
    leave `due_in_days` unset — this tool will apply a sensible recommended
    default (2 weeks) and say so explicitly, rather than leaving the
    follow-up undated.
    """
    recommended_default_days = 14
    used_default = due_in_days is None
    days = due_in_days if due_in_days is not None else recommended_default_days

    due_date = (datetime.now() + timedelta(days=days)).strftime("%b %d, %Y")

    if used_default:
        follow_up_text = (
            f"{action} — by {due_date} (~{days} days; no timeframe given, "
            f"applied recommended default of 2 weeks)"
        )
        note = (
            f"No specific timeframe was mentioned, so I set a recommended "
            f"default follow-up of 2 weeks (by {due_date})."
        )
    else:
        follow_up_text = f"{action} — by {due_date} ({days} day(s) from today)"
        note = f"Follow-up reminder set for {due_date} ({days} day(s) from today): {action}"

    return {
        "updates": {"follow_up_actions": follow_up_text},
        "badge": "Follow-ups",
        "message": note,
    }


ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    sentiment_analysis,
    competitor_mention_tracker,
    follow_up_reminder,
]
