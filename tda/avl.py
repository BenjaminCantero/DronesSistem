class AVLNode:
    def __init__(self, key, frequency=1):
        # Nodo del árbol AVL. Almacena la clave (key), frecuencia de inserción,
        # referencias a hijos izquierdo y derecho, y la altura del nodo.
        self.key = key
        self.frequency = frequency
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        # Inicializa el árbol AVL con la raíz vacía.
        self.root = None

    def insert(self, key):
        # Inserta una clave en el árbol AVL.
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        # Inserta recursivamente una clave en el árbol.
        if not node:
            return AVLNode(key)
        elif key == node.key:
            node.frequency += 1  # Si la clave ya existe, incrementa la frecuencia.
            return node
        elif key < node.key:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)

        # Actualiza la altura del nodo.
        node.height = 1 + max(self._get_height(node.left),
                              self._get_height(node.right))
        # Balancea el árbol si es necesario.
        return self._balance(node)

    def _get_height(self, node):
        # Devuelve la altura de un nodo (0 si es None).
        return node.height if node else 0

    def _get_balance(self, node):
        # Calcula el factor de balanceo de un nodo.
        return (self._get_height(node.left) -
                self._get_height(node.right)) if node else 0

    def _balance(self, node):
        # Realiza rotaciones para mantener el balance del árbol.
        balance = self._get_balance(node)

        # Caso: subárbol izquierdo pesado
        if balance > 1:
            if self._get_balance(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Caso: subárbol derecho pesado
        if balance < -1:
            if self._get_balance(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, z):
        # Rotación simple a la izquierda
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        # Actualiza alturas
        z.height = 1 + max(self._get_height(z.left),
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left),
                           self._get_height(y.right))

        return y

    def _rotate_right(self, z):
        # Rotación simple a la derecha
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        # Actualiza alturas
        z.height = 1 + max(self._get_height(z.left),
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left),
                           self._get_height(y.right))

        return y

    def inorder(self):
        # Devuelve una lista de tuplas (clave, frecuencia) en orden ascendente.
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        # Recorrido inorder recursivo.
        if node:
            self._inorder(node.left, result)
            result.append((node.key, node.frequency))
            self._inorder(node.right, result)

    def search(self, key):
        # Busca la frecuencia de una clave en el árbol.
        return self._search(self.root, key)

    def _search(self, node, key):
        # Búsqueda recursiva de una clave.
        if not node:
            return None
        if key == node.key:
            return node.frequency
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)
