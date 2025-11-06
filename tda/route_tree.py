from tda.avl import AVLTree, AVLNode

class RouteTree(AVLTree):
    def __init__(self):
        super().__init__()
        
    def get_most_frequent_routes(self, n=5):
        """Obtiene las n rutas más frecuentes"""
        routes = []
        self._inorder_frequency(self.root, routes)
        return sorted(routes, key=lambda x: x[1], reverse=True)[:n]
    
    def _inorder_frequency(self, node, routes):
        """Recorre el árbol en orden para obtener las rutas y sus frecuencias"""
        if node:
            self._inorder_frequency(node.left, routes)
            routes.append((node.key, node.frequency))
            self._inorder_frequency(node.right, routes)
            
    def get_route_frequency(self, route_key):
        """Obtiene la frecuencia de una ruta específica"""
        node = self._find(self.root, route_key)
        return node.frequency if node else 0
        
    def _find(self, node, key):
        """Busca un nodo por su clave"""
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._find(node.left, key)
        return self._find(node.right, key)