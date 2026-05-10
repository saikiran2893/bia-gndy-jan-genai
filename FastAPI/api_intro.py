from fastapi import FastAPI, Security, HTTPException, Depends,status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional,List
from fastapi.middleware.cors import CORSMiddleware 
import httpx
import asyncio
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import BackgroundTasks

class AgentTask(BaseModel):
    task_id: int
    description: str = Field(..., example="This is a sample task description.")
    status: Optional[str] = "pending"

class JobRequest(BaseModel):
    task_id: int
    parameters: Optional[dict] = Field(default_factory=dict)


app = FastAPI(
    title  ="My first Agentic API",
    description="This is a simple API to demonstrate how to create an agentic API with FastAPI.",
    version="0.1.0"
)

API_KEY_NAME = "X-API-Key"
api_key_header   = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

VALID_API_KEYS = {"my-secret-key-123", "another-safe-key"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity, adjust as needed
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,  # Allow cookies and authentication credentials
)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key in VALID_API_KEYS:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
                 detail="Invalid API")

# {
#   "task_id": "1000",
#   "description": "This is a sample task description.",
#   "status": "pending"
# }

@app.post("/api/v1/tasks/")
def create_task(task: AgentTask, api_key: str = Depends(get_api_key)): ## Pydantic model for request body validation
    """
    Create a new task for the agent.
    """
    return {"message": "Task created successfully", "task": task}


async def fake_video_streamer():
    for i in range(10):
        yield f"data: Video frame {i} at {asyncio.get_event_loop().time()}\n\n"
        await asyncio.sleep(1)  # Simulate delay in video streaming

from fastapi import Query

@app.get("/api/v1/stream-tasks/")
async def stream_tasks(
    api_key: str = Query(...)
):

    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return StreamingResponse(
        fake_video_streamer(),
        media_type="text/event-stream"
    )

async def send_email_notification(task_id: int):
    # Simulate sending an email (replace with actual email sending logic)
    await asyncio.sleep(300)  # Simulate delay in sending email
    print(f"Email notification sent for task {task_id}")

@app.post('/api/v1/run-job/')
async def run_job(request:JobRequest, bg: BackgroundTasks):
    bg.add_task(send_email_notification, task_id=request.task_id)
    return JSONResponse(content={"message": f"Job for task {request.task_id} is running. Email notification will be sent upon completion."})    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


## Run this in browser: http://localhost:8000/docs to see the interactive API documentation provided by FastAPI.