import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_index_status():
    """Test the index status endpoint."""
    response = requests.get(f"{BASE_URL}/index/status")
    print("Index Status Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_chat_simple():
    """Test the simple chat endpoint."""
    data = {
        "query": "What are the main challenges in connectivity in South Asia?"
    }
    response = requests.post(f"{BASE_URL}/chat/simple", json=data)
    print("\nChat Simple Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    # Wait for the server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Test endpoints
    status = test_index_status()
    
    if status.get("status") == "success":
        test_chat_simple()
    else:
        print("\nIndex not ready yet. Try again later.")
