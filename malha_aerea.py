import sys
import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QComboBox, QPushButton
)
from mpl_toolkits.basemap import Basemap

# função para criar o grafo usando networkx
def criar_grafo(aeroportos_principais_estado):
    # criar o grafo
    grafo = nx.Graph()

    # adicionar os aeroportos principais como nós do grafo
    for _, aeroporto in aeroportos_principais_estado.iterrows():
        grafo.add_node(aeroporto['iata_code'], pos=(aeroporto['latitude_deg'], aeroporto['longitude_deg']))

    # transformar os nós do grafo em lista
    lista_nos = list(grafo.nodes)

    # adicionar a distância entre cada aeroporto como arestas do grafo usando geopy
    for i, origem in enumerate(lista_nos):
        for offset in range(1, 4):
            destino_idx = (i + offset) % len(lista_nos)
            destino = lista_nos[destino_idx]
            origem_latlon = grafo.nodes[origem]['pos']
            destino_latlon = grafo.nodes[destino]['pos']
            distancia = geodesic(origem_latlon, destino_latlon).km
            grafo.add_edge(origem, destino, weight=round(distancia, 2))
    
    # retornar grafo
    return grafo

# função para plotar o gráfico inicial
def plotar_grafico(aeroportos_principais_estado, grafo):
    # configurar a figura e o eixo do gráfico
    fig, ax = plt.subplots(figsize=(10, 8))

    # criar o mapa usando basemap
    m = Basemap(projection='merc', llcrnrlat=-35, urcrnrlat=10, llcrnrlon=-75, urcrnrlon=-30, ax=ax)

    # plotar o mapa
    m.drawcountries(linewidth=1, color='black')
    m.drawstates(linewidth=1, color='black')
    m.drawcoastlines(linewidth=1)
    m.fillcontinents(color='forestgreen', lake_color='deepskyblue')
    m.drawmapboundary(fill_color='deepskyblue')
    
    # obter a posição dos nós a partir das coordenadas usando basemap
    pos = {aeroporto['iata_code']: m(aeroporto['longitude_deg'], aeroporto['latitude_deg'])
           for _, aeroporto in aeroportos_principais_estado.iterrows()}
    
    # plotar o grafo no mapa
    for aresta in grafo.edges(data=True):
        origem, destino, data = aresta
        x1, y1 = pos[origem]
        x2, y2 = pos[destino]
        ax.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5)
    for no, (x, y) in pos.items():
        ax.scatter(x, y, s=50, c='blue', edgecolors='k', zorder=1)
        ax.text(x, y, no, fontsize=8, ha='center', color='white', zorder=2)
    
    # retorna a figura e a posição dos nós
    return fig, pos

