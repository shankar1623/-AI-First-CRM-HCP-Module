from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    form_data: Dict[str, Any]
    badges: List[str]
