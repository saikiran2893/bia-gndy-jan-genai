from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from agents.analyst_agent import create_analyst_agent
from agents.review_agent import create_review_agent



def create_analysis_team(model_client):
    analyst_agent = create_analyst_agent(model_client)
    review_agent = create_review_agent(model_client)

    # Create a team with the agents and termination conditions.
    team = RoundRobinGroupChat([analyst_agent, review_agent],
       termination_condition=TextMentionTermination("DONE") | MaxMessageTermination(12)
    )

    return team
