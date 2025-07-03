from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(String, primary_key=True)
    nombre = Column(String)
    nodo_id = Column(String)
    prioridad = Column(Integer)

class Orden(Base):
    __tablename__ = 'ordenes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    origen = Column(String)
    destino = Column(String)
    cliente_id = Column(String, ForeignKey('clientes.id'))
    cliente = relationship("Cliente")

engine = create_engine('sqlite:///drones.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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

def obtener_ordenes_db():
    session = Session()
    ordenes = session.query(Orden).all()
    session.close()
    return ordenes