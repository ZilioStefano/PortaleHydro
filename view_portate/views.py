from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statistics import mean
import numpy as np

colori={"bluscuro":"#30415d",#0bluscuro
        "blu":"#004fa3",#1blu
        "bluchiaro":"#88a4ca",#2bluchiaro
        "arancione":"#ffa700",#3arancione
        "grigio":"#6a7782",#4grigio
        "rosso":"#ff7376",#5rosso
        "azzurro":"#b6dae0",#6azzurro
        "verde":"#a5c357",#7verde
        "arancione2":"#ff9c0d",#8arancione2
        "giallo":"#f2cf65",#9giallo
        }

colors=['lightgray', #0
        'pink', #1
        'darkred', #2
        'red', #3
        'lightblue', #4
        'darkblue', #5
        'darkpurple', #6
        'green', #7
        'blue', #8
        'lightgreen', #9
        'lightred', #10
        'gray', #11
        'cadetblue', #12
        'orange', #13
        'purple', #14
        'darkgreen', #15
        'black', #16
        'beige',  #17
        'white' #18
        ]

def createPlot(data, name, column):
    t = pd.to_datetime(data['t'], format='%d/%m/%Y,%H:%M:%S')
    Q_raw = data.iloc[:,1]
    Q_filtered = data.iloc[:,column[2]]
    Q_smooth = data.iloc[:,column[3]]

    max_y = max(Q_raw)
    min_y = min(Q_raw)
    range = max_y - min_y

    fig = go.Figure()

    plot1 = go.Scatter(x=t, y=Q_raw)
    plot2 = go.Scatter(x=t, y=Q_filtered)
    plot3 = go.Scatter(x=t, y=Q_smooth)

    fig.add_trace(plot1)
    fig.add_trace(plot2)
    fig.add_trace(plot3)

    fig.update_layout(
        template="ggplot2",
        yaxis_range=[min_y - 1 / 3 * range, max_y + 1 / 3 * range],
        xaxis_title="",
        yaxis_title="Portata [l/s]",
        paper_bgcolor='whitesmoke',
        height=800,
        colorway=[colori.get("grigio"), colori.get("bluchiaro"), colori.get("arancione")]
        )

    dataPlot = fig.to_html(name + ".html")

    return dataPlot

def createHistogram(data, Name, column):
    Q_filtered = data.iloc[:,column[2]]
    fig = px.histogram(Q_filtered)
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
    MeanLat = mean(Lat)
    MeanLong = mean(Long)
    Stato = data['Stato']

    ### VISUALIZZAZIONE MISURATORI DIFFERENZIATA PER UTENTE ###
    # if request.user.username=='damiano':
    #     punto_misura=MeasureList["Punto di misura"]
    punti_misura = data["Punto_di_misura"]
    # else:
    # punto_misura = MeasureList.loc[MeasureList["Permesso"]==request.user.username,"Punto di misura"].tolist()

    figure = folium.Figure()
    map = folium.Map(location=[MeanLat, MeanLong],
                     zoom_start=7,
                     control_scale=True,
                     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                     )
    folium.TileLayer(tiles='OpenStreetMap', opacity=0.4).add_to(map)

    #aggiunge icona
    for i in range(len(punti_misura)):
        if Stato[i] == "In servizio":
            MarkerColor = colors[8]

        elif Stato[i] == "Guasto":
            MarkerColor = colors[3]

        elif Stato[i] == "Da installare":
            MarkerColor = colors[13]

        elif Stato[i] == "In valutazione":
            MarkerColor = colors[16] #black

        folium.Marker(location=[Lat[i], Long[i]], tooltip=punti_misura[i], max_width=2000,
            icon=folium.Icon(icon='fa-weight-scale', prefix='fa', color=MarkerColor)).add_to(map)

    map.add_to(figure)
    map_fig = map._repr_html_()
    return map_fig

def ff(x):
    if len(str(x)) <= 3: return 1
    else: return 0
