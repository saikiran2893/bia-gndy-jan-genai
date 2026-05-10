from fastapi import FastAPI,WebSocket,WebSocketDisconnect


app = FastAPI()

#llm = openai.ChatCompletion(model="gpt-3.5-turbo")
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            ##repsone_data= llm.generate_response(data)  # Simulate LLM response generation
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("WebSocket connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)