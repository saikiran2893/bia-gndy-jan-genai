from graph.builder import build_travel_graph

def export_langgraph_image():
    graph = build_travel_graph()

    # Get compiled graph visualization object
    graph_viz = graph.get_graph()


    # Save PNG image
    png_bytes = graph_viz.draw_mermaid_png()
    with open("travel_graph.png", "wb") as f:
        f.write(png_bytes)

    print("Saved:  travel_graph.png")

if __name__ == "__main__":
    export_langgraph_image()