def create_feed(MisuratoriTab):

    ModelloClean = MisuratoriTab["Modello"].values
    head = MisuratoriTab.head()
    MedDevStr = []

    UltimoValore = MisuratoriTab["Ultimo_valore"].values
    UltimoTimeStamp = MisuratoriTab["Ultimo_timestamp"].values
    UltimoTimeStamp = pd.to_datetime(UltimoTimeStamp)

    Medie = MisuratoriTab["Portata_media_globale"].values
    Devs = MisuratoriTab["Dev_portata"].values
    lastMeasure = []

    StateColor = []
    StatoMisuratori = MisuratoriTab["Stato"]

    for i in range(len(ModelloClean)):

        if str(ModelloClean[i]) == "nan":
            ModelloClean[i] = ""

        if pd.isnull(UltimoTimeStamp[i]):
            lastMeasure.append("")
        else:
            lastMeasure.append(str(UltimoValore[i])+" l/s al "+UltimoTimeStamp[i].strftime('%d/%m/%Y %H:%M'))

        if np.isnan(Medie[i]):
            MedDevStr.append("")
        else:
            string = str(Medie[i]) +chr(177)+ str(Devs[i])+" l/s"
            # string = string.replace("Â", " ")
            MedDevStr.append(string)

        if StatoMisuratori[i] == "In servizio":
            StateColor.append("green")

    FeedDict = {"testa": head, "punti_misura": MisuratoriTab["Punto_di_misura"], "Modello": ModelloClean, "Media": MedDevStr, "Ultima_misura": lastMeasure, "Stato": StatoMisuratori,"colore": StateColor}
    # FeedDf = pd.DataFrame(FeedDict)

    # FeedDf = FeedDf.style.set_properties(**{'color': "black", 'align': "left", 'backgroundcolor': "yellow"})
    # FeedDf = FeedDf.style.set_properties(
    #     **{"text-align": "left"}
    # )

    # FeedDf.style.applymap(ff)
    # FeedDf.to_html("Feed.html", index=False, classes=["table-bordered", "table-striped", "table-hover"], justify='left')

    # with open('Feed.html', 'r') as f:
    #     FeedHTML = f.read()

    return FeedDict


    # Bancale.to_html("OpenBancale.html")

@login_required
def home(request):
    df_tab_misuratori = pd.read_excel("view_portate/static/data/Misuratori installati.xlsx")
    df_tab_misuratori = df_tab_misuratori.replace(np.nan, '', regex=True) #sostituisce nan con stringaq vuota

    map_fig = createMap(df_tab_misuratori)
    feed_dict = df_tab_misuratori.to_dict(orient="index").items()

    context = {"Map": map_fig, "tab_feed": feed_dict, "colori": colori}
    return render(request, 'view_portate/HomePage.html', context)

@login_required
def merone1(request):
    data = pd.read_csv("view_portate/static/data/datiMerone1.csv")
    colonne = [0, 1, 2, 3]
    graph = createPlot(data, 'Merone1', colonne)
    histo = createHistogram(data, 'Merone1', colonne)
    graphs = {'Graph': graph,'Histo': histo,'title': 'Merone I salto',"colori": colori}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

@login_required
def merone3(request):
    data = pd.read_csv("view_portate/static/data/datiMerone3.csv")
    colonne = [0, 1, 2, 3]
    graph = createPlot(data, 'Merone3', colonne)
    histo = createHistogram(data, 'Merone3', colonne)
    graphs = {'Graph': graph,'Histo': histo,'title': 'Merone III salto',"colori": colori}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

@login_required
def trebisacce(request):
    colonne = [0, 1, 3, 4]
    data = pd.read_csv("view_portate/static/data/datiTrebisacce.csv")
    graph = createPlot(data, 'Trebisacce', colonne)
    histo = createHistogram(data, 'Trebisacce', colonne)
    graphs = {'Graph': graph,'Histo': histo,'title': 'Partitore Trebisacce',"colori": colori}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

# Create your views here.
