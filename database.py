from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    nodo_id = Column(String, nullable=False)
    prioridad = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "nodo_id": self.nodo_id,
            "prioridad": self.prioridad
        }

class Orden(Base):
    __tablename__ = 'ordenes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    cliente_id = Column(String, ForeignKey('clientes.id'), nullable=False)
    fecha_creacion = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cliente = relationship("Cliente", backref="ordenes")

    def to_dict(self):
        return {
            "id": self.id,
            "origen": self.origen,
            "destino": self.destino,
            "cliente_id": self.cliente_id,
            "fecha_creacion": self.fecha_creacion,
            "cliente_nombre": self.cliente.nombre if self.cliente else None
        }

# Configuración de la base de datos
engine = create_engine('sqlite:///drones.db', echo=True)
Session = sessionmaker(bind=engine)

def init_db():
    """Inicializa la base de datos creando todas las tablas necesarias"""
    Base.metadata.create_all(engine)

# Crear las tablas al importar el módulo
init_db()

def agregar_cliente_db(client_id, client_name, node_id, priority):
    """Agrega un nuevo cliente a la base de datos"""
    session = Session()
    try:
        if session.query(Cliente).filter_by(id=client_id).first():
            return False
        nuevo_cliente = Cliente(
            id=client_id,
            nombre=client_name,
            nodo_id=node_id,
            prioridad=priority
        )
        session.add(nuevo_cliente)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def obtener_clientes_db():
    """Obtiene todos los clientes de la base de datos"""
    session = Session()
    try:
        clientes = session.query(Cliente).all()
        return [cliente.to_dict() for cliente in clientes]
    finally:
        session.close()

def agregar_orden_db(origen, destino, cliente_id):
    """Agrega una nueva orden a la base de datos"""
    session = Session()
    try:
        # Verificar que el cliente existe
        cliente = session.query(Cliente).filter_by(id=cliente_id).first()
        if not cliente:
            raise ValueError(f"El cliente con ID {cliente_id} no existe")

        nueva_orden = Orden(
            origen=origen,
            destino=destino,
            cliente_id=cliente_id
        )
        session.add(nueva_orden)
        session.commit()
        return nueva_orden.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def obtener_ordenes_db():
    """Obtiene todas las órdenes de la base de datos"""
    session = Session()
    try:
        ordenes = session.query(Orden).all()
        return [orden.to_dict() for orden in ordenes]
    finally:
        session.close()