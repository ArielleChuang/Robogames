import streamlit as st
import time, json
import numpy as np
import altair as alt
import pandas as pd
import Robogame as rg
import networkx as nx 
import time, json
import matplotlib.pyplot as plt
import nx_altair as nxa
from graphviz import Digraph
import io
from PIL import Image
import copy

# Main content
st.set_page_config(page_title="Robogame Fam Net", layout="wide")
st.title('Family Network')


# create the game, and mark it as ready
game = rg.Robogame("bob")
game.setReady()

# # # Checking JSON file for getTree()
# json_data = game.getTree()

# # Check if JSON data is not None
# if json_data is not None:
#     # Print the structure of the JSON data
#     print("JSON data structure:")
#     print(json.dumps(json_data, indent=2))  # Pretty-print JSON
# else:
#     print("No JSON data received.")

col1, col2 = st.columns(2)

with col1:
        st.subheader('Network Image')
        viz7 = st.empty()
        family = game.getTree()
        fam_net = nx.tree_graph(family) 

        # Create a Digraph object
        graph = Digraph(format='png')

        # Add nodes to the graph
        for node in fam_net.nodes:
            graph.node(str(node))

        # Add edges to the graph
        for edge in fam_net.edges:
            graph.edge(str(edge[0]), str(edge[1]))

        # Generate PNG image from the graph
        png_data = graph.pipe(format='png')

        # Open the image using PIL
        image = Image.open(io.BytesIO(png_data))

        # Display the image in the Streamlit app
        viz5 = st.image(image, use_column_width=True, width=800)
        

@st.cache
def load_family_tree():
    family_data = game.getTree()
    fam_net = nx.tree_graph(family_data)
    return fam_net.copy()

# Load the family tree once (cached)
fam_net = load_family_tree()

with col2:
    st.subheader('Family Tree')

    # Create an empty placeholder for the visualization
    viz6 = st.empty()

    # Input box for the user to enter the node they want to search
    search_node = st.text_input("Enter a node to search:", "")

    # Assuming pos is not necessary or is predefined
    pos = nx.spring_layout(fam_net)

    # Draw the networkx graph with explicit node positions
    nx.draw_networkx(fam_net, pos=pos, with_labels=True, 
node_color='skyblue', node_size=500, font_size=10, font_color='black', 
font_weight='bold', edge_color='gray', linewidths=0.5)

    # Highlight the parent node and its descendants if found
    try:
        search_node_id = int(search_node)
        if search_node_id in fam_net.nodes:
            # Find parent node
            parent = list(fam_net.predecessors(search_node_id))
            if parent:
                # Find descendants of the parent node
                descendants = nx.descendants(fam_net, parent[0])

                # Draw the parent node and its descendants in red
                nx.draw_networkx_nodes(fam_net, pos=pos, 
nodelist=[parent[0]] + list(descendants), node_color='red', node_size=700, 
alpha=0.8)
    except ValueError:
        # Handle the case where the input is not a valid integer
        pass

    # Display the matplotlib plot using st.pyplot
    viz6.pyplot(plt)
