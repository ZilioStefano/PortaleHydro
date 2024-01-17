from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# from plotly.subplots import make_subplots
from statistics import mean
import numpy as np
from datetime import datetime

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

def createPlotPortata(data, name):
    t = pd.to_datetime(data['t'], format='%d/%m/%Y,%H:%M:%S')
    Q_raw = data.iloc[:,1]
    #Q_filtered = data.iloc[:2]
    Q_smooth = data.iloc[:,3]
    Q_MEDIA = data.iloc[1,4]

    max_y = max(Q_smooth)
    # min_y = min(Q_smooth)
    range = max_y

    fig = go.Figure()

    plot1 = go.Scatter(x=t, y=Q_raw, name='Dati portata strumentali')
    #plot2 = go.Scatter(x=t, y=Q_filtered)
    plot3 = go.Scatter(x=t, y=Q_smooth, name='Media mobile sui dati filtrati')


    fig.add_trace(plot1)
    #fig.add_trace(plot2)
    fig.add_trace(plot3)
    fig.add_hline(y=Q_MEDIA, line_dash="dash", line_width=3, line_color="red",
                  annotation_text="Media",
                  annotation_position="top right")

    fig.update_layout(
        template="ggplot2",
        title=dict(text="Portata", font=dict(size=18), automargin=True, yref='paper'),
        yaxis_range=[-10, max_y + 1/2 * range],
        xaxis_title="",
        autosize=True,
        # width=800,
        height=700,
        yaxis_title="Portata (l/s)",
        paper_bgcolor='whitesmoke',
        legend=dict(
            #title="Portata",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01),
        margin=dict(l=20, r=20, t=20, b=20),
        colorway=["lightgray", colori.get("bluchiaro"), colori.get("arancione")]
        )

    dataPlot = fig.to_html("portata"+name+".html")

    return dataPlot

def createPlotHistogram(data, name):
    Q_filtered = data.iloc[:,2]
    fig = px.histogram(Q_filtered)
    fig.update_layout(
        title=dict(text="Istogramma portate", font=dict(size=15),automargin=True, yref='paper'),
        template="seaborn",
        autosize=True,
        # width=800,
        height=350,
        xaxis_title="Portata (l/s)",
        yaxis_title="Conteggi (min)",
        showlegend=False,
        # legend=dict(
        #     title="Istogramma portata",
        #     yanchor="top",
        #     y=0.99,
        #     xanchor="left",
        #     x=0.01),
        margin=dict(l=10, r=10, t=10, b=10),
        bargap=0.1
        )
    dataPlot = fig.to_html("histo"+name+".html")

    return dataPlot

def createPlotDurata(data, name):
    hours = data.iloc[:,0]
    QQ = data.iloc[:,1]
    max_y = max(QQ)
    # min_y = min(Q_smooth)
    range = max_y


    fig = px.line(x=hours, y=QQ)
    fig.update_layout(
        template="seaborn",
        title=dict(text="Curva di durata", font=dict(size=15),automargin=True, yref='paper'),
        autosize=True,
        yaxis_range=[-10, max_y + 1 / 2 * range],
        xaxis_range=[-10, max(hours)+100],
        # width=800,
        height=350,
        xaxis_title="Tempo (h)",
        yaxis_title="Portata (l/s)",
        showlegend=False,
        # legend=dict(
        #     title="Curva di Durata",
        #     yanchor="top",
        #     y=0.99,
        #     xanchor="left",
        #     x=0.01),
        margin=dict(l=10, r=10, t=10, b=10),
        )
    dataPlot = fig.to_html("durata"+name+".html")

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
                     zoom_start=5,
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


@login_required
def home(request):
    df_tab_misuratori = pd.read_excel("view_portate/static/data/Misuratori installati.xlsx")
    df_tab_misuratori = df_tab_misuratori.replace(np.nan, '', regex=True)
    df_tab_misuratori["Ultimo_timestamp"] = df_tab_misuratori["Ultimo_timestamp"].dt.date
    df_tab_misuratori['Ultimo_timestamp'] = df_tab_misuratori['Ultimo_timestamp'].apply(lambda x: x.strftime('%d/%m/%Y')if not pd.isnull(x) else '')


    map_fig = createMap(df_tab_misuratori)
    feed_dict = df_tab_misuratori.to_dict(orient="index").items()

    context = {"Map": map_fig, "tab_feed": feed_dict, "colori": colori}
    return render(request, 'view_portate/HomePage.html', context)

@login_required
def merone1(request):
    data_portata = pd.read_csv("view_portate/static/data/datiMerone1.csv")
    plot_portata = createPlotPortata(data_portata, 'Merone1')
    plot_histo = createPlotHistogram(data_portata, 'Merone1')
    data_durata = pd.read_csv("view_portate/static/data/durataMerone1.csv")
    plot_durata = createPlotDurata(data_durata, 'Merone1')
    graphs = {'portata': plot_portata,'histo': plot_histo,'durata': plot_durata,'title': 'Pagina dati - Merone I salto',"colori": colori}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

@login_required
def merone3(request):
    data_portata = pd.read_csv("view_portate/static/data/datiMerone3.csv")
    plot_portata = createPlotPortata(data_portata, 'Merone3')
    plot_histo = createPlotHistogram(data_portata, 'Merone3')
    data_durata = pd.read_csv("view_portate/static/data/durataMerone3.csv")
    plot_durata = createPlotDurata(data_durata, 'Merone3')
    graphs = {'portata': plot_portata,'histo': plot_histo,'durata': plot_durata,'title': 'Pagina dati - Merone III salto',"colori": colori}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)

@login_required
def trebisacce(request):
    data_portata = pd.read_csv("view_portate/static/data/datiTrebisacce.csv")
    plot_portata = createPlotPortata(data_portata, 'Trebisacce')
    plot_histo = createPlotHistogram(data_portata, 'Trebisacce')
    data_durata = pd.read_csv("view_portate/static/data/durataTrebisacce.csv")
    plot_durata = createPlotDurata(data_durata, 'Trebisacce')
    graphs = {'portata': plot_portata,'histo': plot_histo,'durata': plot_durata,'title': 'Pagina dati - Partitore Trebisacce',"colori": colori}

    return render(request, template_name='view_portate/PaginaDati.html', context=graphs)



