"""
Script per popolare il database con dati demo.
"""
import sys
sys.path.insert(0, '.')

from decimal import Decimal
from app.database import SessionLocal, engine, Base
from app.models import User, Account, InvestmentProduct, Portfolio
from app.auth import get_password_hash


def seed_database():
    """Popola il database con dati di esempio."""
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database gia popolato, seed saltato.")
            print(f"Utenti esistenti: {existing_users}")
            return
        
        print("Avvio seed del database...")
        
        users_data = [
            {
                "username": "mario.rossi",
                "email": "mario.rossi@email.com",
                "full_name": "Mario Rossi",
                "password": "password123",
                "initial_balance": Decimal("5000.00")
            },
            {
                "username": "giulia.bianchi",
                "email": "giulia.bianchi@email.com", 
                "full_name": "Giulia Bianchi",
                "password": "password123",
                "initial_balance": Decimal("3500.00")
            },
            {
                "username": "luca.verdi",
                "email": "luca.verdi@email.com",
                "full_name": "Luca Verdi",
                "password": "password123",
                "initial_balance": Decimal("8000.00")
            }
        ]
        
        for i, user_data in enumerate(users_data):
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"])
            )
            db.add(user)
            db.flush()
            
            account = Account(
                account_number=f"IT60X0542811101000000{12345 + i}",
                balance=user_data["initial_balance"],
                currency="EUR",
                owner_id=user.id
            )
            db.add(account)
            
            portfolio = Portfolio(
                owner_id=user.id,
                name="Portafoglio di Simulazione"
            )
            db.add(portfolio)
            
            print(f"Creato utente: {user_data['username']}")
        
        products_data = [
            {
                "name": "Fondo Obbligazionario Sicuro",
                "ticker": "FOBSIC",
                "description": "Fondo a basso rischio che investe in obbligazioni governative europee. Ideale per chi cerca stabilità.",
                "current_price": Decimal("102.50"),
                "risk_profile": "Conservativo",
                "sim_annual_return_rate": Decimal("0.025"),  # 2.5%
                "sim_volatility": Decimal("0.03")  # 3%
            },
            {
                "name": "Fondo Bilanciato Equilibrio",
                "ticker": "FBEQUI",
                "description": "Mix equilibrato di azioni e obbligazioni per una crescita moderata con rischio contenuto.",
                "current_price": Decimal("156.80"),
                "risk_profile": "Moderato",
                "sim_annual_return_rate": Decimal("0.05"),  # 5%
                "sim_volatility": Decimal("0.10")  # 10%
            },
            {
                "name": "ETF Azionario Globale",
                "ticker": "ETFGLB",
                "description": "Replica l'andamento delle principali borse mondiali. Diversificazione geografica massima.",
                "current_price": Decimal("89.25"),
                "risk_profile": "Moderato",
                "sim_annual_return_rate": Decimal("0.07"),  # 7%
                "sim_volatility": Decimal("0.15")  # 15%
            },
            {
                "name": "Fondo Azionario Tech",
                "ticker": "FATECH",
                "description": "Investe nelle principali aziende tecnologiche. Alto potenziale di crescita, alta volatilità.",
                "current_price": Decimal("245.00"),
                "risk_profile": "Aggressivo",
                "sim_annual_return_rate": Decimal("0.12"),  # 12%
                "sim_volatility": Decimal("0.25")  # 25%
            },
            {
                "name": "Fondo Mercati Emergenti",
                "ticker": "FMEMER",
                "description": "Esposizione ai mercati in via di sviluppo: Asia, America Latina, Africa. Rischio elevato.",
                "current_price": Decimal("67.30"),
                "risk_profile": "Aggressivo",
                "sim_annual_return_rate": Decimal("0.10"),  # 10%
                "sim_volatility": Decimal("0.30")  # 30%
            }
        ]
        
        for product_data in products_data:
            product = InvestmentProduct(**product_data)
            db.add(product)
            print(f"Creato prodotto: {product_data['name']}")
        
        db.commit()
        
        print("\nSeed completato.")
        print("\nCredenziali demo:")
        print("  mario.rossi / password123")
        print("  giulia.bianchi / password123")
        print("  luca.verdi / password123")
        
    except Exception as e:
        db.rollback()
        print(f"Errore durante il seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
