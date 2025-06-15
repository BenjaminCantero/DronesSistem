import datetime

class Order:
    def __init__(self, order_id, origin, destination, path, cost, priority=1):
        # Inicializa una orden de entrega.
        # order_id: identificador único de la orden.
        # origin: nodo de origen.
        # destination: nodo de destino.
        # path: lista de nodos que conforman la ruta.
        # cost: costo total de la ruta.
        # priority: prioridad de la orden (por defecto 1).
        self.id = order_id
        self.origin = origin
        self.destination = destination
        self.path = path
        self.cost = cost
        self.priority = priority
        self.status = "In Progress"  # Estado inicial de la orden.
        self.creation_date = datetime.datetime.now()  # Fecha de creación.
        self.delivery_date = None  # Fecha de entrega (se asigna al completar la orden).

    def complete_order(self):
        # Marca la orden como entregada y registra la fecha de entrega.
        self.status = "Delivered"
        self.delivery_date = datetime.datetime.now()

    def to_dict(self):
        # Devuelve un diccionario con los datos de la orden, útil para mostrar o serializar.
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "path": " → ".join(self.path),
            "cost": self.cost,
            "priority": self.priority,
            "status": self.status,
            "creation_date": str(self.creation_date),
            "delivery_date": str(self.delivery_date) if self.delivery_date else None
        }
