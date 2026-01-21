"""
Test API per FinConnect.
"""
import pytest


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
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "wrongpassword"}
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
    
    def test_transfer_success(self, client, test_user, second_user, auth_headers, db_session):
        response = client.post(
            "/api/v1/transfers/",
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
        response = client.post(
            "/api/v1/transfers/",
            headers=auth_headers,
            json={
                "receiver_account_number": "IT00TEST0000000000002",
                "amount": 9999.00,  # Più del saldo disponibile
                "description": "Test transfer"
            }
        )
        
        assert response.status_code == 400
        assert "insufficiente" in response.json()["detail"].lower()


class TestSimulation:
    
    def test_simulate_pac(self, client, test_user, test_product, auth_headers):
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
