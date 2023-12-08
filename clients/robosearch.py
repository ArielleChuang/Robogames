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
st.set_page_config(page_title="Robot Search", layout="wide")
st.title('Robot Search: Tools to Find Relevant Bots')

# create the game, and mark it as ready
game = rg.Robogame("bob")
game.setReady()

col1, col2 = st.columns(2)

with col1:
    st.subheader('Identifying Robot Siblings')
    viz6 = st.empty()
    family = game.getTree()

    fam_net = nx.tree_graph(family)

    @st.cache
    def load_family_tree():
        family_data = game.getTree()
        fam_net = nx.tree_graph(family_data)
        return fam_net.copy()

    # Load the family tree once (cached)
    fam_net = load_family_tree()
   

    # Input box for the user to enter the node they want to search
    search_node = st.text_input("Enter a node to search:", "")

    # Assuming pos is not necessary or is predefined
    pos = nx.spring_layout(fam_net)

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

    viz6.pyplot(plt)



with col2:
    st.subheader('Positive Productivity')

    # Create an empty placeholder for the visualization
    viz7 = st.empty()

    robots = game.getRobotInfo()
    
    # Extracting robot productivity information
    robot_productivity = {}
    for index, row in robots.iterrows():
        robot_id = row['id']
        productivity = row['Productivity']
        if not pd.isnull(robot_id) and not pd.isnull(productivity):
            robot_productivity[robot_id] = productivity
    


    # Assuming pos is not necessary or is predefined
    pos = nx.spring_layout(fam_net)

    # Draw the networkx graph with explicit node positions
    # Color nodes based on productivity
    node_colors = ['green' if robot_productivity.get(node) and robot_productivity[node] > 0 else 'skyblue' for node in fam_net.nodes]
    nx.draw_networkx(fam_net, pos=pos, with_labels=True,
                     node_color=node_colors, node_size=500, font_size=10, font_color='black',
                     font_weight='bold', edge_color='gray', linewidths=0.5)

    # Highlight the searched node and its siblings if found
    try:
        search_node_id = int(search_node)
        if search_node_id in fam_net.nodes:
            # Find siblings of the searched node
            siblings = list(fam_net.neighbors(search_node_id))

            # Draw the searched node and its siblings in red
            nx.draw_networkx_nodes(fam_net, pos=pos,
                                   nodelist=[search_node_id] + siblings, node_color='red', node_size=700,
                                   alpha=0.8)
    except ValueError:
        # Handle the case where the input is not a valid integer
        pass

    # Display the matplotlib plot using st.pyplot
    viz7.pyplot(plt)
