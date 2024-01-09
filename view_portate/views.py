from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import folium
import pandas as pd
import plotly.express as px
from statistics import mean

def createPlot(data, name):
    if name == "Merone3":
        yMax = 150
        name = "Merone III salto"
    elif name == "Merone1":
        yMax = 300
        name = "Merone I salto"
    else:
        yMax = 150

    t = data["t"]
    # t = pd.to_datetime(t, format='%d/%m/%Y %H:%M:%S')
    # Q = np.array(data["Q"])
    Q = data["Q"]
    fig1 = px.line(x=t, y=Q, template="ggplot2")
    fig1.update_layout(yaxis_range=[0, yMax], xaxis_title="", yaxis_title="Portata [l/s]", paper_bgcolor='whitesmoke',
                       height=800)
    dataPlot = fig1.to_html(name + ".html")

    return dataPlot


def createHistogram(data, Name):

    if Name == "Merone3":
        xMax = 120
        xMin = 0
        Name = "Merone III salto"
    elif Name == "Merone1":
        xMax = 160
        xMin = 0
        Name = "Merone I salto"
    else:
        xMax = 150
        xMin = -10

    Q = data["Q"]

    fig1 = px.histogram(Q) #, template="ggplot2", title=Name)
    fig1.update_layout(xaxis_range=[xMin, xMax], xaxis_title="Portata [ l/s ]", yaxis_title="Conteggi [minuti]", paper_bgcolor='whitesmoke', bargap=0.1, height=500)
    dataPlot = fig1.to_html("Histo"+Name+".html")

    return dataPlot


@login_required
def home(request):
    MeasureList = pd.read_excel("view_portate/static/data/Misuratori installati.xlsx")
    Lat = MeasureList["Latitudine"]
    Long = MeasureList["Longitudine"]
    # user_name = request.user.username
    if request.user.username=='damiano':
        punto_misura=MeasureList["Punto di misura"]
    else:
        punto_misura = MeasureList.loc[MeasureList["Permesso"]==request.user.username,"Punto di misura"].tolist()

    MeanLat = mean(Lat)
    MeanLong = mean(Long)

    figure = folium.Figure()
    map = folium.Map(location=[MeanLat, MeanLong], zoom_start=9, control_scale=True,
                     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                     )
    folium.TileLayer(tiles='OpenStreetMap',opacity=0.4).add_to(map)

    for i in range(len(punto_misura)):
        folium.Marker(location=[Lat[i], Long[i]], tooltip=punto_misura[i], max_width=2000,
            icon=folium.Icon(icon='fa-weight-scale', prefix='fa')).add_to(map)

    map.add_to(figure)
    # figure.render()
    figure2 = map._repr_html_()

    context = {"Map": figure2}
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
