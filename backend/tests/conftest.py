"""
Pytest fixtures per i test.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.auth import get_password_hash
from app.models import User, Account, InvestmentProduct, Portfolio

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    db_session.flush()
    
    account = Account(
        account_number="IT00TEST0000000000001",
        balance=1000.00,
        currency="EUR",
        owner_id=user.id
    )
    db_session.add(account)
    
    portfolio = Portfolio(
        owner_id=user.id,
        name="Test Portfolio"
    )
    db_session.add(portfolio)
    
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def second_user(db_session):
    user = User(
        username="seconduser",
        email="second@example.com",
        full_name="Second User",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    db_session.flush()
    
    account = Account(
        account_number="IT00TEST0000000000002",
        balance=500.00,
        currency="EUR",
        owner_id=user.id
    )
    db_session.add(account)
    
    portfolio = Portfolio(
        owner_id=user.id,
        name="Second Portfolio"
    )
    db_session.add(portfolio)
    
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_product(db_session):
    product = InvestmentProduct(
        name="Test Fund",
        ticker="TEST",
        description="A test investment product",
        current_price=100.00,
        risk_profile="Moderato",
        sim_annual_return_rate=0.05,
        sim_volatility=0.10
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    return product


@pytest.fixture
def auth_token(client, test_user):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
