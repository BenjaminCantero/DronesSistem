class Route:
    def __init__(self, path, cost):
        # Inicializa una ruta.
        # path: lista de nodos que conforman la ruta.
        # cost: costo total de recorrer la ruta.
        self.path = path
        self.cost = cost

    def to_string(self):
        # Devuelve una representación en texto de la ruta y su costo.
        return f"{' → '.join(self.path)} | Cost: {self.cost}"

    def __str__(self):
        # Permite imprimir el objeto Route directamente como texto.
        return self.to_string()
