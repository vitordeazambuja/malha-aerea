import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# leitura do arquivo e filtragem com base em aeroportos médios e grandes
arquivo = "br-airports.csv"
aeroportos = pd.read_csv(arquivo)
aeroportos_principais = aeroportos[aeroportos['type'].isin(['large_airport', 'medium_airport'])]

# formatação e agrupamento dos aeroportos por estado
aeroportos_principais['Estado'] = aeroportos_principais['iso_region'].str.split('-').str[1]
aeroportos_principais_estado = aeroportos_principais.groupby('Estado').head(1)

# criação do grafo usando networkx
grafo = nx.Graph()

# adição dos aeroportos principais como nós do grafo
for _,aeroporto in aeroportos_principais_estado.iterrows():
    grafo.add_node(aeroporto['iata_code'], pos=(aeroporto['latitude_deg'],aeroporto['longitude_deg']))

# adição da distância entre cada aeroporto como as arestas do grafo usando geopy
for i, origem in aeroportos_principais_estado.iterrows():
    for j, destino in aeroportos_principais_estado.iterrows():
        if origem['iata_code'] != destino['iata_code']:
            distancia = geodesic((origem['latitude_deg'],origem['longitude_deg']),(destino['latitude_deg'], destino['longitude_deg'])).km
            distancia = round(distancia,2)
            grafo.add_edge(origem['iata_code'], destino['iata_code'], weight=distancia)

# criação do mapa usando basemap
m = Basemap(projection='merc', llcrnrlat=-35, urcrnrlat=10, llcrnrlon=-75, urcrnrlon=-30)

# obtendo a posição dos nós a partir das coordenadas usando basemap
pos = {aeroporto['iata_code']: m(aeroporto['longitude_deg'], aeroporto['latitude_deg']) 
       for _, aeroporto in aeroportos_principais_estado.iterrows()}

# configurando a figura e o eixo
fig, ax = plt.subplots(figsize=(10, 8))

# plotando o mapa
m.drawcountries(linewidth=1, color='black')
m.drawstates(linewidth=1, color='black')
m.drawcoastlines(linewidth=1)
m.fillcontinents(color='forestgreen',lake_color='forestgreen')
m.drawmapboundary(fill_color='deepskyblue')

# plotando o grafo no mapa
for aresta in grafo.edges(data=True):
    origem, destino, data = aresta
    x1, y1 = pos[origem]
    x2, y2 = pos[destino]
    ax.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5)
for no, (x, y) in pos.items():
    ax.scatter(x, y, s=50, c='blue', edgecolors='k', zorder=1)
    ax.text(x, y, no, fontsize=8, ha='center', color='white', zorder=2)

# mostrar o gráfico
plt.title("Malha Aérea do Brasil", fontsize=16)
plt.show()