"""
Router per autenticazione: login e registrazione.
"""
import random
import string
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Autenticazione"])


def generate_iban() -> str:
    """Genera un IBAN italiano fittizio."""
    # Formato: IT + 2 cifre controllo + 1 lettera + 5 cifre ABI + 5 cifre CAB + 12 caratteri conto
    country = "IT"
    check_digits = ''.join(random.choices(string.digits, k=2))
    cin = random.choice(string.ascii_uppercase)
    abi = ''.join(random.choices(string.digits, k=5))
    cab = ''.join(random.choices(string.digits, k=5))
    account = ''.join(random.choices(string.digits, k=12))
    
    return f"{country}{check_digits}{cin}{abi}{cab}{account}"


@router.post("/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Effettua il login e restituisce un token JWT."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password non corretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Registra un nuovo utente con conto associato."""
    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username già registrato"
        )
    
    # Verifica email univoca
    existing_email = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    # Crea l'utente
    hashed_password = auth.get_password_hash(user_data.password)
    
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.flush()  # Per ottenere l'ID dell'utente
    
    # Crea il conto associato con saldo iniziale di 1000€ per demo
    new_account = models.Account(
        account_number=generate_iban(),
        balance=1000.00,  # Saldo iniziale per demo
        currency="EUR",
        owner_id=new_user.id
    )
    
    db.add(new_account)
    
    # Crea anche il portafoglio vuoto
    new_portfolio = models.Portfolio(
        owner_id=new_user.id,
        name="Portafoglio di Simulazione"
    )
    
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_user)
    
    return new_user
