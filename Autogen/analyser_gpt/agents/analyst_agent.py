from autogen_agentchat.agents import AssistantAgent
from agents.prompts import ANALYST_PROMPT, REVIEW_PROMPT


def create_analyst_agent(model_client):
    analyst_agent = AssistantAgent(
        name="AnalystAgent",
        model_client=model_client,
        system_message= ANALYST_PROMPT,
    )

    return analyst_agent