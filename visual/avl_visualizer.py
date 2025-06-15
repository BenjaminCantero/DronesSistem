import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    """
    Clase para visualizar un árbol AVL usando NetworkX y Matplotlib.
    Permite mostrar gráficamente la estructura del árbol y la frecuencia de cada ruta.
    """
    def __init__(self, avl_tree):
        # Guarda una referencia al árbol AVL que se va a visualizar
        self.tree = avl_tree

    def draw(self):
        """
        Dibuja el árbol AVL como un grafo dirigido.
        Cada nodo muestra su clave y frecuencia.
        """
        G = nx.DiGraph()  # Grafo dirigido para representar el árbol
        self._add_edges(self.tree.root, G)  # Agrega nodos y aristas recursivamente
        pos = nx.spring_layout(G)  # Calcula posiciones para los nodos
        labels = nx.get_node_attributes(G, 'label')  # Obtiene las etiquetas de los nodos

        fig, ax = plt.subplots()
        nx.draw(
            G, pos, with_labels=True, labels=labels,
            node_size=1200, node_color="lightblue", ax=ax
        )
        return fig  # Devuelve la figura para mostrarla en Streamlit

    def _add_edges(self, node, G):
        """
        Método recursivo para agregar nodos y aristas al grafo NetworkX.
        Cada nodo muestra su clave y frecuencia.
        """
        if not node:
            return
        G.add_node(node.key, label=f"{node.key}\nFreq: {node.frequency}")
        if node.left:
            G.add_edge(node.key, node.left.key)
            self._add_edges(node.left, G)
        if node.right:
            G.add_edge(node.key, node.right.key)
            self._add_edges(node.right, G)
