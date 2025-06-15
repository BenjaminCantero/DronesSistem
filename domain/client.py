class Client:
    def __init__(self, id, name, node_id, priority, total_orders=0):
        # Inicializa un cliente del sistema logístico.
        # id: identificador único del cliente.
        # name: nombre del cliente.
        # node_id: identificador del nodo donde está ubicado el cliente.
        # priority: prioridad del cliente (puede influir en la atención de órdenes).
        # total_orders: cantidad de órdenes asociadas a este cliente (por defecto 0).
        self.id = id
        self.name = name
        self.node_id = node_id
        self.priority = priority
        self.total_orders = total_orders

    def to_dict(self):
        # Devuelve un diccionario con los datos del cliente, útil para mostrar o serializar.
        return {
            "id": self.id,
            "name": self.name,
            "node_id": self.node_id,
            "priority": self.priority,
            "total_orders": self.total_orders
        }
