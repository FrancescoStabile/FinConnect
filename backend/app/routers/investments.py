"""
Router per prodotti di investimento, portafoglio e simulazione PAC.
"""
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/investments", tags=["Investimenti"])


@router.get("/products", response_model=List[schemas.InvestmentProductRead])
async def get_products(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Restituisce l'elenco di tutti i prodotti di investimento disponibili.
    """
    products = db.query(models.InvestmentProduct).all()
    return products


@router.get("/portfolio", response_model=schemas.PortfolioRead)
async def get_portfolio(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Restituisce il portafoglio di simulazione dell'utente.
    Se non esiste, lo crea vuoto.
    """
    # Cerca il portafoglio esistente
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.owner_id == current_user.id
    ).first()
    
    # Se non esiste, crealo
    if not portfolio:
        portfolio = models.Portfolio(
            owner_id=current_user.id,
            name="Portafoglio di Simulazione"
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    # Calcola i valori per ogni holding
    holdings_data = []
    total_value = Decimal("0.00")
    
    for holding in portfolio.holdings:
        current_value = holding.quantity * holding.product.current_price
        cost_basis = holding.quantity * holding.average_buy_price
        profit_loss = current_value - cost_basis
        
        holdings_data.append({
            "id": holding.id,
            "product": holding.product,
            "quantity": holding.quantity,
            "average_buy_price": holding.average_buy_price,
            "current_value": current_value,
            "profit_loss": profit_loss
        })
        
        total_value += current_value
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "owner_id": portfolio.owner_id,
        "holdings": holdings_data,
        "total_value": total_value
    }


@router.post("/simulate", response_model=schemas.SimulationResult)
async def simulate_pac(
    simulation_data: schemas.SimulationRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Esegue una simulazione "what-if" di un Piano di Accumulo (PAC).
    
    Non modifica il portafoglio, è solo una proiezione.
    
    - product_id: ID del prodotto su cui simulare
    - initial_amount: Importo iniziale investito
    - monthly_contribution: Contributo mensile
    - investment_period_years: Durata in anni (1-50)
    
    Restituisce proiezioni per scenario medio, migliore e peggiore.
    """
    # Ottieni il prodotto
    product = db.query(models.InvestmentProduct).filter(
        models.InvestmentProduct.id == simulation_data.product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prodotto non trovato"
        )
    
    # Parametri per la simulazione
    initial = simulation_data.initial_amount
    monthly = simulation_data.monthly_contribution
    years = simulation_data.investment_period_years
    
    # Tassi dal prodotto
    annual_return = float(product.sim_annual_return_rate)
    volatility = float(product.sim_volatility)
    
    # Scenari: medio, best case (+1 std dev), worst case (-1 std dev)
    monthly_return_avg = (1 + annual_return) ** (1/12) - 1
    monthly_return_best = (1 + annual_return + volatility) ** (1/12) - 1
    monthly_return_worst = (1 + annual_return - volatility) ** (1/12) - 1
    
    projection_data = []
    
    # Valori iniziali
    value_avg = float(initial)
    value_best = float(initial)
    value_worst = float(initial)
    total_invested = float(initial)
    
    # Proiezione anno per anno
    for year in range(1, years + 1):
        # Simula 12 mesi
        for month in range(12):
            # Aggiungi contributo mensile
            value_avg += float(monthly)
            value_best += float(monthly)
            value_worst += float(monthly)
            total_invested += float(monthly)
            
            # Applica rendimento
            value_avg *= (1 + monthly_return_avg)
            value_best *= (1 + monthly_return_best)
            value_worst *= (1 + max(monthly_return_worst, -0.99))  # Protezione da valori negativi
        
        # Salva punto dati per questo anno
        projection_data.append(schemas.SimulationProjectionPoint(
            year=year,
            total_invested=Decimal(str(round(total_invested, 2))),
            projected_average_value=Decimal(str(round(value_avg, 2))),
            projected_best_case=Decimal(str(round(value_best, 2))),
            projected_worst_case=Decimal(str(round(max(value_worst, 0), 2)))
        ))
    
    return schemas.SimulationResult(
        request=simulation_data,
        product_name=product.name,
        total_invested_final=Decimal(str(round(total_invested, 2))),
        projected_average_final=Decimal(str(round(value_avg, 2))),
        projected_best_final=Decimal(str(round(value_best, 2))),
        projected_worst_final=Decimal(str(round(max(value_worst, 0), 2))),
        projection_data=projection_data
    )
