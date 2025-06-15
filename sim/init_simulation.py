import random
from model.graph import Graph

class SimulationInitializer:
    def __init__(self, n_nodes, m_edges):
        # Inicializa el generador de simulaciones con la cantidad de nodos y aristas deseadas.
        self.n_nodes = n_nodes
        self.m_edges = m_edges
        self.graph = Graph()  # Crea un grafo vacío

    def generate_connected_graph(self):
        # Genera un grafo conexo con los parámetros dados.
        self._create_vertices()        # Crea los nodos
        self._assign_roles()           # Asigna roles a cada nodo
        self._create_spanning_tree()   # Crea un árbol generador para asegurar conexión
        self._add_extra_edges()        # Agrega aristas extra hasta llegar a m_edges
        return self.graph

    def _create_vertices(self):
        # Crea los vértices numerados del 0 al n_nodes-1
        for i in range(self.n_nodes):
            self.graph.add_vertex(str(i))

    def _assign_roles(self):
        # Asigna roles a los nodos: 20% almacenamiento, 20% recarga, el resto clientes
        n_storage = int(self.n_nodes * 0.2)
        n_recharge = int(self.n_nodes * 0.2)
        n_clients = self.n_nodes - n_storage - n_recharge

        roles = (["storage"] * n_storage +
                 ["recharge"] * n_recharge +
                 ["client"] * n_clients)
        random.shuffle(roles)  # Mezcla los roles para asignarlos aleatoriamente

        for i, role in enumerate(roles):
            self.graph.vertices[str(i)].role = role  # Asigna el rol a cada nodo

    def _create_spanning_tree(self):
        # Crea un árbol generador aleatorio para asegurar que el grafo sea conexo
        nodes = list(self.graph.vertices.keys())
        random.shuffle(nodes)
        for i in range(self.n_nodes - 1):
            weight = random.randint(1, 20)  # Peso aleatorio para la arista
            self.graph.add_edge(nodes[i], nodes[i + 1], weight)

    def _add_extra_edges(self):
        # Agrega aristas adicionales aleatorias hasta alcanzar el número deseado de aristas
        nodes = list(self.graph.vertices.keys())
        while self.graph.edge_count() < self.m_edges:
            u, v = random.sample(nodes, 2)
            if not self.graph.has_edge(u, v):
                weight = random.randint(1, 20)
                self.graph.add_edge(u, v, weight)
