# Menor Caminho - Malha Aérea do Brasil

## Visão Geral
Um projeto em Python que utiliza grafos para modelar aeroportos geograficamente e simular rotas aéreas. A aplicação calcula a rota de menor distância entre os aeroportos com o algoritmo de Dijkstra e a destaca no mapa.

## Funcionalidades
- Visualização da malha aérea do Brasil em um mapa com os principais aeroportos médios e grandes.
- Interface gráfica permite selecionar estados e aeroportos de origem e destino.
- Cálculo do menor caminho entre dois aeroportos usando o algoritmo de Dijkstra, considerando a distância geográfica.
- Exibe a rota calculada no mapa, juntamente com a distância total.

## Pré-requisitos
Para executar o projeto, você precisará que o arquivo br-airports.csv esteja no mesmo diretório do arquivo malha_aerea.py e que as seguintes bibliotecas estejam instaladas no Python:

- pandas
- networkx
- geopy
- matplotlib
- mpl_toolkits.basemap
- PyQt5

As bibliotecas podem ser instaladas com:

`pip install pandas networkx geopy matplotlib basemap PyQt5`

## Execução
Execute o script com:

`python malha_aerea.py`

## Uso da Interface
1. Escolha o estado e o aeroporto de origem.
2. Escolha o estado e o aeroporto de destino.
3. Clique no botão Calcular Rota.
4. A rota será destacada no mapa com a distância total exibida.
