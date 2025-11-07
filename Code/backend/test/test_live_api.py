import requests
import json

print("Testing API endpoints...")
print("=" * 50)

try:
    # Test timeline
    print("\n1. Testing /api/energy-timeline")
    response = requests.get('http://localhost:5000/api/energy-timeline')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Data length: {len(data)}")
    print(json.dumps(data, indent=2))
    
    # Test efficiency
    print("\n2. Testing /api/energy-efficiency")
    response = requests.get('http://localhost:5000/api/energy-efficiency')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Data length: {len(data)}")
    print(json.dumps(data[:3], indent=2))  # Just first 3 items
    
except Exception as e:
    print(f"Error: {e}")
