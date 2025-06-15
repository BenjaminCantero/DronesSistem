class Vertex:
    def __init__(self, id, role="client"):
        # Inicializa un nodo (vértice) del grafo.
        # id: identificador único del nodo.
        # role: tipo de nodo ('client', 'storage' o 'recharge'). Por defecto es 'client'.
        self.id = id
        self.role = role
        self.neighbors = {}  # Diccionario de vecinos: clave = id del vecino, valor = peso de la arista.

    def add_neighbor(self, neighbor_id, weight):
        # Agrega un vecino al nodo actual con el peso de la arista.
        self.neighbors[neighbor_id] = weight

    def get_neighbors(self):
        # Devuelve un iterable con los pares (id_vecino, peso) de los vecinos del nodo.
        return self.neighbors.items()
