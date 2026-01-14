# FinConnect - Istruzioni per GitHub Copilot

> Questo file viene letto automaticamente da GitHub Copilot per avere contesto sul progetto.

## 📋 Informazioni Progetto

- **Nome:** FinConnect
- **Tipo:** Project Work - Tesi Triennale
- **Corso:** Informatica per le Aziende Digitali (L-31)
- **Deadline:** 30 Gennaio 2026
- **Descrizione:** Prototipo di Home Banking Full-Stack con simulazione investimenti

## 🛠 Stack Tecnologico

### Backend
- **Linguaggio:** Python 3.10+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 (sync)
- **Database:** PostgreSQL 15
- **Auth:** JWT con python-jose, bcrypt con passlib
- **Migrations:** Alembic
- **Validation:** Pydantic v2

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **Charts:** Recharts
- **Styling:** CSS vanilla (semplice, per demo)

## 📁 Struttura Progetto

```
FinConnect/
├── .github/
│   └── copilot-instructions.md  # Questo file
├── plan/
│   ├── Progettazione.md         # Documento di design
│   ├── PIANO_SVILUPPO.md        # Timeline e task
│   └── TemaTesi.md              # Requisiti tesi
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point FastAPI
│   │   ├── config.py            # Settings Pydantic
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT + password utils
│   │   └── routers/             # API endpoints
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── context/             # AuthContext
│       ├── services/            # api.js (Axios)
│       ├── pages/               # Route components
│       └── components/          # UI riutilizzabili
├── docs/
│   ├── diagrams/                # UML, ER
│   └── screenshots/             # Per la tesi
└── docker-compose.yml           # PostgreSQL + pgAdmin
```

## 🎯 Convenzioni di Codice

### Python/Backend
- **Naming:** snake_case per variabili e funzioni
- **Type hints:** SEMPRE, su tutti i parametri e return
- **Docstrings:** Google style per funzioni pubbliche
- **Imports:** Standard lib → Third party → Local (separati da linea vuota)
- **Models:** Una classe per tabella, relazioni bidirezionali
- **Schemas:** Separare Base, Create, Read per ogni entità

### React/Frontend
- **Naming:** camelCase per variabili, PascalCase per componenti
- **Componenti:** Functional components con hooks
- **File:** .jsx per componenti React
- **State:** useState per locale, Context per globale (auth)
- **Props:** Destructuring nei parametri

### API
- **Prefix:** /api/v1
- **Auth:** Bearer token in Authorization header
- **Errors:** HTTPException con status code appropriati
- **Response:** JSON sempre, mai HTML

## 🗄 Schema Database

### Tabelle (6)
1. **users** - Utenti (username, email, hashed_password, full_name)
2. **accounts** - Conti (account_number/IBAN, balance, currency, owner_id)
3. **transactions** - Movimenti (amount, description, sender_id, receiver_id)
4. **investment_products** - Prodotti fittizi (name, ticker, price, risk, return_rate, volatility)
5. **portfolios** - Portafoglio simulazione (owner_id, name)
6. **holdings** - Posizioni (portfolio_id, product_id, quantity, avg_price)

### Relazioni Chiave
- User 1:1 Account (semplificazione per prototipo)
- User 1:1 Portfolio
- Account 1:N Transaction (come sender o receiver)
- Portfolio 1:N Holding
- Holding N:1 InvestmentProduct

## 🔐 Autenticazione

- **Flow:** OAuth2 Password Flow
- **Token:** JWT con scadenza 24h (per demo)
- **Endpoint:** POST /api/v1/auth/token
- **Header:** `Authorization: Bearer <token>`
- **Dependency:** `get_current_user` in auth.py

## 📝 Endpoint API

| Metodo | Path | Auth | Descrizione |
|--------|------|------|-------------|
| POST | /auth/token | ❌ | Login, restituisce JWT |
| POST | /auth/register | ❌ | Registrazione utente |
| GET | /users/me | ✅ | Info utente corrente |
| GET | /accounts/me | ✅ | Dettagli conto |
| GET | /accounts/me/transactions | ✅ | Lista movimenti |
| POST | /transfers | ✅ | Esegui bonifico |
| GET | /investments/products | ✅ | Lista prodotti |
| GET | /investments/portfolio | ✅ | Portfolio utente |
| POST | /investments/simulate | ✅ | Simulazione PAC |

## ⚠️ Contesto Importante

1. **È un prototipo accademico** - Non serve sicurezza production-grade
2. **Focus su funzionalità** - UI deve essere funzionale, non bella
3. **JWT 24h** - Semplificazione per evitare refresh token
4. **SQLite per test** - Pytest usa SQLite in-memory
5. **4-5 test sufficienti** - Dimostrativi, non coverage completo

## 📅 Stato Attuale

Controlla `plan/PIANO_SVILUPPO.md` per lo stato aggiornato delle attività.

## 🚫 Cosa NON fare

- Non suggerire refresh token (non necessario)
- Non suggerire test E2E con Playwright/Cypress
- Non suggerire Docker per il frontend
- Non usare TypeScript (progetto in JS)
- Non usare styled-components o CSS-in-JS
- Non suggerire autenticazione social (Google, GitHub)
