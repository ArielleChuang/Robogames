# Team2 Roboviz Games  
To run the file to see the family network visualization, run streamlit run tree_dashboard.py  
To run the file to see the bidding function, social network, number generator and dynamic dataframe for productivity, run streamlit run net_dashboard.py   
**#List of packages that need to be installed in local environment**  
import streamlit as st  
import time  
import numpy as np  
import altair as alt  
import pandas as pd  
import Robogame as rg  
import networkx as nx   
import time, json  
import matplotlib.pyplot as plt  
from pyvis.network import Network  
from streamlit.components.v1 import html as components_html  
from stvis import pv_static  
import copy  
from streamlit_echarts import st_echarts   
from pyecharts import options as opts   
Given the game design, it may take time for color encodings to show on the family tree visualization or on the dynamic dataframe, since
productivity is only shown after robots have declared a team. If you find errors or warnings in the dashboard upon running, please make sure your
streamlit version is the most recent (ver 1.28)
