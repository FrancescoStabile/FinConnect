"""
Router per gestione conti e transazioni.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/accounts", tags=["Conti"])


@router.get("/me", response_model=schemas.AccountRead)
async def get_my_account(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Restituisce il conto dell'utente autenticato."""
    account = db.query(models.Account).filter(
        models.Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun conto associato a questo utente"
        )
    
    return account


@router.get("/me/transactions", response_model=List[schemas.TransactionRead])
async def get_my_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Restituisce le transazioni del conto dell'utente."""
    account = db.query(models.Account).filter(
        models.Account.owner_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun conto associato a questo utente"
        )
    
    # Ottieni tutte le transazioni (inviate o ricevute)
    transactions = db.query(models.Transaction).filter(
        or_(
            models.Transaction.sender_account_id == account.id,
            models.Transaction.receiver_account_id == account.id
        )
    ).order_by(
        models.Transaction.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return transactions
