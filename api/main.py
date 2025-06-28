from fastapi import FastAPI, HTTPException
from sim.simulation import Simulation
from sim.init_simulation import SimulationInitializer
from reports.report_generator import ReportGenerator
from fastapi.responses import FileResponse
import os

app = FastAPI(title="API Sistema Drones")

# Instancia global de simulación (para demo, en producción usar base de datos o inyección de dependencias)
sim = None

def get_sim():
    global sim
    if sim is None:
        initializer = SimulationInitializer(15, 20)
        graph = initializer.generate_connected_graph()
        sim = Simulation(graph)
    return sim

@app.get("/clients/")
def get_clients():
    sim = get_sim()
    return [client[1].to_dict() for client in sim.get_clients()]

@app.get("/clients/{client_id}")
def get_client(client_id: str):
    sim = get_sim()
    client = sim.clients.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client.to_dict()

@app.get("/orders/")
def get_orders():
    sim = get_sim()
    return [order[1].to_dict() for order in sim.get_orders()]

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    sim = get_sim()
    order = sim.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order.to_dict()

@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    sim = get_sim()
    order = sim.get_order(order_id)
    if not order or order.status == "Delivered":
        raise HTTPException(status_code=400, detail="No se puede cancelar la orden")
    order.status = "Cancelled"
    return {"message": "Orden cancelada"}

@app.post("/orders/{order_id}/complete")
def complete_order(order_id: int):
    sim = get_sim()
    order = sim.get_order(order_id)
    if not order or order.status == "Delivered":
        raise HTTPException(status_code=400, detail="No se puede completar la orden")
    order.complete_order()
    return {"message": "Orden completada"}

@app.get("/routes/")
def get_routes():
    sim = get_sim()
    return [{"route": route, "frequency": freq} for route, freq in sim.get_route_frequencies()]

@app.get("/stats/")
def get_stats():
    sim = get_sim()
    roles = [v.role for v in sim.graph.vertices.values()]
    return {
        "nodos": len(sim.graph.vertices),
        "aristas": sim.graph.edge_count(),
        "almacenamiento": roles.count('storage'),
        "recarga": roles.count('recharge'),
        "cliente": roles.count('client')
    }

@app.get("/report/pdf")
def get_report_pdf():
    sim = get_sim()
    filename = "informe_drones_api.pdf"
    ReportGenerator(sim).generate_pdf(filename)
    return FileResponse(filename, media_type="application/pdf", filename=filename)

@app.get("/info/reports/visits/clients")
def get_visits_clients():
    sim = get_sim()
    clients = list(sim.get_clients())
    # Ranking por total_orders descendente
    sorted_clients = sorted(clients, key=lambda x: x[1].total_orders, reverse=True)
    return [{"id": c.id, "name": c.name, "total_orders": c.total_orders} for _, c in sorted_clients]

@app.get("/info/reports/visits/recharges")
def get_visits_recharges():
    sim = get_sim()
    roles_dict = {k: v.role for k, v in sim.graph.vertices.items()}
    origin_freq = sim.origin_freq
    dest_freq = sim.dest_freq
    total_freq = {node: origin_freq.get(node, 0) + dest_freq.get(node, 0) for node in sim.graph.vertices.keys()}
    recharges = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'recharge']
    recharges_sorted = sorted(recharges, key=lambda x: x[1], reverse=True)
    return [{"node": n, "visits": f} for n, f in recharges_sorted]

@app.get("/info/reports/visits/storages")
def get_visits_storages():
    sim = get_sim()
    roles_dict = {k: v.role for k, v in sim.graph.vertices.items()}
    origin_freq = sim.origin_freq
    dest_freq = sim.dest_freq
    total_freq = {node: origin_freq.get(node, 0) + dest_freq.get(node, 0) for node in sim.graph.vertices.keys()}
    storages = [(node, freq) for node, freq in total_freq.items() if roles_dict[node] == 'storage']
    storages_sorted = sorted(storages, key=lambda x: x[1], reverse=True)
    return [{"node": n, "visits": f} for n, f in storages_sorted]

@app.get("/info/reports/summary")
def get_summary():
    sim = get_sim()
    roles = [v.role for v in sim.graph.vertices.values()]
    summary = {
        "nodos": len(sim.graph.vertices),
        "aristas": sim.graph.edge_count(),
        "almacenamiento": roles.count('storage'),
        "recarga": roles.count('recharge'),
        "cliente": roles.count('client'),
        "total_ordenes": len(list(sim.get_orders())),
        "clientes": len(list(sim.get_clients())),
        "rutas_registradas": len(sim.get_route_frequencies()),
    }
    return summary
