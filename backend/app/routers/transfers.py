"""
Router per i bonifici.
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/transfers", tags=["Bonifici"])


@router.post("/", response_model=schemas.TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_data: schemas.TransferRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Esegue un bonifico dal conto dell'utente autenticato a un altro conto.
    
    - receiver_account_number: IBAN del destinatario
    - amount: Importo del bonifico (deve essere > 0)
    - description: Descrizione/causale (opzionale)
    """
    # 1. Ottieni il conto del mittente
    sender_account = db.query(models.Account).filter(
        models.Account.owner_id == current_user.id
    ).first()
    
    if not sender_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun conto associato a questo utente"
        )
    
    # 2. Ottieni il conto del destinatario
    receiver_account = db.query(models.Account).filter(
        models.Account.account_number == transfer_data.receiver_account_number
    ).first()
    
    if not receiver_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conto destinatario non trovato"
        )
    
    # 3. Verifica che non sia un bonifico verso se stessi
    if sender_account.id == receiver_account.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi effettuare un bonifico verso il tuo stesso conto"
        )
    
    # 4. Verifica fondi sufficienti
    if sender_account.balance < transfer_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insufficiente per completare il bonifico"
        )
    
    # 5. Esegui il trasferimento (operazione atomica)
    sender_account.balance = sender_account.balance - transfer_data.amount
    receiver_account.balance = receiver_account.balance + transfer_data.amount
    
    # 6. Crea il record della transazione
    transaction = models.Transaction(
        amount=transfer_data.amount,
        description=transfer_data.description,
        sender_account_id=sender_account.id,
        receiver_account_id=receiver_account.id
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction
