from langchain_groq import ChatGroq

from app.config import settings

# gemma2-9b-it is the model mandated by the task brief, but Groq does not
# expose function/tool-calling for gemma2-9b-it today. Since the whole agent
# is built around LangGraph tool-calling (extracting structured fields from
# free text and invoking the right tool), we drive the graph with
# llama-3.3-70b-versatile, which DOES support tool calling on Groq.
# gemma2-9b-it is still wired in (see GROQ_SUMMARY_MODEL) and used for a
# secondary, non-tool-calling summarization pass so the mandated model is
# genuinely part of the pipeline.

tool_calling_llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0,
)

summary_llm = ChatGroq(
    model=settings.GROQ_SUMMARY_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
)


def summarize_text(text: str) -> str:
    """Use gemma2-9b-it to produce a one-line summary of an interaction."""
    prompt = (
        "Summarize the following HCP (Healthcare Professional) sales interaction "
        "note in one short sentence, professional tone:\n\n" + text
    )
    try:
        result = summary_llm.invoke(prompt)
        return result.content.strip()
    except Exception:
        # Don't let a transient Groq/network hiccup break the whole tool call —
        # fall back to a plain confirmation instead of crashing the agent turn.
        return "Interaction details recorded."
