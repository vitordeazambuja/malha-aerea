import pandas as pd
import networkx as nx
from geopy.distance import geodesic

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