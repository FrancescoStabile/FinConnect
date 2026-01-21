"""
Schemi Pydantic per la validazione dei dati API.
Definisce i contratti JSON per request e response.
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List, Optional


# ============== AUTENTICAZIONE ==============

class Token(BaseModel):
    """Risposta con token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Dati estratti dal token JWT."""
    username: Optional[str] = None


# ============== UTENTE ==============

class UserBase(BaseModel):
    """Campi base dell'utente."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=250)


class UserCreate(UserBase):
    """Schema per la registrazione utente."""
    password: str = Field(..., min_length=6)


class UserRead(UserBase):
    """Schema per la lettura utente (response)."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== CONTO ==============

class AccountBase(BaseModel):
    """Campi base del conto."""
    account_number: str
    currency: str = "EUR"


class AccountRead(AccountBase):
    """Schema per la lettura conto (response)."""
    id: int
    balance: Decimal
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== TRANSAZIONI ==============

class TransactionBase(BaseModel):
    """Campi base della transazione."""
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=255)


class TransferRequest(BaseModel):
    """Schema per richiesta bonifico."""
    receiver_account_number: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=255)


class TransactionRead(BaseModel):
    """Schema per la lettura transazione (response)."""
    id: int
    amount: Decimal
    description: Optional[str]
    timestamp: datetime
    sender_account_id: int
    receiver_account_id: int
    
    model_config = ConfigDict(from_attributes=True)


# ============== PRODOTTI INVESTIMENTO ==============

class InvestmentProductRead(BaseModel):
    """Schema per la lettura prodotto investimento."""
    id: int
    name: str
    ticker: str
    description: Optional[str]
    current_price: Decimal
    risk_profile: str
    sim_annual_return_rate: Decimal
    sim_volatility: Decimal
    
    model_config = ConfigDict(from_attributes=True)


# ============== HOLDINGS ==============

class HoldingRead(BaseModel):
    """Schema per la lettura posizione nel portafoglio."""
    id: int
    product: InvestmentProductRead
    quantity: Decimal
    average_buy_price: Decimal
    current_value: Decimal  # Calcolato: quantity * current_price
    profit_loss: Decimal    # Calcolato: current_value - (quantity * average_buy_price)
    
    model_config = ConfigDict(from_attributes=True)


# ============== PORTAFOGLIO ==============

class PortfolioRead(BaseModel):
    """Schema per la lettura portafoglio."""
    id: int
    name: str
    owner_id: int
    holdings: List[HoldingRead]
    total_value: Decimal  # Calcolato: somma current_value di tutti gli holdings
    
    model_config = ConfigDict(from_attributes=True)


# ============== SIMULAZIONE ==============

class SimulationRequest(BaseModel):
    """Schema per richiesta simulazione PAC."""
    product_id: int
    initial_amount: Decimal = Field(..., ge=0)
    monthly_contribution: Decimal = Field(..., ge=0)
    investment_period_years: int = Field(..., gt=0, le=50)


class SimulationProjectionPoint(BaseModel):
    """Punto dati per la proiezione annuale."""
    year: int
    total_invested: Decimal
    projected_average_value: Decimal
    projected_best_case: Decimal
    projected_worst_case: Decimal


class SimulationResult(BaseModel):
    """Risultato completo della simulazione."""
    request: SimulationRequest
    product_name: str
    total_invested_final: Decimal
    projected_average_final: Decimal
    projected_best_final: Decimal
    projected_worst_final: Decimal
    projection_data: List[SimulationProjectionPoint]