# classe para implementar a interface
class MainWindow(QMainWindow):
    # função de inicialização
    def __init__(self, aeroportos_principais_estado, grafo):
        # definir variáveis
        super().__init__()
        self.aeroportos_principais_estado = aeroportos_principais_estado
        self.grafo = grafo

        # configurar a janela
        self.setWindowTitle("Malha Aérea do Brasil")
        self.setGeometry(100, 100, 1000, 800)

        # configurar o layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # mostrar o gráfico inicial
        self.fig_base, self.pos = plotar_grafico(self.aeroportos_principais_estado, self.grafo)
        self.canvas_base = FigureCanvas(self.fig_base)
        self.layout.addWidget(self.canvas_base)

        # criar o layout de controle
        self.controls_layout = QHBoxLayout()
        self.layout.addLayout(self.controls_layout)

        # criar as comboboxes e o botão
        self.estado_origem_cb = QComboBox()
        self.estado_destino_cb = QComboBox()
        self.aeroporto_origem_cb = QComboBox()
        self.aeroporto_destino_cb = QComboBox()
        self.calcular_btn = QPushButton("Calcular Rota")
        
        # configurar as comboboxes para exibir os Estados
        estados = sorted(self.aeroportos_principais_estado['Estado'].unique())
        self.estado_origem_cb.addItems(estados)
        self.estado_destino_cb.addItems(estados)
        
        # implementar a conexão da combobox com a função de atualização
        self.estado_origem_cb.currentIndexChanged.connect(self.atualizar_aeroportos_origem)
        self.estado_destino_cb.currentIndexChanged.connect(self.atualizar_aeroportos_destino)
        
        # chamada das funções de atualização
        self.atualizar_aeroportos_origem()
        self.atualizar_aeroportos_destino()

        # adicionar labels, comboboxes e botão ao layout
        self.controls_layout.addWidget(QLabel("Estado de Origem:"))
        self.controls_layout.addWidget(self.estado_origem_cb)
        self.controls_layout.addWidget(QLabel("Aeroporto de Origem:"))
        self.controls_layout.addWidget(self.aeroporto_origem_cb)
        self.controls_layout.addWidget(QLabel("Estado de Destino:"))
        self.controls_layout.addWidget(self.estado_destino_cb)
        self.controls_layout.addWidget(QLabel("Aeroporto de Destino:"))
        self.controls_layout.addWidget(self.aeroporto_destino_cb)
        self.controls_layout.addWidget(self.calcular_btn)

        # implementar funcionalidade de calcular rota ao botão
        self.calcular_btn.clicked.connect(self.calcular_rota)

    # função para atualizar os aeroportos de origem
    def atualizar_aeroportos_origem(self):
        # obter o valor do Estado de origem da combobox
        estado = self.estado_origem_cb.currentText()

        # filtrar os dados para obter os aeroportos somente do Estado selecionado
        aeroportos = self.aeroportos_principais_estado[self.aeroportos_principais_estado['Estado'] == estado]

        # limpa os itens da combobox do aeroporto de origem quando for trocar o Estado selecionado
        self.aeroporto_origem_cb.clear()

        # filtrar aeroportos validos de um Estado e evitar erro de NaN
        aeroportos_validos = aeroportos['iata_code'].dropna().astype(str)

        # adicionar os aeroportos válidos na combobox
        self.aeroporto_origem_cb.addItems(aeroportos_validos)

    # função para atualizar os aeroportos de destino
    def atualizar_aeroportos_destino(self):
        # obter o valor do Estado de origem da combobox
        estado = self.estado_destino_cb.currentText()

        # filtrar os dados para obter os aeroportos somente do Estado selecionado
        aeroportos = self.aeroportos_principais_estado[self.aeroportos_principais_estado['Estado'] == estado]

        # limpa os itens da combobox do aeroporto de origem quando for trocar o Estado selecionado
        self.aeroporto_destino_cb.clear()

        # filtrar aeroportos validos de um Estado e evitar erro de NaN
        aeroportos_validos = aeroportos['iata_code'].dropna().astype(str)

        # adicionar os aeroportos válidos na combobox
        self.aeroporto_destino_cb.addItems(aeroportos_validos)

    # função para calcular a menor rota e a distância e gerar o segundo gráfico
    def calcular_rota(self):
        # obter a origem e o destino com base na opção selecionada na combobox
        origem = self.aeroporto_origem_cb.currentText()
        destino = self.aeroporto_destino_cb.currentText()
        
        # cálculo do menor caminho e da distância usando dijkstra e networkx
        menor_caminho = nx.shortest_path(self.grafo, source=origem, target=destino, weight='weight', method='dijkstra')
        distancia_total = round(nx.shortest_path_length(self.grafo, source=origem, target=destino, weight='weight', method='dijkstra'), 2)

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
        
        # plotar as arestas
        for aresta in self.grafo.edges(data=True):
            origem, destino, data = aresta
            x1, y1 = self.pos[origem]
            x2, y2 = self.pos[destino]
            ax2.plot([x1, x2], [y1, y2], color='gray', linewidth=0.5)
        
        # plotar a aresta de menor caminho e destacar no mapa
        for i in range(len(menor_caminho) - 1):
            origem, destino = menor_caminho[i], menor_caminho[i + 1]
            x1, y1 = self.pos[origem]
            x2, y2 = self.pos[destino]
            ax2.plot([x1, x2], [y1, y2], color='red', linewidth=1, zorder=3)
        
        # plotar os nós
        for no, (x, y) in self.pos.items():
            ax2.scatter(x, y, s=50, c='blue', edgecolors='k', zorder=1)
            ax2.text(x, y, no, fontsize=8, ha='center', color='white', zorder=2)
        
        # definir o título do mapa para mostrar os aeroportos e a distância total do menor caminho entre os nós
        ax2.set_title(f"Menor caminho entre {menor_caminho[0]} e {menor_caminho[-1]} com distância total de: {distancia_total}km", fontsize=14)

        # atualizar o mapa na interface
        self.layout.removeWidget(self.canvas_base)
        self.canvas_base.deleteLater()
        self.canvas_base = FigureCanvas(fig2)
        self.layout.insertWidget(0, self.canvas_base)

# função main
def main():
    # ler o arquivo e filtrar com base em aeroportos médios e grandes
    arquivo = "br-airports.csv"
    aeroportos = pd.read_csv(arquivo)
    aeroportos_principais = aeroportos[aeroportos['type'].isin(['large_airport', 'medium_airport'])]

    # formatar e agrupar os aeroportos por estado
    aeroportos_principais['Estado'] = aeroportos_principais['iso_region'].str.split('-').str[1]
    aeroportos_principais_estado = aeroportos_principais.groupby('Estado').head(1)
    
    # criar o grafo chamando a função criar_grafo
    grafo = criar_grafo(aeroportos_principais_estado)
    
    # inicializar a aplicação
    app = QApplication(sys.argv)
    main_window = MainWindow(aeroportos_principais_estado, grafo)
    main_window.show()
    sys.exit(app.exec_())

# chamada da função main
main()
