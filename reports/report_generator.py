from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os

class ReportGenerator:
    def __init__(self, sim):
        self.sim = sim

    def generate_pdf(self, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, "Informe del Sistema de Drones", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        # Tabla de pedidos
        pdf.cell(0, 8, "Tabla de Pedidos", ln=True)
        orders = list(self.sim.get_orders())
        pdf.set_font("Arial", size=8)
        pdf.cell(0, 6, "ID | Origen | Destino | Costo | Estado", ln=True)
        for _, order in orders:
            o = order.to_dict()
            pdf.cell(0, 6, f"{o['id']} | {o['origin']} | {o['destination']} | {o['cost']} | {o['status']}", ln=True)
        pdf.ln(4)
        # Clientes con más pedidos
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, "Clientes con más pedidos", ln=True)
        clients = list(self.sim.get_clients())
        sorted_clients = sorted(clients, key=lambda x: x[1].total_orders, reverse=True)
        for _, client in sorted_clients[:5]:
            pdf.cell(0, 6, f"{client.name} (ID: {client.id}) - Pedidos: {client.total_orders}", ln=True)
        pdf.ln(4)
        # Rutas más usadas
        pdf.cell(0, 8, "Rutas más usadas", ln=True)
        for route, freq in self.sim.get_route_frequencies()[:5]:
            pdf.cell(0, 6, f"{route} - {freq} veces", ln=True)
        pdf.ln(4)
        # Gráficos
        with tempfile.TemporaryDirectory() as tmpdir:
            # Gráfico de torta de roles
            roles = [v.role for v in self.sim.graph.vertices.values()]
            labels = ['Almacenamiento', 'Recarga', 'Cliente']
            sizes = [roles.count('storage'), roles.count('recharge'), roles.count('client')]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            pie_path = os.path.join(tmpdir, 'roles_pie.png')
            fig.savefig(pie_path)
            plt.close(fig)
            pdf.image(pie_path, w=80)
            pdf.ln(4)
            # Gráfico de barras de nodos más visitados
            origin_freq = self.sim.origin_freq
            dest_freq = self.sim.dest_freq
            total_freq = {node: origin_freq.get(node, 0) + dest_freq.get(node, 0) for node in self.sim.graph.vertices.keys()}
            top_nodos = sorted(total_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            bar_labels = [str(n) for n, _ in top_nodos]
            bar_values = [f for _, f in top_nodos]
            fig2, ax2 = plt.subplots()
            ax2.bar(bar_labels, bar_values)
            ax2.set_ylabel("Frecuencia de visitas")
            ax2.set_xlabel("Nodo")
            ax2.set_title("Nodos más visitados")
            bar_path = os.path.join(tmpdir, 'bar.png')
            fig2.savefig(bar_path)
            plt.close(fig2)
            pdf.image(bar_path, w=100)
        pdf.output(filename)
