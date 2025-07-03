import streamlit as st
from sim.init_simulation import SimulationInitializer
from sim.simulation import Simulation
from visual.networkx_adapter import NetworkXAdapter
from visual.avl_visualizer import AVLVisualizer
from visual.map_visualizer import show_graph_map
from domain.client import Client
import matplotlib.pyplot as plt
import pandas as pd
from reports.report_generator import ReportGenerator
from database import Session, Cliente, Orden, obtener_ordenes_db

# Configuración de la página de Streamlit
st.set_page_config(page_title="Sistema Logístico Autónomo con Drones", layout="wide")

# Inicialización de variables en la sesión de Streamlit
if 'sim' not in st.session_state:
    st.session_state.sim = None
if 'graph_adapter' not in st.session_state:
    st.session_state.graph_adapter = None
if 'order_success' not in st.session_state:
    st.session_state.order_success = False

# Función auxiliar para obtener los nodos más visitados por tipo
def get_top_nodos_por_tipo(total_freq, roles_dict, n=5):
    tipos = ['storage', 'recharge', 'client']
    resultado = {}
    for tipo in tipos:
        nodos = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == tipo]
        resultado[tipo] = sorted(nodos, key=lambda x: x[1], reverse=True)[:n]
    return resultado

def run():
    st.title("🚁 Sistema Logístico Autónomo con Drones")

    # Definición de pestañas principales de la app
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔄 Ejecutar Simulación",
        "🌍 Explorar Red",
        "👥 Clientes y Órdenes",
        "📋 Analítica de Rutas",
        "📈 Estadísticas Generales"
    ])

    # ----------- Pestaña 1: Ejecutar Simulación -----------
    with tab1:
        st.header("🔄 Ejecutar Simulación")
        st.markdown("Configura los parámetros iniciales para la simulación de la red logística de drones.")
        col1, col2, col3 = st.columns(3)
        with col1:
            n_nodes = st.slider("Número de nodos", 10, 150, 15)
        with col2:
            m_edges = st.slider("Número de aristas", n_nodes - 1, 300, max(n_nodes - 1, 20))
        with col3:
            n_orders = st.slider("Número de órdenes", 10, 300, 10)

        # Botón para iniciar la simulación
        if st.button("🚀 Iniciar Simulación"):
            if m_edges < n_nodes - 1:
                st.error("El número de aristas debe ser al menos n-1 para que el grafo sea conexo.")
            else:
                initializer = SimulationInitializer(n_nodes, m_edges)
                graph = initializer.generate_connected_graph()
                st.session_state.sim = Simulation(graph)
                st.session_state.graph_adapter = NetworkXAdapter(graph)
                st.success("¡Simulación iniciada correctamente!")

        # Mostrar información y visualización del grafo si ya existe una simulación
        if st.session_state.sim:
            st.markdown(f"**Nodos:** {len(st.session_state.sim.graph.vertices)}  \n**Aristas:** {st.session_state.sim.graph.edge_count()}")
            fig = st.session_state.graph_adapter.draw_graph()
            fig.set_size_inches(4, 3)  # Tamaño pequeño de la imagen
            st.pyplot(fig)

    # ----------- Pestaña 2: Explorar Red -----------
    with tab2:
        st.header("🌍 Explorar Red")
        if st.session_state.sim:
            # Visualización sobre mapa real
            st.subheader("Visualización georreferenciada (Mapa real)")
            show_graph_map(
                st.session_state.sim.graph,
                path=st.session_state.get("calculated_path"),
                mst_edges=st.session_state.get("mst_edges")
            )

            # Leyenda de colores para los tipos de nodos
            st.markdown("""
            **Leyenda de colores:**
            <span style='color:#1f77b4'>●</span> Almacenamiento &nbsp;&nbsp;
            <span style='color:#2ca02c'>●</span> Recarga &nbsp;&nbsp;
            <span style='color:#ff7f0e'>●</span> Cliente &nbsp;&nbsp;
            <span style='color:purple'>━━</span> MST
            """, unsafe_allow_html=True)

            st.markdown("### Buscar Ruta entre Nodos")
            origin = st.text_input("Nodo de origen", key="origin_input")
            destination = st.text_input("Nodo de destino", key="destination_input")

            # Selección de algoritmo
            algorithm = st.radio("Algoritmo de ruta", ["Autonomía (actual)", "Dijkstra", "Floyd-Warshall"], index=0)

            # Botón para calcular ruta entre nodos
            if st.button("✈ Calcular Ruta"):
                if not origin or not destination:
                    st.error("Por favor, ingresa tanto el nodo de origen como el de destino.")
                    st.session_state.calculated_path = None
                    st.session_state.calculated_cost = None
                    st.session_state.calculated_origin = None
                    st.session_state.calculated_destination = None
                else:
                    if algorithm == "Dijkstra":
                        path, cost = st.session_state.sim.graph.dijkstra(origin, destination)
                    elif algorithm == "Floyd-Warshall":
                        dist, next_node = st.session_state.sim.graph.floyd_warshall()
                        path = st.session_state.sim.graph.reconstruct_fw_path(origin, destination, next_node)
                        cost = dist[origin][destination] if path else None
                    else:
                        path, cost = st.session_state.sim.calculate_route(origin, destination)
                    if path:
                        st.session_state.calculated_path = path
                        st.session_state.calculated_cost = cost
                        st.session_state.calculated_origin = origin
                        st.session_state.calculated_destination = destination
                    else:
                        st.session_state.calculated_path = None
                        st.session_state.calculated_cost = None
                        st.session_state.calculated_origin = None
                        st.session_state.calculated_destination = None

            # Botón para mostrar el MST
            if st.button("🌲 Mostrar MST (Kruskal)"):
                st.session_state["mst_edges"] = st.session_state.sim.graph.kruskal_mst()
            if st.button("❌ Ocultar MST"):
                st.session_state["mst_edges"] = None

            # Mostrar ruta encontrada y permitir registrar orden solo si hay cliente en el destino
            if st.session_state.get("calculated_path"):
                st.success(f"**Ruta encontrada:** {' → '.join(st.session_state.calculated_path)} | **Costo:** {st.session_state.calculated_cost}")
                if st.button("✅ Completar Entrega y Registrar Orden"):
                    destino = st.session_state.calculated_destination
                    clientes_en_destino = [
                        client for _, client in st.session_state.sim.get_clients()
                        if client.node_id == destino
                    ]
                    if not clientes_en_destino:
                        st.error("No se puede crear la orden: no hay ningún cliente registrado en el nodo de destino.")
                    else:
                        st.session_state.sim.create_order(
                            st.session_state.calculated_origin,
                            st.session_state.calculated_destination
                        )
                        st.session_state.order_success = True
            elif "calculated_path" in st.session_state and st.session_state.calculated_path is None:
                st.error("No hay ruta disponible con la autonomía actual.")

    # ----------- Pestaña 3: Clientes y Órdenes -----------
    with tab3:
        st.header("👥 Clientes y Órdenes")
        if st.session_state.sim:
            if st.session_state.order_success:
                st.success("Orden generada y ruta registrada exitosamente.")
                st.session_state.order_success = False

            st.markdown("### Agregar Cliente")
            with st.form("add_client_form"):
                # Generar ID sugerido para el nuevo cliente
                try:
                    next_id = str(len(list(st.session_state.sim.get_clients())) + 1)
                except Exception:
                    next_id = "1"
                client_id = st.text_input("ID del cliente", value=next_id)
                client_name = st.text_input("Nombre del cliente", value=f"Cliente {client_id}")
                available_nodes = list(st.session_state.sim.graph.vertices.keys())
                node_id = st.selectbox("Nodo donde se ubicará el cliente", available_nodes)
                priority = st.selectbox("Prioridad", [1, 2, 3, 4, 5], index=0)
                submit = st.form_submit_button("Agregar cliente")

                if submit:
                    # Validación de ID único
                    if any(client[1].id == client_id for client in st.session_state.sim.get_clients()):
                        st.error("Ya existe un cliente con ese ID.")
                    else:
                        client = Client(client_id, client_name, node_id, priority)
                        st.session_state.sim.add_client(client)
                        # Guardar cliente en la base de datos
                        if agregar_cliente_db(client_id, client_name, node_id, priority):
                            st.success(f"Cliente {client.name} agregado en nodo {node_id} con prioridad {priority}")
                        else:
                            st.error("Error al agregar el cliente en la base de datos.")

            # Mostrar clientes y órdenes registrados
            st.subheader("Clientes registrados")
            clientes_registrados = st.session_state.sim.get_clients()
            st.json([client[1].to_dict() for client in clientes_registrados])

            # Cargar y mostrar órdenes desde la base de datos
            st.subheader("Órdenes registradas")
            ordenes_registradas = obtener_ordenes_db()
            st.json([orden.to_dict() for orden in ordenes_registradas])

    # ----------- Pestaña 4: Analítica de Rutas -----------
    with tab4:
        st.header("📋 Analítica de Rutas")
        if st.session_state.sim:
            frequencies = st.session_state.sim.get_route_frequencies()
            st.write("Rutas más frecuentes:")

            if frequencies:
                sorted_freq = sorted(frequencies, key=lambda x: x[1], reverse=True)
                for route, freq in sorted_freq:
                    st.write(f"{route} → {freq} veces")

                ruta_mas_frecuente = sorted_freq[0]
                st.info(f"Ruta más frecuente: {ruta_mas_frecuente[0]} ({ruta_mas_frecuente[1]} veces)")
            else:
                st.write("No hay rutas registradas aún.")

            # Visualización del árbol AVL de rutas
            if st.button("🌳 Visualizar Árbol AVL de Rutas"):
                visualizer = AVLVisualizer(st.session_state.sim.route_log)
                fig = visualizer.draw()
                st.pyplot(fig)

            # Botón para generar informe PDF
            if st.button("📄 Generar Informe PDF"):
                report = ReportGenerator(st.session_state.sim)
                filename = "informe_drones.pdf"
                report.generate_pdf(filename)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Descargar Informe PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )

    # ----------- Pestaña 5: Estadísticas Generales -----------
    with tab5:
        st.header("📈 Estadísticas Generales")
        if st.session_state.sim:
            roles = [v.role for v in st.session_state.sim.graph.vertices.values()]
            st.write(f"Almacenamiento: {roles.count('storage')}, Recarga: {roles.count('recharge')}, Cliente: {roles.count('client')}")

            labels = ['Almacenamiento', 'Recarga', 'Cliente']
            sizes = [roles.count('storage'), roles.count('recharge'), roles.count('client')]

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig)

            st.subheader("Frecuencia de nodos de origen")
            st.json(st.session_state.sim.origin_freq)
            st.subheader("Frecuencia de nodos de destino")
            st.json(st.session_state.sim.dest_freq)

            roles_dict = {k: v.role for k, v in st.session_state.sim.graph.vertices.items()}
            total_freq = {node: st.session_state.sim.origin_freq.get(node, 0) + st.session_state.sim.dest_freq.get(node, 0)
                          for node in st.session_state.sim.graph.vertices.keys()}

            top_nodos = get_top_nodos_por_tipo(total_freq, roles_dict)
            top_storage = top_nodos['storage']
            top_recharge = top_nodos['recharge']
            top_client = top_nodos['client']

            bar_labels = (
                [f"Almacenamiento {n}" for n, _ in top_storage] +
                [f"Recarga {n}" for n, _ in top_recharge] +
                [f"Cliente {n}" for n, _ in top_client]
            )
            bar_values = (
                [f for _, f in top_storage] +
                [f for _, f in top_recharge] +
                [f for _, f in top_client]
            )
            color_map = (
                ['#1f77b4'] * len(top_storage) +
                ['#2ca02c'] * len(top_recharge) +
                ['#ff7f0e'] * len(top_client)
            )

            if bar_labels:
                st.subheader("Nodos más visitados por tipo")
                fig2, ax2 = plt.subplots()
                ax2.bar(range(len(bar_labels)), bar_values, color=color_map[:len(bar_labels)])
                ax2.set_ylabel("Frecuencia de visitas (origen + destino)")
                ax2.set_xticks(range(len(bar_labels)))
                ax2.set_xticklabels(bar_labels, rotation=45, ha='right')
                st.pyplot(fig2)
            else:
                st.info("Aún no hay visitas registradas en los nodos.")

def agregar_cliente_db(client_id, client_name, node_id, priority):
    session = Session()
    if session.query(Cliente).filter_by(id=client_id).first():
        session.close()
        return False
    nuevo_cliente = Cliente(id=client_id, nombre=client_name, nodo_id=node_id, prioridad=priority)
    session.add(nuevo_cliente)
    session.commit()
    session.close()
    return True

def obtener_clientes_db():
    session = Session()
    clientes = session.query(Cliente).all()
    session.close()
    return clientes

def agregar_orden_db(origen, destino, cliente_id):
    session = Session()
    nueva_orden = Orden(origen=origen, destino=destino, cliente_id=cliente_id)
    session.add(nueva_orden)
    session.commit()
    session.close()

if __name__ == "__main__":
    run()