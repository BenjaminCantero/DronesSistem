import networkx as nx
import matplotlib.pyplot as plt

class NetworkXAdapter:
    """
    Adaptador para convertir y visualizar el grafo propio usando NetworkX y Matplotlib.
    Permite mostrar los nodos y aristas con colores según el tipo de nodo.
    """
    def __init__(self, graph):
        # Guarda una referencia al grafo personalizado del proyecto
        self.graph = graph

    def to_networkx(self):
        """
        Convierte el grafo propio a un objeto de NetworkX.
        Añade los nodos con su atributo 'role' y las aristas con su peso.
        """
        G = nx.Graph()
        # Agrega nodos con su rol
        for vertex in self.graph.vertices.values():
            G.add_node(vertex.id, role=vertex.role)
        # Agrega aristas con su peso, evitando duplicados
        for vertex in self.graph.vertices.values():
            for neighbor, weight in vertex.neighbors.items():
                if not G.has_edge(vertex.id, neighbor):
                    G.add_edge(vertex.id, neighbor, weight=weight)
        return G

    def draw_graph(self):
        """
        Dibuja el grafo usando NetworkX y Matplotlib.
        Los nodos se colorean según su tipo (rol).
        """
        G = self.to_networkx()
        pos = nx.spring_layout(G, seed=42)  # Calcula posiciones para los nodos
        colors = [self._get_color(G.nodes[node]['role']) for node in G.nodes]

        fig, ax = plt.subplots(figsize=(4, 3))  # Tamaño pequeño de la imagen
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=500, ax=ax)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
        return fig

    def _get_color(self, role):
        """
        Devuelve el color correspondiente según el tipo de nodo.
        """
        if role == 'storage':
            return 'blue'
        elif role == 'recharge':
            return 'green'
        else:
            return 'orange'
