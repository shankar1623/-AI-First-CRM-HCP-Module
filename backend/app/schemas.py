from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class FormData(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    competitors_mentioned: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    form_data: FormData = FormData()


class ChatResponse(BaseModel):
    reply: str
    form_data: FormData
    badges: List[str] = []
    tool_calls: List[Dict[str, Any]] = []


class InteractionCreate(FormData):
    pass


class InteractionOut(FormData):
    id: int

    class Config:
        from_attributes = True
