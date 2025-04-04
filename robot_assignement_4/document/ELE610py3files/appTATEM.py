#!/usr/bin/env python
""" appTATEM.py 
Set up a web-page on the computer that acts as a web-server.
The web-page can be viewed by any web-browser. The page shows a graphical
summary of TATEM log-files in JSON format, the files should be stored on
a catalog on this computer, 'data_path' defined in AppTATEM/getData.py.
This file also uses files on catalog AppTATEM.

downloaded Oct 6, 2023 from GitHub:  ELE630/TATEM/src/python/appTATEM.py 
last update on GitHub:  Ali-Jab committed on Oct 23, 2022
see GitHub for documentation
UiS, Karl Skretting made some minor changes
November 2023: renamed to ../ELE610/TATEM/appTATEM.py  and ../ELE610/py3/appTATEM.py
"""

# some packages that may be used for logging and debugging
# from cgitb import html
# from distutils.log import debug
# from setuptools._distutils import log
# from statistics import mode
# from turtle import fillcolor 
# from xmlrpc.server import DocCGIXMLRPCRequestHandler

from matplotlib.pyplot import title
import pandas as pd
import dash
from dash import Input, Output
from AppTATEM.plots import Plots
from AppTATEM.getData import GetData, data_path
from AppTATEM.layout import layout
import os
import plotly.graph_objects as go

appTATEM = dash.Dash(__name__, title="TATEM Visualizer")

# --------------------------------------------------
# html layout of the application, specified in layout.py
appTATEM.layout = layout
#end of application layout
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#application functionality and passing of information to tables and plots

@appTATEM.callback(
    Output('chart', 'figure'),
    [Input('datatable_id', 'selected_rows'),
    Input('dropdown', 'value'), 
    Input('filedropdown', 'value')]
)

# callback for updating plots that are shown below the table, 
# also handles what happens when one or more rows are selected
def update_plots(chosenRows, dropdownval, filedropdown):
    # class that is used to get information from dataframe, also converts file content to dataframe
    infoGetter = GetData()
    
    if filedropdown == 'allfiles':
        masterdf = infoGetter.combineFilesToOneDf()
        eventInfo = infoGetter.getEventInfo(masterdf)
        p = Plots(eventInfo, [], dropdownval)
        if dropdownval == 'eventResults':
            scatterAll = p.eventResultPlot()
        else:
            scatterAll = p.scatterAll()
        return scatterAll
    masterdf = infoGetter.fromFileToDF(os.path.join(data_path, filedropdown))
    if len(chosenRows)==0:
        dfFiltered = infoGetter.getEventInfo(masterdf)
        if dropdownval == 'eventResults':
            p = Plots(dfFiltered, chosenRows, dropdownval)
            scatterAll = p.eventResultPlot()
        else:
            # scatter plot of all tA, tO and tR values
            p = Plots(dfFiltered, chosenRows, dropdownval)
        
            scatterAll = p.scatterGivenFile()
        return scatterAll
    elif len(chosenRows) == 1:
        rowIndex = chosenRows[0]
        eventInfo = infoGetter.getEventInfo(masterdf)
        details = infoGetter.getDetails(masterdf)
        row = details.at[rowIndex, "details"]
        #check if there is any data in details to plot
        if len(row) == 0:
            p = Plots(infoGetter.getEventInfo(masterdf), chosenRows, dropdownval)
            signal = p.plotText("successError")
        else: 
            rowdf = pd.DataFrame.from_records(row)
            # make signal plots for DO, L1, L2, S1 and S2 in one figure
            p = Plots(rowdf, chosenRows, dropdownval)
            event = infoGetter.getEventInfoByIndex(chosenRows[0], eventInfo)
            signal = p.signal()
            # signal.add_vrect(x0=event['eventStart'], x1=(event['eventStart']+event['tA']), annotation_text='tA period', annotation_position='top left', fillcolor='#DAF7A6', opacity=0.25, line_width=2)
            # signal.add_vrect(x0=(event['operationStart']), x1=(event['operationStart']+event['tO']), annotation_text='tO period', annotation_position='top left', fillcolor='#66C7F4', opacity=0.25, line_width=2)
            # signal.add_vrect(x0=(event['operationStart']+event['tO']), x1=(event['operationStart']+event['tO']+event['tR']), annotation_text='tR period', annotation_position='top left', fillcolor='#F59031', opacity=0.25, line_width=2)
        return signal
    else:
        eventInfo = infoGetter.getEventInfo(masterdf)
        dfFiltered = eventInfo[eventInfo.index.isin(chosenRows)]
        # make a scatterplot for only the values of tA, tO and tR in chosenRows
        p = Plots(dfFiltered, chosenRows, dropdownval)
        try: 
            #p = Plots(dfFiltered, chosenRows, dropdownval)
            scatterChosen = p.scatterChosen()
            return scatterChosen
        except KeyError as keyerror:
            return p.plotText("keyError")

#callback for updating the table with data from the selected file(filedropdown)
@appTATEM.callback(
    Output('datatable_id', 'data'),
    Input('filedropdown', 'value')
)

def updateDatatable(filedropdown):
    infoGetter = GetData()
    if filedropdown == 'allfiles':
        masterdf = infoGetter.combineFilesToOneDf()
        eventInfo = infoGetter.getEventInfo(masterdf)
    else:
        masterdf = infoGetter.fromFileToDF(os.path.join(data_path, filedropdown))
        eventInfo = infoGetter.getEventInfo(masterdf)
    return eventInfo.to_dict('records')

#----------------------------------------------------------------------------

# callback for highlighting the racing track points
@appTATEM.callback(
    Output('raceTrack', 'figure'),
    Input('datatable_id', 'selected_rows')
)

def updateRacetrack(chosenRows):
    df = GetData()
    p = Plots(df, chosenRows, "")
    raceTrack = p.raceTrack()
    return raceTrack

#-----------------------------------------------------------------------------
#callback for updating the file dropdown

@appTATEM.callback(
    Output('filedropdown', 'options'),
    Input('filedropdown', 'value')
)

def updateFileDropdownList(value):
    newFileList = GetData().getReportList()
    filedropdown = [{'label': newFileList[i], 'value': newFileList[i]} for i in range(len(newFileList))]
    filedropdown.append({'label': 'All Files', 'value': 'allfiles'})
    return filedropdown
#-----------------------------------------------------------------------------
#callback for 
# @appTATEM.callback(
#     Output('chart', 'figure'),
#     Input('checkbox', 'value')
# )

# def compareAllFilesInDirectory(checkboxValue):
#     if checkboxValue != None:
#         infoGetter = GetData()
#         masterdf = infoGetter.combineFilesToOneDf()
#         eventInfo = infoGetter.getEventInfo(masterdf)
#         p = Plots(eventInfo, [], 'All files selected at once')
#         scatterAll = p.scatterAll()
#         return scatterAll

#-----------------------------------------------------------------------------
# run application

if __name__ =='__main__':
    appTATEM.run_server(debug=False)

