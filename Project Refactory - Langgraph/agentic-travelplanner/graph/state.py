from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from typing import Optional


class TravelState(MessagesState):
    """
    Extend Messages with travel specific details
    """
    itinerary: Optional[str] = None
    revision: int=0
    human_feedback: str =""
    approved: bool = False