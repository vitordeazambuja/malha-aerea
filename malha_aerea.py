import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# ler o arquivo e filtrar com base em aeroportos médios e grandes
arquivo = "br-airports.csv"
aeroportos = pd.read_csv(arquivo)
aeroportos_principais = aeroportos[aeroportos['type'].isin(['large_airport', 'medium_airport'])]

# formatar e agrupar os aeroportos por estado
aeroportos_principais['Estado'] = aeroportos_principais['iso_region'].str.split('-').str[1]
aeroportos_principais_estado = aeroportos_principais.groupby('Estado').head(1)

# criar o grafo usando networkx
grafo = nx.Graph()

# adicionar os aeroportos principais como nós do grafo
for _,aeroporto in aeroportos_principais_estado.iterrows():
    grafo.add_node(aeroporto['iata_code'], pos=(aeroporto['latitude_deg'],aeroporto['longitude_deg']))

# transformar os nós do grafo em lista
lista_nos = list(grafo.nodes)

# adicionar a distância entre cada aeroporto como arestas do grafo usando geopy
for i, origem in enumerate(lista_nos):
    for offset in range(1, 4):
        destino_idx = (i + offset) % len(lista_nos)
        destino = lista_nos[destino_idx]
        origem_latlon = (grafo.nodes[origem]['pos'][0], grafo.nodes[origem]['pos'][1])
        destino_latlon = (grafo.nodes[destino]['pos'][0], grafo.nodes[destino]['pos'][1])
        distancia = geodesic(origem_latlon, destino_latlon).km
        grafo.add_edge(origem, destino, weight=round(distancia, 2))


# criar o primeiro mapa usando basemap
m = Basemap(projection='merc', llcrnrlat=-35, urcrnrlat=10, llcrnrlon=-75, urcrnrlon=-30)

# obter a posição dos nós a partir das coordenadas usando basemap
pos = {aeroporto['iata_code']: m(aeroporto['longitude_deg'], aeroporto['latitude_deg']) 
       for _, aeroporto in aeroportos_principais_estado.iterrows()}

# configurar a figura e o eixo do primeiro gráfico
fig, ax = plt.subplots(figsize=(10, 8))

# plotar o primeiro mapa
m.drawcountries(linewidth=1, color='black')
m.drawstates(linewidth=1, color='black')
m.drawcoastlines(linewidth=1)
m.fillcontinents(color='forestgreen',lake_color='forestgreen')
m.drawmapboundary(fill_color='deepskyblue')

# plotar o grafo no primeiro mapa
for aresta in grafo.edges(data=True):
    origem, destino, data = aresta
    x1, y1 = pos[origem]
    x2, y2 = pos[destino]
    ax.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5)
for no, (x, y) in pos.items():
    ax.scatter(x, y, s=50, c='blue', edgecolors='k', zorder=1)
    ax.text(x, y, no, fontsize=8, ha='center', color='white', zorder=2)

# mostrar o primeiro gráfico
plt.title("Malha Aérea do Brasil", fontsize=16)
plt.show()


# definir o aeroporto de origem e o aeroporto de destino
origem = 'GRU'
destino = 'BVB'


# calcular o menor caminho entre os aeroportos e calcular a distância total entre eles
menor_caminho = nx.shortest_path(grafo, source=origem, target=destino, weight='weight')
distancia_total = nx.shortest_path_length(grafo,source=origem, target=destino, weight='weight')


# configurar a figura e o eixo do segundo gráfico
fig2, ax2 = plt.subplots(figsize=(10, 8))

# criar o segundo mapa usando basemap
m2 = Basemap(projection='merc', llcrnrlat=-35, urcrnrlat=10, llcrnrlon=-75, urcrnrlon=-30, ax=ax2)

# plotar o segundo mapa
m2.drawcountries(linewidth=1, color='black')
m2.drawstates(linewidth=1, color='black')
m2.drawcoastlines(linewidth=1)
m2.fillcontinents(color='forestgreen', lake_color='deepskyblue')
m2.drawmapboundary(fill_color='deepskyblue')

# plotar o grafo no segundo mapa
for no, (x, y) in pos.items():
    ax2.scatter(x, y, s=50, c='blue', edgecolors='k', zorder=1)
    ax2.text(x, y, no, fontsize=8, ha='center', color='white', zorder=2)
for aresta in grafo.edges(data=True):
    origem, destino, data = aresta
    x1, y1 = pos[origem]
    x2, y2 = pos[destino]
    ax2.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5)

# destacar o menor caminho
for i in range(len(menor_caminho) - 1):
    origem, destino = menor_caminho[i], menor_caminho[i + 1]
    x1, y1 = pos[origem]
    x2, y2 = pos[destino]
    ax2.plot([x1, x2], [y1, y2], color='red', linewidth=1, zorder=3)

# mostrar o segundo gráfico
plt.title(f"Menor caminho entre {menor_caminho[0]} e {menor_caminho[-1]} com a distância total de: {distancia_total}km", fontsize=16)
plt.show()