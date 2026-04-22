from config.settings import build_llm
from tools import ALL_TOOLS
from langgraph.prebuilt import ToolNode
from graph.state import TravelState
from utils.prompts import SYSTEM_PROMPT, REVISION_SYSTEM_PROMPT
from langchain_core.messages import HumanMessage, AIMessage,SystemMessage
from langgraph.types import interrupt
import textwrap
import time
import re
from openai import RateLimitError




_llm = build_llm()
_llm_with_tools = _llm.bind_tools(ALL_TOOLS)

_tool_executor = ToolNode(ALL_TOOLS)

_APPROVAL_TOKENS = {"approve","ok","looks good","perfect","yes","done","accept","good","nice","fine"}


MAX_REVISION = 5


def _invoke_with_retry(model, messages, retries: int = 3):
    """Retry LLM calls on transient OpenAI rate-limit errors."""
    for attempt in range(retries + 1):
        try:
            return model.invoke(messages)
        except RateLimitError as exc:
            if attempt == retries:
                raise
            # Prefer provider-suggested wait if present; otherwise exponential backoff.
            wait_match = re.search(r"try again in ([0-9]+(?:\.[0-9]+)?)s", str(exc), re.IGNORECASE)
            wait_seconds = float(wait_match.group(1)) if wait_match else (2 ** attempt)
            time.sleep(wait_seconds + 0.5)

def planner_node(state:TravelState)-> dict:
    """
    This is the reasoning node.

    Add the SYSTEM PROMPT and pass the full message to the LLM, return back the next message(which may containt tool call)
    """
    messages = state["messages"]
    messages = [SystemMessage(content=SYSTEM_PROMPT)]+messages
    response = _invoke_with_retry(_llm_with_tools, messages)
    return {"messages":response}


def draft_intenary_node(state:TravelState)-> dict:
    """
    called once tool-calling is complete.

    Ask LLM to synthesise all tool call output collected so far into the final structure plan and store it in the state itenary
    
    """

    draft_compilation_promt = """ All tool data has been collected,Now produce the complete ,formatted travel plan as describe in the 
                            system prompt. Include every section and final recommendation

                        """
    
    messages = state["messages"]
    messages = [SystemMessage(content=SYSTEM_PROMPT)]+messages+[HumanMessage(content=draft_compilation_promt)]
    response = _invoke_with_retry(_llm_with_tools, messages)
    itinerary = response.content
    return {"messages":[response],"itinerary":itinerary}



def human_review_node(state:TravelState)->dict:

    itinerary = state["itinerary"]
    banner = textwrap.dedent(f""" {itinerary}

                                Please review the plan above.
                             1. if your happy please approve the plan
                             2. or describe what is the changes you want
                             
                            """).strip()
    
    feedback = interrupt(banner)

    feedback_clean = feedback.strip()

    is_approved = any(tok in feedback_clean.lower() for tok in _APPROVAL_TOKENS)

    revision_count = state.get("revision",0)


    if revision_count >MAX_REVISION:
        is_approved = True

    return {"messages":[HumanMessage(content=feedback_clean)],"approved":is_approved,"human_feedback":feedback_clean}


def revise_node(state:TravelState) ->dict:
    """
    Rewrites the itenary based on the human feedback
    """

    feedback = state["human_feedback"]
    current_itinerary = state["itinerary"]
    revision_count = state.get("revision", 0)

    revision_prompt = REVISION_SYSTEM_PROMPT.format(feedback=feedback, current_itenary=current_itinerary)
    messages = [SystemMessage(content = revision_prompt),HumanMessage(content = "Please provide revised travel plan")]

    # Revision should produce a direct rewrite, not another tool-calling cycle.
    response = _invoke_with_retry(_llm, messages)
    revised_itinerary = (response.content or "").strip() or current_itinerary

    return {"messages":[response],"itinerary":revised_itinerary,"revision":revision_count + 1,"human_feedback":""}



def finalize_node(state:TravelState)-> dict:
    itinerary = state.get("itinerary", "")
    final_message = AIMessage(content=itinerary)

    return {"messages":[final_message],"approved":True}


def should_use_tools(state:TravelState)-> dict:
    messages = state["messages"][-1]
    if hasattr(messages,"tool_calls") and messages.tool_calls:
        return "tools" 
    
    return "draft_itenary"


def after_human_review(state:TravelState)-> dict:
    return "finalize" if state["approved"] else "revise"