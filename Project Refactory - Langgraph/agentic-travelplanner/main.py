from graph.builder import build_travel_graph

from langchain_core.messages import HumanMessage
from langgraph.types import Command
import sys



THREAD_ID = "travel-session-001"
CONFIG = {"configurable":{"thread_id":THREAD_ID}}
LINE = "-" *70

def _stream_until_interrupt(graph, inputs_or_command, config: dict) -> bool:
    """
    Stream graph events until an interrupt or END.

    Prints any AI messages that appear during streaming.
    Returns True if an interrupt was hit, False if the graph finished.
    """
    hit_interrupt = False

    for event in graph.stream(inputs_or_command, config, stream_mode="values"):
        messages = event.get("messages", [])
        if messages:
            last = messages[-1]
            # Print intermediate AI messages (tool reasoning, etc.)
            if hasattr(last, "content") and last.content:
                role = getattr(last, "type", "ai")
                if role == "ai":
                    print(f"\n[Agent] {last.content[:300]}{'...' if len(last.content) > 300 else ''}")

    # Check if the graph is now interrupted
    snapshot = graph.get_state(config)
    if snapshot.next and "human_feedback" in snapshot.next:
        hit_interrupt = True

    return hit_interrupt


def run():
    print("Describe your trip (Destination,budget, currency, intrest,duration)")
    print(LINE)

    user_input = input("You: ").strip()


    if not user_input:
        print("No request Provided. Exiting")
        sys.exit(0)

    graph = build_travel_graph()


    intial_input = {"messages":HumanMessage(content=user_input)}

    print(LINE)

    # ──  Run until the first interrupt (human_review) ─────────────────
    hit_interrupt = _stream_until_interrupt(graph, intial_input, CONFIG)

     # ──  Human-in-the-loop revision loop ───────────────────────────────
    while hit_interrupt:
        snapshot      = graph.get_state(CONFIG)
        state_values  = snapshot.values

        # Display the itinerary
        itinerary = state_values.get("itinerary", "")
        revision  = state_values.get("revision", 0)

        print(f"\n{'═' * 70}")
        print(f"  TRAVEL PLAN  (revision #{revision})")
        print(f"{'═' * 70}\n")
        print(itinerary)
        print(f"\n{LINE}")

        if revision > 0:
            print(f"  This is revision #{revision} based on your feedback.")

        print("\n  Type  'approve'  to confirm the plan.")
        print("   Or describe what you'd like to change:")
        print(LINE)
        feedback = input("You: ").strip()

        if not feedback:
            feedback = "approve"    # empty input = silent approval

        # Resume the graph with the human's feedback
        resume_command = Command(resume=feedback)
        hit_interrupt  = _stream_until_interrupt(graph, resume_command, CONFIG)

    # ──  Print the final approved plan ─────────────────────────────────
    final_state = graph.get_state(CONFIG).values
    final_plan  = final_state.get("itinerary", "")
    revisions   = final_state.get("revision", 0)

    print(f"\n{'═' * 70}")
    print("  FINAL APPROVED TRAVEL PLAN")
    print(f"{'═' * 70}\n")
    print(final_plan)
    print(f"\n Approved after {revisions} revision(s).  Have a wonderful trip! ")
    

if __name__ == "__main__":
    run()