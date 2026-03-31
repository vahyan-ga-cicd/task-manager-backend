import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_audit_admin():
    try:
        # Note: This will likely fail without a valid JWT token
        # But we want to see if the route exists
        response = requests.get(f"{BASE_URL}/audit/admin")
        print(f"Admin Audit Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_audit_admin()
