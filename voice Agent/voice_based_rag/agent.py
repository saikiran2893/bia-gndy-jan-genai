from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions,JobContext,WorkerOptions,cli,function_tool,RunContext
from livekit.plugins import openai,cartesia,noise_cancellation
from sentence_transformers import SentenceTransformer

from build_kb import COLLECTION_NAME,QDRANT_PATH,EMBED_MODEL_NAME
from qdrant_client import QdrantClient

def get_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)

def retrive_documents(query:str, top_k:int =3, score_threshold:float = 0.15):
    client = get_client()
    model = SentenceTransformer(EMBED_MODEL_NAME)

    if not client.collection_exists(COLLECTION_NAME):
        return []
    
    query_vector = model.encode(query).tolist()


    response = client.query_points(collection_name=COLLECTION_NAME,
                                   query= query_vector,
                                   limit = top_k,
                                   score_threshold=score_threshold,
                                   with_payload=True)
    
    return [
        {"text":point.payload["text"],
         "source":point.payload["source"],
         "score":point.score}

        for point in response.points
    ]

def build_context_string(docs):
    if not docs:
        return "No relevant document found in Knowledge base"
    
    context = "RELEVANT KNOWLEDGE BASE CONTENT: \n\n"
    for i, doc in enumerate(docs):
        context = context + f"DOCUMENT {i}- Score {doc['score']} - Soucre {doc['source']}"
        context = context + f"{doc['text']} \n\n"
    return context
    

load_dotenv()


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a helpful, friendly voice assistant. "
                "When the user asks something that could be answered from the "
                "uploaded knowledge base (course materials, manuals, policies, etc.), "
                "ALWAYS call the search_knowledge_base tool first, then answer using "
                "the returned context. If the tool finds nothing relevant, say so "
                "honestly and answer from general knowledge instead. "
                "Keep spoken answers short — 2 to 4 sentences, no markdown, "
                "since this is read aloud by text-to-speech."
            )
        )

    @function_tool()
    async def search_knowledge_base(self,context:RunContext, query:str):
        docs = retrive_documents(query,top_k=3)
        print(f"RAG SEARCH ;{query} -> {len(docs)}. chunks has been found")
        return build_context_string(docs)

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt = openai.STT(),
        llm = openai.LLM(model="gpt-4o-mini"),
        tts= cartesia.TTS(model="sonic-2",voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
    )

    await session.start(room = ctx.room,
                        agent = Assistant(),
                        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()))
    
    await session.generate_reply(instructions="Greet the user warmly and offer your assistance by andwering questions from the uplaoded document")


if __name__=="__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))