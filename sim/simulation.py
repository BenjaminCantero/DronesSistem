from tda.route_tree import RouteTree
from tda.hash_map import HashMap
from domain.order import Order
from domain.client import Client
from database import Session, Cliente, Orden
from collections import deque
import streamlit as st

class Simulation:
    def __init__(self, graph):
        # Inicializa la simulación con un grafo dado.
        # Crea estructuras para órdenes, clientes, registro de rutas y frecuencias.
        self.graph = graph
        self.orders = HashMap()
        self.clients = HashMap()
        self.route_log = RouteTree()
        self.order_id = 0
        self.origin_freq = {}
        self.dest_freq = {}
        
        # Cargar clientes existentes desde la base de datos
        session = Session()
        try:
            db_clients = session.query(Cliente).all()
            for client in db_clients:
                self.add_client(client.id, client.nombre, client.nodo_id, client.prioridad)
        except Exception as e:
            print(f"Error al cargar clientes: {e}")
        finally:
            session.close()

    def add_client(self, client_id, client_name, node_id, priority):
        """Agrega un nuevo cliente al sistema y a la base de datos"""
        # Verificar si el nodo existe
        if node_id not in self.graph.vertices:
            raise ValueError(f"El nodo {node_id} no existe en el grafo")
            
        # Crear el cliente
        client = Client(client_id, client_name, node_id, priority)
        
        # Agregar a la estructura en memoria
        self.clients.insert(client_id, client)
        
        # Agregar a la base de datos
        session = Session()
        try:
            # Verificar si ya existe
            existing = session.query(Cliente).filter_by(id=client_id).first()
            if not existing:
                db_client = Cliente(
                    id=client_id,
                    nombre=client_name,
                    nodo_id=node_id,
                    prioridad=priority
                )
                session.add(db_client)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return client

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
        """
        Calcula la mejor ruta entre origen y destino considerando:
        - Límite de batería
        - Puntos de recarga
        - Distancia total
        """
        if origin not in self.graph.vertices or destination not in self.graph.vertices:
            return None, None

        # (nodo, ruta, costo_total, batería_restante)
        queue = deque([(origin, [origin], 0, battery_limit)])
        visited = set()  # (nodo, batería_restante)
        all_routes = []

        while queue:
            current, path, total_cost, battery = queue.popleft()

            # Si llegamos al destino, guardamos la ruta
            if current == destination:
                all_routes.append((path, total_cost))
                continue

            # Explorar vecinos
            for next_node, edge_cost in self.graph.get_neighbors(current):
                if next_node in path:  # Evitar ciclos
                    continue

                # Calcular nueva batería y costo
                new_battery = battery - edge_cost
                new_total_cost = total_cost + edge_cost

                # Si no hay suficiente batería pero es un punto de recarga
                if new_battery < 0 and self.graph.vertices[next_node].role == "recharge":
                    new_battery = battery_limit  # Recargar completamente

                # Si hay suficiente batería o es un punto de recarga
                if new_battery >= 0:
                    state = (next_node, new_battery)
                    if state not in visited:
                        visited.add(state)
                        new_path = path + [next_node]
                        queue.append((next_node, new_path, new_total_cost, new_battery))

        if not all_routes:
            return None, None

        # Seleccionar la mejor ruta (la más corta)
        best_route = min(all_routes, key=lambda x: x[1])
        return best_route

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
