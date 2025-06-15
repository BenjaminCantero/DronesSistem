from tda.avl import AVLTree
from tda.hash_map import HashMap
from domain.order import Order
from collections import deque
import streamlit as st

class Simulation:
    def __init__(self, graph):
        # Inicializa la simulación con un grafo dado.
        # Crea estructuras para órdenes, clientes, registro de rutas y frecuencias.
        self.graph = graph
        self.orders = HashMap()
        self.clients = HashMap()
        self.route_log = AVLTree()
        self.order_id = 0
        self.origin_freq = {}
        self.dest_freq = {}

    def add_client(self, client):
        # Agrega un cliente al HashMap de clientes.
        self.clients.insert(client.id, client)

    def create_order(self, origin, destination):
        # Crea una orden entre dos nodos si ambos existen y hay ruta posible.
        if origin not in self.graph.vertices or destination not in self.graph.vertices:
            st.error(f"No se pudo crear la orden: el nodo '{origin}' o '{destination}' no existe.")
            return None
        path, cost = self.calculate_route(origin, destination)
        if path:
            self._register_order(origin, destination, path, cost)
            return self.orders.get(self.order_id - 1)
        st.error(f"No se pudo crear la orden: no existe ruta de {origin} a {destination}")
        return None

    def _register_order(self, origin, destination, path, cost):
        # Registra una orden, la almacena y actualiza frecuencias y el árbol AVL de rutas.
        st.success(f"ORDEN CREADA: {origin} → {destination} | Ruta: {' → '.join(path)} | Costo: {cost}")
        order = Order(self.order_id, origin, destination, path, cost)
        self.orders.insert(self.order_id, order)
        self.order_id += 1
        route_key = " → ".join(path)
        self.route_log.insert(route_key)
        self.origin_freq[origin] = self.origin_freq.get(origin, 0) + 1
        self.dest_freq[destination] = self.dest_freq.get(destination, 0) + 1

    def calculate_route(self, origin, destination, battery_limit=50):
        # Calcula todas las rutas posibles entre origen y destino considerando la autonomía.
        all_routes = []
        queue = deque([(origin, [origin], 0)])
        while queue:
            current, path, cost = queue.popleft()
            if current == destination and cost <= battery_limit:
                all_routes.append((path, cost))
                continue
            for neighbor, weight in self.graph.get_neighbors(current):
                if neighbor not in path:
                    new_cost = cost + weight
                    if new_cost > battery_limit:
                        if self.graph.vertices[neighbor].role != "recharge":
                            continue
                        new_cost = 0  # recarga la batería al llegar a un nodo de recarga
                    queue.append((neighbor, path + [neighbor], new_cost))
        if not all_routes:
            return None, None
        best_path, best_cost = self._select_best_route(all_routes)
        return best_path, best_cost

    def _select_best_route(self, all_routes):
        # Selecciona la mejor ruta: primero la más frecuente, luego la de menor costo.
        def route_frequency(route):
            key = " → ".join(route)
            node = self.route_log.root
            while node:
                if key == node.key:
                    return node.frequency
                elif key < node.key:
                    node = node.left
                else:
                    node = node.right
            return 0
        all_routes.sort(key=lambda x: (-route_frequency(x[0]), x[1]))
        return all_routes[0]

    def get_order(self, order_id):
        # Devuelve una orden por su ID.
        return self.orders.get(order_id)

    def get_orders(self):
        # Devuelve todas las órdenes registradas.
        return self.orders.items()

    def get_clients(self):
        # Devuelve todos los clientes registrados.
        return self.clients.items()

    def get_route_frequencies(self):
        # Devuelve la frecuencia de todas las rutas registradas (inorder del AVL).
        return self.route_log.inorder()
