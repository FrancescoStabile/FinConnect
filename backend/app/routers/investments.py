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


@router.post("/buy", response_model=schemas.BuyResponse, status_code=status.HTTP_201_CREATED)
async def buy_investment(
    buy_data: schemas.BuyRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acquista quote di un prodotto di investimento.
    
    Logica:
    1. Verifica che l'utente abbia saldo sufficiente
    2. Calcola quante quote può acquistare (importo / prezzo_quota)
    3. Sottrae l'importo dal saldo del conto
    4. Aggiorna/crea l'holding nel portafoglio
    """
    # Ottieni il conto dell'utente
    account = db.query(models.Account).filter(
        models.Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conto non trovato"
        )
    
    # Verifica saldo sufficiente
    if account.balance < buy_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insufficiente. Disponibile: €{account.balance}, Richiesto: €{buy_data.amount}"
        )
    
    # Ottieni il prodotto
    product = db.query(models.InvestmentProduct).filter(
        models.InvestmentProduct.id == buy_data.product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prodotto di investimento non trovato"
        )
    
    # Calcola le quote acquistate
    quantity = buy_data.amount / product.current_price
    
    # Ottieni o crea il portafoglio
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.owner_id == current_user.id
    ).first()
    
    if not portfolio:
        portfolio = models.Portfolio(
            owner_id=current_user.id,
            name="Portafoglio Investimenti"
        )
        db.add(portfolio)
        db.flush()  # Per ottenere l'ID
    
    # Cerca holding esistente per questo prodotto
    holding = db.query(models.Holding).filter(
        models.Holding.portfolio_id == portfolio.id,
        models.Holding.product_id == product.id
    ).first()
    
    if holding:
        # Aggiorna holding esistente con media ponderata del prezzo
        total_cost_old = holding.quantity * holding.average_buy_price
        total_cost_new = quantity * product.current_price
        new_quantity = holding.quantity + quantity
        new_avg_price = (total_cost_old + total_cost_new) / new_quantity
        
        holding.quantity = new_quantity
        holding.average_buy_price = new_avg_price
    else:
        # Crea nuovo holding
        holding = models.Holding(
            portfolio_id=portfolio.id,
            product_id=product.id,
            quantity=quantity,
            average_buy_price=product.current_price
        )
        db.add(holding)
    
    # Sottrai l'importo dal saldo
    account.balance -= buy_data.amount
    
    db.commit()
    
    return schemas.BuyResponse(
        message="Acquisto completato con successo",
        product_name=product.name,
        quantity_purchased=round(quantity, 4),
        amount_spent=buy_data.amount,
        new_account_balance=account.balance
    )


@router.post("/sell", response_model=schemas.SellResponse, status_code=status.HTTP_200_OK)
async def sell_investment(
    sell_data: schemas.SellRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vende quote di un prodotto di investimento dal portafoglio.
    
    Logica:
    1. Verifica che l'utente possieda abbastanza quote
    2. Calcola il valore al prezzo corrente
    3. Rimuove/riduce l'holding
    4. Accredita il valore sul conto bancario
    """
    # Ottieni il conto dell'utente
    account = db.query(models.Account).filter(
        models.Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conto non trovato"
        )
    
    # Ottieni il portafoglio
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.owner_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portafoglio non trovato"
        )
    
    # Ottieni il prodotto
    product = db.query(models.InvestmentProduct).filter(
        models.InvestmentProduct.id == sell_data.product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prodotto di investimento non trovato"
        )
    
    # Cerca l'holding
    holding = db.query(models.Holding).filter(
        models.Holding.portfolio_id == portfolio.id,
        models.Holding.product_id == product.id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Non possiedi quote di {product.name}"
        )
    
    # Verifica quantità sufficiente
    if holding.quantity < sell_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quote insufficienti. Possiedi: {holding.quantity}, Richiesto: {sell_data.quantity}"
        )
    
    # Calcola il valore di vendita
    sale_value = sell_data.quantity * product.current_price
    
    # Aggiorna o rimuovi l'holding
    if holding.quantity == sell_data.quantity:
        # Vendita totale: rimuovi l'holding
        db.delete(holding)
    else:
        # Vendita parziale: riduci la quantità
        holding.quantity -= sell_data.quantity
    
    # Accredita il valore sul conto
    account.balance += sale_value
    
    db.commit()
    
    return schemas.SellResponse(
        message="Vendita completata con successo",
        product_name=product.name,
        quantity_sold=sell_data.quantity,
        amount_received=round(sale_value, 2),
        new_account_balance=account.balance
    )
