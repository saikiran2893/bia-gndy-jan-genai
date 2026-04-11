from models.openai_client import get_model_client
from teams.analysis_team import create_analysis_team
from autogen_agentchat.ui import Console

async def main(task: str):
    try:
        client = get_model_client()
        print("CLIENT:", client)
    except Exception as e:
        print(f"Error initializing model client: {e}")
    team = create_analysis_team(client)
    results = await Console(team.run_stream(task=task))
    print(f"\nStop reason: {results.stop_reason}")
    print("Final Results:", results)

    for msg in results.messages:
        print(f"{msg.source}: {msg.content}\n")

if __name__ == "__main__":
    import asyncio

    task = input("Enter the task for the agents to analyze: ")
    asyncio.run(main(task))