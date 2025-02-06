from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .connection import Base
import datetime

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    interactions = relationship("Interaction", back_populates="customer")
    documents = relationship("Document", back_populates="customer")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    title = Column(String(200))
    content = Column(Text)
    doc_metadata = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="documents")

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="interactions") 