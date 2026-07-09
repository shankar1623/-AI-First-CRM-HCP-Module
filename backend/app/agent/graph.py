import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage

from app.agent.state import AgentState
from app.agent.llm import tool_calling_llm
from app.agent.tools import ALL_TOOLS

llm_with_tools = tool_calling_llm.bind_tools(ALL_TOOLS)
TOOLS_BY_NAME = {t.name: t for t in ALL_TOOLS}

SYSTEM_PROMPT = """You are the AI assistant embedded in an AI-first CRM's \
"Log HCP Interaction" screen for pharma field reps. The rep NEVER types \
directly into the form on screen — the only way fields get filled in is \
through your tool calls, driven by what the rep tells you in chat.

Current form state (JSON): {form_data}

Rules:
- If the rep describes a NEW interaction, call log_interaction with every \
field you can extract (HCP name, interaction type, date, time, attendees, \
topics discussed, materials/samples, sentiment, outcomes). Never pass \
follow-up info to log_interaction — see below.
- If the rep is correcting or adding to something already on the form, \
call edit_interaction with ONLY the changed field(s).
- Also call sentiment_analysis when the HCP's reaction is described, \
competitor_mention_tracker when a competing product/company is named, and \
follow_up_reminder whenever ANY next step or follow-up is mentioned — \
even a vague one like "follow up with her" with no date. Convert any \
timeframe you find into due_in_days (e.g. "a week" -> 7, "2 weeks" -> 14, \
"next month" -> 30, "tomorrow" -> 1). If no timeframe is mentioned at all, \
just call follow_up_reminder with the action and omit due_in_days — the \
tool will apply a sensible default and tell the rep it did so. You may \
call several tools for one message.
- After tool results come back, reply to the rep with a brief, friendly \
confirmation of what was logged/updated. Do not repeat the entire form \
back — just confirm what changed.
"""


def call_model(state: AgentState) -> AgentState:
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT.format(
            form_data=json.dumps(state.get("form_data", {}))
        ))] + list(messages)
    else:
        messages = [SystemMessage(content=SYSTEM_PROMPT.format(
            form_data=json.dumps(state.get("form_data", {}))
        ))] + list(messages[1:])

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def execute_tools(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    form_data = dict(state.get("form_data", {}))
    badges = list(state.get("badges", []))
    tool_messages = []

    for call in getattr(last_message, "tool_calls", []) or []:
        tool_fn = TOOLS_BY_NAME.get(call["name"])
        if tool_fn is None:
            tool_messages.append(ToolMessage(
                content=f"Unknown tool {call['name']}", tool_call_id=call["id"]
            ))
            continue

        try:
            result = tool_fn.invoke(call["args"])
        except Exception as exc:
            tool_messages.append(ToolMessage(
                content=f"Tool {call['name']} failed: {exc}", tool_call_id=call["id"]
            ))
            continue

        updates = result.get("updates", {}) if isinstance(result, dict) else {}
        badge = result.get("badge") if isinstance(result, dict) else None
        message = result.get("message", "") if isinstance(result, dict) else str(result)

        form_data.update(updates)
        if badge and badge not in badges:
            badges.append(badge)

        tool_messages.append(ToolMessage(content=message, tool_call_id=call["id"]))

    return {"messages": tool_messages, "form_data": form_data, "badges": badges}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", execute_tools)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


agent_graph = build_graph()
