import folium
from streamlit_folium import st_folium

# Visualizador de grafo sobre mapa real usando folium
def draw_graph_on_map(graph, path=None, mst_edges=None, center_lat=-38.7359, center_lon=-72.5904, zoom_start=13):
    """
    Dibuja el grafo sobre un mapa real de Temuco (por defecto) usando folium.
    path: lista de nodos (ids) que representan la ruta a resaltar (opcional)
    mst_edges: lista de aristas (u, v, peso) del MST a resaltar (opcional)
    """
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    color_map = {'storage': 'blue', 'recharge': 'green', 'client': 'orange'}
    for node_id, vertex in graph.vertices.items():
        lat = getattr(vertex, 'lat', None)
        lon = getattr(vertex, 'lon', None)
        role = getattr(vertex, 'role', 'client')
        if lat is not None and lon is not None:
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color=color_map.get(role, 'gray'),
                fill=True,
                fill_color=color_map.get(role, 'gray'),
                popup=f"{node_id} ({role})"
            ).add_to(m)
    # Dibujar aristas normales
    for u, v, data in graph.edges():
        u_lat = getattr(graph.vertices[u], 'lat', None)
        u_lon = getattr(graph.vertices[u], 'lon', None)
        v_lat = getattr(graph.vertices[v], 'lat', None)
        v_lon = getattr(graph.vertices[v], 'lon', None)
        if None not in (u_lat, u_lon, v_lat, v_lon):
            folium.PolyLine(
                locations=[(u_lat, u_lon), (v_lat, v_lon)],
                color='gray',
                weight=2,
                opacity=0.7
            ).add_to(m)
    # Dibujar MST si se proporciona
    if mst_edges:
        for u, v, w in mst_edges:
            u_lat = getattr(graph.vertices[u], 'lat', None)
            u_lon = getattr(graph.vertices[u], 'lon', None)
            v_lat = getattr(graph.vertices[v], 'lat', None)
            v_lon = getattr(graph.vertices[v], 'lon', None)
            if None not in (u_lat, u_lon, v_lat, v_lon):
                folium.PolyLine(
                    locations=[(u_lat, u_lon), (v_lat, v_lon)],
                    color='purple',
                    weight=4,
                    opacity=0.8,
                    dash_array='10,10'
                ).add_to(m)
    # Dibujar ruta resaltada si se proporciona
    if path and len(path) > 1:
        route_coords = []
        for node_id in path:
            vertex = graph.vertices.get(node_id)
            if vertex and vertex.lat is not None and vertex.lon is not None:
                route_coords.append((vertex.lat, vertex.lon))
        if len(route_coords) > 1:
            folium.PolyLine(
                locations=route_coords,
                color='red',
                weight=5,
                opacity=0.9
            ).add_to(m)
    return m

def show_graph_map(graph, path=None, mst_edges=None):
    m = draw_graph_on_map(graph, path=path, mst_edges=mst_edges)
    st_folium(m, width=700, height=500)
