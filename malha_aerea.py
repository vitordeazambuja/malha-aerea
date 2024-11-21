import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt

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

# cria uma cópia do dataframe para modificá-lo
aeroportos_principais_estado = aeroportos_principais_estado.copy()

# adicionando coluna Estado usando .loc
aeroportos_principais_estado.loc[:, 'Estado'] = aeroportos_principais_estado['iso_region'].str.split('-').str[1]

# obtendo a posição dos nós a partir das coordenadas
pos = {nodo: (data['pos'][0], data['pos'][1]) for nodo, data in grafo.nodes(data=True)}

# plotar o grafo
plt.figure(figsize=(10, 8))
nx.draw_networkx(grafo, pos, with_labels=True, node_size=500, font_size=10, node_color='lightblue')

# mostrar o gráfico
plt.title("Malha Aérea do Brasil")
plt.show()
