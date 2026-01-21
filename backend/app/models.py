"""
Modelli ORM SQLAlchemy per il database FinConnect.
Definisce tutte le 6 tabelle del sistema.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    Numeric, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Tabella utenti per l'autenticazione."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(250), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relazioni bidirezionali
    account = relationship("Account", back_populates="owner", uselist=False)
    portfolio = relationship("Portfolio", back_populates="owner", uselist=False)


class Account(Base):
    """Tabella conti bancari."""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(27), unique=True, nullable=False, index=True)  # IBAN
    balance = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    currency = Column(String(3), nullable=False, default="EUR")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relazioni
    owner = relationship("User", back_populates="account")
    sent_transactions = relationship(
        "Transaction", 
        back_populates="sender_account",
        foreign_keys="Transaction.sender_account_id"
    )
    received_transactions = relationship(
        "Transaction", 
        back_populates="receiver_account",
        foreign_keys="Transaction.receiver_account_id"
    )


class Transaction(Base):
    """Tabella transazioni/movimenti."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    sender_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    receiver_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    # Relazioni
    sender_account = relationship(
        "Account", 
        back_populates="sent_transactions",
        foreign_keys=[sender_account_id]
    )
    receiver_account = relationship(
        "Account", 
        back_populates="received_transactions",
        foreign_keys=[receiver_account_id]
    )


class InvestmentProduct(Base):
    """Tabella prodotti di investimento fittizi."""
    __tablename__ = "investment_products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    ticker = Column(String(10), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    current_price = Column(Numeric(10, 4), nullable=False)
    risk_profile = Column(String(50), nullable=False, index=True)  # Conservativo, Moderato, Aggressivo
    sim_annual_return_rate = Column(Numeric(5, 4), nullable=False)  # es. 0.05 = 5%
    sim_volatility = Column(Numeric(5, 4), nullable=False)  # es. 0.15 = 15%
    
    # Relazioni
    holdings = relationship("Holding", back_populates="product")


class Portfolio(Base):
    """Tabella portafogli di simulazione."""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String(100), nullable=False, default="Portafoglio di Simulazione")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relazioni
    owner = relationship("User", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")


class Holding(Base):
    """Tabella posizioni nel portafoglio."""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("investment_products.id"), nullable=False)
    quantity = Column(Numeric(12, 4), nullable=False)
    average_buy_price = Column(Numeric(10, 4), nullable=False)
    
    # Constraint per evitare duplicati
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'product_id', name='uq_portfolio_product'),
    )
    
    # Relazioni
    portfolio = relationship("Portfolio", back_populates="holdings")
    product = relationship("InvestmentProduct", back_populates="holdings")
