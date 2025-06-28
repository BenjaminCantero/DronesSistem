from model.vertex import Vertex

class Graph:
    def __init__(self):
        # Inicializa el grafo con un diccionario vacío de vértices.
        self.vertices = {}

    def add_vertex(self, id, role="client", lat=None, lon=None):
        # Agrega un nuevo vértice al grafo si no existe, con soporte para lat/lon.
        if id not in self.vertices:
            self.vertices[id] = Vertex(id, role, lat, lon)

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

    def edges(self):
        """
        Devuelve un generador de todas las aristas del grafo como (from_id, to_id, weight).
        Cada arista aparece solo una vez (grafo no dirigido).
        """
        seen = set()
        for from_id, vertex in self.vertices.items():
            for to_id, weight in vertex.neighbors.items():
                edge = tuple(sorted([from_id, to_id]))
                if edge not in seen:
                    seen.add(edge)
                    yield (from_id, to_id, weight)

    def _valid_vertex(self, id):
        # Verifica si un id corresponde a un vértice existente en el grafo.
        return id in self.vertices

    def kruskal_mst(self):
        """
        Algoritmo de Kruskal para encontrar el Árbol de Expansión Mínima (MST).
        Devuelve una lista de aristas (u, v, peso) que forman el MST.
        """
        parent = {}
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        def union(u, v):
            pu, pv = find(u), find(v)
            parent[pu] = pv
        # Inicializar conjuntos
        for v in self.vertices:
            parent[v] = v
        # Ordenar aristas por peso
        edges = sorted(self.edges(), key=lambda x: x[2])
        mst = []
        for u, v, w in edges:
            if find(u) != find(v):
                mst.append((u, v, w))
                union(u, v)
            if len(mst) == len(self.vertices) - 1:
                break
        return mst

    def dijkstra(self, start, end):
        import heapq
        heap = [(0, start, [start])]
        visited = set()
        while heap:
            cost, u, path = heapq.heappop(heap)
            if u == end:
                return path, cost
            if u in visited:
                continue
            visited.add(u)
            for v, w in self.get_neighbors(u):
                if v not in visited:
                    heapq.heappush(heap, (cost + w, v, path + [v]))
        return None, None

    def floyd_warshall(self):
        # Devuelve distancias y predecesores para todos los pares
        nodes = list(self.vertices.keys())
        n = len(nodes)
        dist = {u: {v: float('inf') for v in nodes} for u in nodes}
        next_node = {u: {v: None for v in nodes} for u in nodes}
        for u in nodes:
            dist[u][u] = 0
        for u, v, w in self.edges():
            dist[u][v] = w
            dist[v][u] = w
            next_node[u][v] = v
            next_node[v][u] = u
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]
        return dist, next_node

    def reconstruct_fw_path(self, start, end, next_node):
        if next_node[start][end] is None:
            return None
        path = [start]
        while start != end:
            start = next_node[start][end]
            path.append(start)
        return path
