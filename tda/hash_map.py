class HashMap:
    def __init__(self, capacity=100):
        # Inicializa la tabla hash con una capacidad dada (por defecto 100)
        # Cada posición es una lista para manejar colisiones (hashing con encadenamiento)
        self.capacity = capacity
        self.map = [[] for _ in range(capacity)]

    def _hash(self, key):
        # Calcula el índice hash para una clave dada
        return hash(key) % self.capacity

    def insert(self, key, value):
        # Inserta un par clave-valor en la tabla hash
        index = self._hash(key)
        for pair in self.map[index]:
            if pair[0] == key:
                pair[1] = value  # Si la clave ya existe, actualiza el valor
                return
        self.map[index].append([key, value])  # Si no existe, agrega el nuevo par

    def get(self, key):
        # Obtiene el valor asociado a una clave, o None si no existe
        index = self._hash(key)
        for pair in self.map[index]:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        # Elimina un par clave-valor por clave. Devuelve True si lo elimina, False si no existe
        index = self._hash(key)
        for i, pair in enumerate(self.map[index]):
            if pair[0] == key:
                del self.map[index][i]
                return True
        return False

    def keys(self):
        # Devuelve una lista con todas las claves almacenadas
        keys = []
        for bucket in self.map:
            keys.extend([pair[0] for pair in bucket])
        return keys

    def values(self):
        # Devuelve una lista con todos los valores almacenados
        values = []
        for bucket in self.map:
            values.extend([pair[1] for pair in bucket])
        return values

    def items(self):
        # Devuelve una lista de pares (clave, valor) almacenados
        items = []
        for bucket in self.map:
            items.extend(bucket)
        return items

    def __contains__(self, key):
        # Permite usar 'in' para verificar si una clave está en el HashMap
        return self.get(key) is not None

    def __len__(self):
        # Devuelve la cantidad total de elementos almacenados
        return sum(len(bucket) for bucket in self.map)
