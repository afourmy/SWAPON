from collections import OrderedDict
from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import backref, relationship

class Object(Base):
    
    # __abstract__ = True
    __tablename__ = 'Object'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

class Node(Object):
    
    __tablename__ = 'Node'
    
    properties = (
        'name',
        'longitude', 
        'latitude'
        )
    
    id = Column(Integer, ForeignKey('Object.id'), primary_key=True)
    longitude = Column(Float)
    latitude = Column(Float)
    
    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)

    def adjacencies(self):
        all_nodes = [x.source for x in self.higher_edges]
        all_nodes.extend([x.destination for x in self.lower_edges])
        return all_nodes
        

class Link(Object):
    
    __tablename__ = 'Link'
    
    properties = (
        'name',
        'source', 
        'destination'
        )

    id = Column(Integer, ForeignKey('Object.id'), primary_key=True)
    
    source_id = Column(
        Integer,
        ForeignKey('Node.id')
        )

    destination_id = Column(
        Integer,
        ForeignKey('Node.id')
        )
        
    source = relationship(
        Node,
        primaryjoin = source_id == Node.id,
        backref = backref('lower_edges', cascade="all, delete-orphan")
        )

    destination = relationship(
        Node,
        primaryjoin = destination_id == Node.id,
        backref = backref('higher_edges', cascade="all, delete-orphan")
        )
        
    properties = OrderedDict([
        ('source', 'Source'),
        ('destination', 'Destination')
        ])

        
    def __init__(self, **kwargs):
        super(Link, self).__init__(**kwargs)

class Fiber(Link):
    
    __tablename__ = 'Fiber'
    
    id = Column(Integer, ForeignKey('Link.id'), primary_key=True)
    color = '#ff8247'
    
    def __init__(self, **kwargs):
        super(Fiber, self).__init__(**kwargs)

class Traffic(Link):
    
    __tablename__ = 'Traffic'
    
    id = Column(Integer, ForeignKey('Link.id'), primary_key=True)
    color = '#902bec'
    
    def __init__(self, **kwargs):
        super(Fiber, self).__init__(**kwargs)

object_class = OrderedDict([
    ('Node', Node),
    ('Fiber', Fiber),
    ('Traffic', Traffic)
    ])

def get_obj(db, model, **kwargs):
    return db.session.query(model).filter_by(**kwargs).first()

def object_factory(db, **kwargs):
    obj_type = kwargs['type']
    if obj_type == 'Node':
        obj = object_class[obj_type](**kwargs)
    else:
        source = get_obj(db, Node, name=kwargs.pop('source'))
        destination = get_obj(db, Node, name=kwargs.pop('destination'))
        obj = object_class[obj_type](
            source_id = source.id, 
            destination_id = destination.id, 
            source = source, 
            destination = destination,
            **kwargs
            )
    db.session.add(obj)
    db.session.commit()