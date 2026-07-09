from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage
from groq import RateLimitError, APIStatusError

from app.agent.graph import agent_graph
from app.schemas import ChatRequest, ChatResponse, FormData

router = APIRouter(prefix="/api/chat", tags=["chat"])

SESSION_HISTORY: dict = {}
MAX_HISTORY_MESSAGES = 16


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest):
    history = SESSION_HISTORY.get(payload.session_id, [])
    history = history[-MAX_HISTORY_MESSAGES:] + [HumanMessage(content=payload.message)]

    try:
        result = agent_graph.invoke(
            {
                "messages": history,
                "form_data": payload.form_data.model_dump(),
                "badges": [],
            },
            config={"recursion_limit": 15},
        )
    except RateLimitError as exc:
        return ChatResponse(
            reply=(
                "Groq's daily free-tier token limit has been reached for the "
                "configured API key. Wait for the reset window shown in the "
                "error, or use a different/upgraded Groq API key, then try "
                "again — nothing was lost, your form data is unchanged."
            ),
            form_data=payload.form_data,
            badges=[],
            tool_calls=[],
        )
    except APIStatusError as exc:
        return ChatResponse(
            reply=f"The AI provider returned an error ({exc.status_code}). Please try again.",
            form_data=payload.form_data,
            badges=[],
            tool_calls=[],
        )

    SESSION_HISTORY[payload.session_id] = result["messages"]

    reply_text = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            reply_text = msg.content
            break

    return ChatResponse(
        reply=reply_text or "Got it.",
        form_data=FormData(**result["form_data"]),
        badges=result.get("badges", []),
        tool_calls=[],
    )


@router.post("/reset/{session_id}")
def reset_session(session_id: str):
    SESSION_HISTORY.pop(session_id, None)
    return {"status": "reset"}