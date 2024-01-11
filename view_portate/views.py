from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statistics import mean
import numpy as np


def createPlot(data, name):
    t = data["t"]
    Q = data["Q"]
    Q1 = Q.quantile(0.25)
    Q3 = Q.quantile(0.75)
    IQR = Q3 - Q1
    upper = Q3 + 3 * IQR
    lower = max([Q1 - 3 * IQR, 0])
    upper_array = np.where(Q >= upper)[0]
    lower_array = np.where(Q <= lower)[0]

    data.drop(index=list(upper_array), inplace=True)
    data.drop(index=list(lower_array), inplace=True)

    tt = data["t"]
    QQ = data["Q"]
    maxy = QQ.max()*1.2

    fig = go.Figure()

    fig1 = go.Scatter(x=t, y=Q)
    fig2 = go.Scatter(x=tt, y=QQ)
    fig.update_layout(
        template="ggplot2",
        yaxis_range=[0, maxy],
        xaxis_title="",
        yaxis_title="Portata [l/s]",
        paper_bgcolor='whitesmoke',
        height=800)
    fig.update_xaxes(nticks=10)
    fig.add_trace(fig1)
    fig.add_trace(fig2)





    fig2 = px.line(x=tt, y=QQ, template="ggplot2")
    fig2.update_layout(
        yaxis_range=[0, maxy ],
        xaxis_title="",
        yaxis_title="Portata [l/s]",
        paper_bgcolor='whitesmoke',
        height=800)
    fig2.update_xaxes(nticks=10)


    dataPlot = fig.to_html(name + ".html")

    return dataPlot


def createHistogram(data, Name):


    Q = data["Q"]
    fig = px.histogram(Q)
    fig.update_layout(
        xaxis_title="Portata [ l/s ]",
        yaxis_title="Conteggi [minuti]",
        paper_bgcolor='whitesmoke',
        bargap=0.1,
        height=500)
    dataPlot = fig.to_html("Histo"+Name+".html")

    return dataPlot

def createMap(data):
    Lat = data["Latitudine"]
    Long = data["Longitudine"]

    ### VISUALIZZAZIONE MISURATORI DIFFERENZIATA PER UTENTE ###
    # if request.user.username=='damiano':
    #     punto_misura=MeasureList["Punto di misura"]
    punto_misura = data["Punto di misura"]
    # else:
    # punto_misura = MeasureList.loc[MeasureList["Permesso"]==request.user.username,"Punto di misura"].tolist()

    MeanLat = mean(Lat)
    MeanLong = mean(Long)

    figure = folium.Figure()
    map = folium.Map(location=[MeanLat, MeanLong],
                     zoom_start=7,
                     control_scale=True,
                     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                     )
    folium.TileLayer(tiles='OpenStreetMap',opacity=0.4).add_to(map)

    for i in range(len(punto_misura)):
        folium.Marker(location=[Lat[i], Long[i]], tooltip=punto_misura[i], max_width=2000,
            icon=folium.Icon(icon='fa-weight-scale', prefix='fa')).add_to(map)

    map.add_to(figure)
    map_fig = map._repr_html_()
    return map_fig



@login_required
def home(request):
    Measures = pd.read_excel("view_portate/static/data/Misuratori installati.xlsx")
    map_fig = createMap(Measures)
    punto_misura = Measures["Punto di misura"]

    context = {"Map": map_fig, "punto_misura": punto_misura}
    return render(request, 'view_portate/HomePage.html', context)

@login_required
def merone1(request):
    data = pd.read_csv("view_portate/static/data/PortateMerone1.csv")
    graph = createPlot(data, 'Merone1')
    histo = createHistogram(data, 'Merone1')
    graphs = {'Graph': graph, 'Histo': histo, 'title': 'Merone I salto'}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

@login_required
def merone3(request):
    data = pd.read_csv("view_portate/static/data/PortateMerone3.csv")
    graph = createPlot(data, 'Merone3')
    histo = createHistogram(data, 'Merone3')
    graphs = {'Graph': graph, 'Histo': histo, 'title': 'Merone III salto'}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

@login_required
def trebisacce(request):
    data = pd.read_csv("view_portate/static/data/PortateTrebisacce.csv")
    graph = createPlot(data, 'Trebisacce')
    histo = createHistogram(data, 'Trebisacce')
    graphs = {'Graph': graph, 'Histo': histo, 'title': 'Partitore Trebisacce'}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

# Create your views here.
