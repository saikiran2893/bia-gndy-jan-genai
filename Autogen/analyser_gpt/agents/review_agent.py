from autogen_agentchat.agents import AssistantAgent
from agents.prompts import  REVIEW_PROMPT



def create_review_agent(model_client):
    review_agent = AssistantAgent(
        name="ReviewAgent",
        model_client=model_client,
        system_message= REVIEW_PROMPT,
    )

    return review_agent