"""
Router per gestione utenti.
"""
from fastapi import APIRouter, Depends

from app import models, schemas, auth

router = APIRouter(prefix="/users", tags=["Utenti"])


@router.get("/me", response_model=schemas.UserRead)
async def get_current_user_info(
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Restituisce le informazioni dell'utente autenticato.
    """
    return current_user
