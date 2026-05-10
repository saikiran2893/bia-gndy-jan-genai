import asyncio
import json
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel,field_validator
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from graph.builder import build_travel_graph
import uuid
from threading import Lock
from typing import Any


logger = logging.getLogger("travel_planner_api")
logging.basicConfig(level=logging.INFO,format=("%(asctime)s - %(levelname)s - %(message)s"))


app = FastAPI(title="Agentic Travel Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])

GRAPH = build_travel_graph()
GRAPH_LOCK = Lock()

class PlanRequest(BaseModel):
    message:str ## Hi! i want a 5 day trip to Dubai next month. I'd like to know what the weather will be like, what places i can visit, and how much thte total trip cost. I want the trip cost in INR. I prefer local food and public transport.

    @field_validator("message")
    def validate_message(cls, value):
        if not value.strip():
            raise ValueError("Message cannot be empty")
        return value
    
    @field_validator("message")
    @classmethod
    def strip_message(cls, value):
        return value.strip() if isinstance(value, str) else None

class PlanResponse(BaseModel):
    thread_id:str
    # values : dict[str,Any]
    status:str #waiting_for_feedback, completed
    itenary:str
    revision: int = 0

class FeedbackRequest(BaseModel):
    thread_id:str
    feedback:str

    @field_validator("feedback")
    @classmethod
    def strip_feedback(cls, value):
        return value.strip() if isinstance(value, str) else None
    
    @field_validator("thread_id")
    @classmethod
    def strip_thread_id(cls, value):
        return value.strip() if isinstance(value, str) else None
    

def _run_until_pause_or_complete(input, thread_id):
    ## Call agent with input and thread_id
    ## Loop until agent returns "waiting_for_feedback" or "completed"
    ## Return the final result
    config = {"configurable":{"thread_id":thread_id}}
    with GRAPH_LOCK:
        for event in GRAPH.stream(input, config,stream_mode="values"):
            print(f"Event: {event}")
            messages = event.get("messages", [])
            if messages:
                last = messages[-1]
                if hasattr(last, "content") and last.content:
                    print(f"\n[Agent] : {last.content[:300]}{'...' if len(last.content) > 300 else ''}")
        
        snapshot = GRAPH.get_state(config)
    #print(f"Final Snapshot: {snapshot}")
        values = snapshot.values
        #print(f"Final Values: {values}")
        # print("\n\n")
        itineary = values.get("itinerary", "No itenary generated")
       # print(f"Final Itinerary: {itineary}")
        revision = values.get("revision", 0)
        status = snapshot.next
        if "human_feedback" in status :
            status = "waiting_for_feedback"
        else:
            status  = "completed"
    return   {"thread_id": thread_id, "status": status, "itenary": itineary,"revision": revision}


@app.post("/plan/start", response_model=PlanResponse)
async def start_planning(request: PlanRequest):
    thread_id = str(uuid.uuid4())
    try:
        user_query = {"messages":[HumanMessage(content = request.message)]}
        result = _run_until_pause_or_complete(user_query, thread_id)  ## Call agent by passing by input
        return result 
    except Exception as e:
        logger.error(f"Error in start_planning: {e}")
        raise HTTPException(status_code=500, detail="Plan Start Error")

@app.post("/plan/feedback", response_model=PlanResponse)
async def provide_feedback(request: FeedbackRequest):
    try:
        user_query = Command(resume=request.feedback)
        result = result = _run_until_pause_or_complete(user_query, request.thread_id) 
        return result
    except Exception as e :
        logger.error(f"Error in provide_feedback: {e}")
        raise HTTPException(status_code=500, detail="Feedback Error")  
 


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,workers=1)