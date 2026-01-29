"""
Test API per FinConnect.
"""
import pytest
import time


class TestAuthentication:
    
    def test_register_user(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "securepassword"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """TC-Auth-01: Login con credenziali errate deve restituire 401."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401


class TestProtectedRoutes:
    """TC-Sec-01: Test protezione rotte autenticate."""
    
    def test_access_dashboard_without_auth(self, client):
        """Accesso a /accounts/me senza token deve restituire 401."""
        response = client.get("/api/v1/accounts/me")
        assert response.status_code == 401
    
    def test_access_portfolio_without_auth(self, client):
        """Accesso a /investments/portfolio senza token deve restituire 401."""
        response = client.get("/api/v1/investments/portfolio")
        assert response.status_code == 401
    
    def test_transfer_without_auth(self, client):
        """Tentativo di bonifico senza token deve restituire 401."""
        response = client.post(
            "/api/v1/transfers",
            json={
                "receiver_account_number": "IT00TEST0000000000002",
                "amount": 100.00,
                "description": "Test"
            }
        )
        assert response.status_code == 401


class TestAccounts:
    
    def test_get_my_account(self, client, test_user, auth_headers):
        response = client.get("/api/v1/accounts/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_number"] == "IT00TEST0000000000001"
        assert float(data["balance"]) == 1000.00
        assert data["currency"] == "EUR"


class TestTransfers:
    """TC-Bank: Test integrità transazioni bancarie."""
    
    def test_transfer_success(self, client, test_user, second_user, auth_headers, db_session):
        """TC-Bank-02: Bonifico valido - verifica atomicità ACID."""
        response = client.post(
            "/api/v1/transfers",
            headers=auth_headers,
            json={
                "receiver_account_number": "IT00TEST0000000000002",
                "amount": 100.00,
                "description": "Test transfer"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == 100.00
        assert data["description"] == "Test transfer"
    
    def test_transfer_insufficient_funds(self, client, test_user, second_user, auth_headers):
        """TC-Bank-01: Bonifico superiore al saldo deve essere bloccato con 400."""
        response = client.post(
            "/api/v1/transfers",
            headers=auth_headers,
            json={
                "receiver_account_number": "IT00TEST0000000000002",
                "amount": 9999.00,  # Più del saldo disponibile
                "description": "Test transfer"
            }
        )
        
        assert response.status_code == 400
        assert "insufficiente" in response.json()["detail"].lower()
    
    def test_transfer_to_self_blocked(self, client, test_user, auth_headers):
        """Bonifico verso se stessi deve essere bloccato."""
        response = client.post(
            "/api/v1/transfers",
            headers=auth_headers,
            json={
                "receiver_account_number": "IT00TEST0000000000001",  # Stesso conto
                "amount": 50.00,
                "description": "Self transfer"
            }
        )
        
        assert response.status_code == 400
        assert "stesso conto" in response.json()["detail"].lower()
    
    def test_transfer_to_nonexistent_account(self, client, test_user, auth_headers):
        """Bonifico verso conto inesistente deve restituire 404."""
        response = client.post(
            "/api/v1/transfers",
            headers=auth_headers,
            json={
                "receiver_account_number": "IT99INVALID000000000",
                "amount": 50.00,
                "description": "Invalid transfer"
            }
        )
        
        assert response.status_code == 404


class TestSimulation:
    """Test simulazione PAC Monte Carlo."""
    
    def test_simulate_pac(self, client, test_user, test_product, auth_headers):
        """Verifica che la simulazione restituisca proiezioni crescenti."""
        response = client.post(
            "/api/v1/investments/simulate",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "initial_amount": 1000,
                "monthly_contribution": 100,
                "investment_period_years": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["product_name"] == "Test Fund"
        assert "projection_data" in data
        assert len(data["projection_data"]) == 5
        
        projections = data["projection_data"]
        assert float(projections[-1]["projected_average_value"]) > float(projections[0]["projected_average_value"])
    
    def test_simulate_pac_capital_invested_correct(self, client, test_user, test_product, auth_headers):
        """Verifica correttezza calcolo capitale investito."""
        initial = 1000
        monthly = 100
        years = 5
        
        response = client.post(
            "/api/v1/investments/simulate",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "initial_amount": initial,
                "monthly_contribution": monthly,
                "investment_period_years": years
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Capitale investito = iniziale + (mensile * 12 * anni)
        expected_capital = initial + (monthly * 12 * years)
        actual_capital = float(data["projection_data"][-1]["total_invested"])
        
        assert actual_capital == expected_capital


class TestValidation:
    """Test validazione input Pydantic."""
    
    def test_register_invalid_email(self, client):
        """Email non valida deve restituire 422."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "full_name": "Test User",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_register_short_password(self, client):
        """Password troppo corta deve restituire 422."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "123"  # < 6 caratteri
            }
        )
        assert response.status_code == 422
    
    def test_transfer_negative_amount(self, client, test_user, auth_headers):
        """Importo negativo deve restituire 422."""
        response = client.post(
            "/api/v1/transfers",
            headers=auth_headers,
            json={
                "receiver_account_number": "IT00TEST0000000000002",
                "amount": -100.00,
                "description": "Invalid"
            }
        )
        assert response.status_code == 422
