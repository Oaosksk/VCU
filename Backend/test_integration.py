"""Test backend endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing /...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_cors():
    """Test CORS headers"""
    print("Testing CORS...")
    headers = {"Origin": "http://localhost:5173"}
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"CORS Headers: {dict(response.headers)}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("Backend Integration Test")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_root()
        test_cors()
        print("✅ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend")
        print("Make sure backend is running:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
