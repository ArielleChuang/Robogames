# load up the libraries
import panel as pn
import pandas as pd
import altair as alt
from altair_transform import extract_data
import Robogame as rg
import time,json
import networkx as nx
import traceback
import numpy as np
import time
import holoviews as hv
import streamz
import streamz.dataframe
import random
from holoviews import opts
from holoviews.streams import Pipe, Buffer
import datetime as dt
import time

hv.extension('bokeh')

# we want to use bootstrap/template, tell Panel to load up what we need
pn.extension(design='bootstrap')

# load up the data
def getFrame():
    return(pd.DataFrame())

default_username = "bob"
default_server = "127.0.0.1"
default_port = "5000"

username_input= pn.widgets.TextInput(name='Username:', placeholder=default_username)
servername_input= pn.widgets.TextInput(name='Server', placeholder='127.0.0.1')
port_input= pn.widgets.TextInput(name='Port', placeholder='5000')
go_button = pn.widgets.Button(name='Run', button_type='primary')
static_text = pn.widgets.StaticText(name='State', value='Hit go to start')

sidecol = pn.Column()
sidecol.append(static_text)
sidecol.append(username_input)
sidecol.append(servername_input)
sidecol.append(port_input)
sidecol.append(go_button)

network = None
tree = None
info = None
hints = None

game = None

latest_update = pn.widgets.StaticText()

pipe = Pipe(data=[])
dmap = hv.DynamicMap(hv.Scatter, streams=[pipe]).opts(
    responsive=True, height=500, width=500, shared_axes=False, framewise=True,
    xlabel='time', ylabel='value', title='Time and Number'
)

pipe_bar = Pipe(data=[])
barmap =hv.DynamicMap(hv.Bars, streams=[pipe_bar]).opts(
    responsive=True, height=500, width=500, xlabel='id', ylabel='value', title='Cranial Uplink Bandwidth'
) 

def send():
    xxx, yyy = list(range(10)), [random.randint(0, 100) for y in range(10)]
    pipe.send((xxx, yyy))
#send()

def update():
    try:
        global game, static_text, network_view, tree_view, info_view, hints_view
        gt = game.getGameTime()
        network_view.object = game.getNetwork()
        tree_view.object = game.getTree()
        info_view.object = game.getRobotInfo()
        robots = game.getRobotInfo()
        hints_view.object = game.getHints()

        # hint
        
        predHints = game.getAllPredictionHints()
        predhints_df = pd.read_json(json.dumps(predHints),orient='records')
        #print(predhints_df)
        # print(predhints_df.groupby("id"))
        pipe.send((predhints_df["time"], predhints_df["value"]))
        hints = game.getHints(hintstart=0)['parts']
        hints_df = pd.read_json(json.dumps(hints),orient='records')
        hint_cub = hints_df.loc[hints_df['column']=='Cranial Uplink Bandwidth']
        #frequencies, edges = np.histogram(robots[['expires']], 20)
        pipe_bar.send((hint_cub["id"], hint_cub["value"]))
        latest_update.value = f'latest: {dt.datetime.now().strftime("%c")}'
        # send()
        #info_view.object = predhints_df
        #hints_view.object = pred
        #pipe.send(predhints_df)
    
        static_text.value = "Time left: " + str(gt['unitsleft'])
    except:
        print(traceback.format_exc())

def go_clicked(event):
    try:
        global game, network, tree, info, hints
        go_button.disabled = True
        uname = username_input.value
        if (uname == ""):
            uname = default_username
        server = servername_input.value
        if (server == ""):
            server = default_server
        port = port_input.value
        if (port == ""):
            port = default_port

        print(uname, server, port)
        game = rg.Robogame("bob",server=server,port=int(port))
        game.setReady()
        

        while(True):
            gametime = game.getGameTime()
            
            if ('Error' in gametime):
                static_text.value = "Error: "+str(gametime)
                break

            timetogo = gametime['gamestarttime_secs'] - gametime['servertime_secs']
            if (timetogo <= 0):
                static_text.value = "Let's go!"
                break
            static_text.value = "waiting to launch... game will start in " + str(int(timetogo))
            time.sleep(1) # sleep 1 second at a time, wait for the game to start

        # run a check every 5 seconds
        cb = pn.state.add_periodic_callback(update, 5000, timeout=60000)
    except:
        #print(traceback.format_exc())
        return

go_button.on_click(go_clicked)

template = pn.template.BootstrapTemplate(
    title='Robogames Demo',
    sidebar=sidecol,
)

sets = pd.read_csv('https://raw.githubusercontent.com/eytanadar/si649public/master/lab5/sets-simple.csv')

base = alt.Chart(sets).mark_circle().encode(
    x = alt.X('union:Q'),
    y = alt.Y('setid:N')
)

network_view = pn.pane.JSON({"message":"waiting for game to start"})
tree_view = pn.pane.JSON({"message":"waiting for game to start"})
info_view = pn.pane.DataFrame()
hints_view = pn.pane.JSON({"message":"waiting for game to start"})

# hints_view = pn.panel(pred)
#hints_view = pn.panel(base)

grid = pn.GridBox(ncols=2,nrows=2)
grid.append(network_view)
grid.append(tree_view)
# grid.append(info_view)
# grid.append(hints_view)
grid.append(pn.Column(dmap, latest_update))
grid.append(barmap)

template.main.append(grid)

template.servable()
