from model.vertex import Vertex

class Graph:
    def __init__(self):
        # Inicializa el grafo con un diccionario vacío de vértices.
        self.vertices = {}

    def add_vertex(self, id, role="client"):
        # Agrega un nuevo vértice al grafo si no existe.
        # id: identificador del nodo.
        # role: tipo de nodo ('client', 'storage', 'recharge').
        if id not in self.vertices:
            self.vertices[id] = Vertex(id, role)

    def add_edge(self, from_id, to_id, weight):
        # Agrega una arista entre dos nodos con un peso dado (grafo no dirigido).
        if self._valid_vertex(from_id) and self._valid_vertex(to_id):
            self.vertices[from_id].add_neighbor(to_id, weight)
            self.vertices[to_id].add_neighbor(from_id, weight)

    def get_neighbors(self, id):
        # Devuelve los vecinos (id y peso) de un nodo dado.
        if self._valid_vertex(id):
            return self.vertices[id].get_neighbors()
        return []

    def has_edge(self, from_id, to_id):
        # Verifica si existe una arista entre dos nodos.
        return self._valid_vertex(from_id) and to_id in self.vertices[from_id].neighbors

    def edge_count(self):
        # Cuenta el número de aristas en el grafo (sin duplicar aristas).
        counted = set()
        count = 0
        for vertex in self.vertices.values():
            for neighbor in vertex.neighbors:
                pair = tuple(sorted([vertex.id, neighbor]))
                if pair not in counted:
                    counted.add(pair)
                    count += 1
        return count

    def _valid_vertex(self, id):
        # Verifica si un id corresponde a un vértice existente en el grafo.
        return id in self.vertices
