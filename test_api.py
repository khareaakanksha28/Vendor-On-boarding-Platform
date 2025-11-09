#!/usr/bin/env python3
"""
Simple API test script for Onboarding Hub
"""
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get("http://localhost:5000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 201:
        return response.json().get('access_token')
    return None

def test_login(email, password):
    """Test user login"""
    print("Testing user login...")
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_fraud_check(token):
    """Test fraud detection"""
    print("Testing fraud detection...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "age": 35,
        "account_age_years": 2.5,
        "annual_income": 75000,
        "credit_score": 720,
        "num_devices": 2,
        "hours_since_registration": 5,
        "failed_login_attempts": 0,
        "transaction_amount": 100
    }
    response = requests.post(f"{BASE_URL}/fraud/check", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_profile(token):
    """Test get profile"""
    print("Testing get profile...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("Onboarding Hub API Test Suite")
    print("=" * 50)
    print()
    
    # Test health check
    try:
        test_health_check()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend server is running on http://localhost:5000")
        exit(1)
    
    # Test registration
    token = test_register()
    print()
    
    if not token:
        # Try login instead
        token = test_login("test@example.com", "testpassword123")
        print()
    
    if token:
        # Test fraud check
        test_fraud_check(token)
        
        # Test profile
        test_profile(token)
    else:
        print("Failed to get authentication token. Cannot test protected endpoints.")
    
    print("=" * 50)
    print("Test suite completed!")
    print("=" * 50)

