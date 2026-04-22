from langgraph.graph import StateGraph, START,END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import TravelState



from nodes import (planner_node,draft_intenary_node,human_review_node,revise_node,finalize_node,_tool_executor,should_use_tools,after_human_review)


def build_travel_graph(checkpointer=None):

    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(TravelState)

    builder.add_node("planner",planner_node)
    builder.add_node("tools",_tool_executor)
    builder.add_node("draft_itenary",draft_intenary_node)
    builder.add_node("human_feedback",human_review_node)
    builder.add_node("revise",revise_node)
    builder.add_node("finalize",finalize_node)



    builder.add_edge(START,"planner")
    builder.add_conditional_edges("planner",should_use_tools,{"tools":"tools","draft_itenary":"draft_itenary"})

    builder.add_edge("tools","planner")
    builder.add_edge("draft_itenary","human_feedback")


    builder.add_conditional_edges("human_feedback",after_human_review,{"revise":"revise","finalize":"finalize"})

    builder.add_edge("revise","human_feedback")

    builder.add_edge("finalize",END)

    return builder.compile(checkpointer=checkpointer, interrupt_before=["human_feedback"])
