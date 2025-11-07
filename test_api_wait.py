import requests
import json
import time

time.sleep(3)  # Wait for server to be ready

print("Testing API endpoints...")
print("=" * 50)

try:
    # Test timeline
    print("\n1. Testing /api/energy-timeline")
    response = requests.get('http://localhost:5000/api/energy-timeline', timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Data length: {len(data)}")
    if len(data) > 0:
        print("✓ Timeline has data!")
        print(json.dumps(data[0], indent=2))
    else:
        print("✗ Timeline is empty!")
    
    # Test efficiency
    print("\n2. Testing /api/energy-efficiency")
    response = requests.get('http://localhost:5000/api/energy-efficiency', timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Data length: {len(data)}")
    if len(data) > 0:
        print("First item:")
        print(json.dumps(data[0], indent=2))
        # Check if model names are formatted
        if ' ' in data[0].get('model', ''):
            print("✓ Model names are formatted!")
        else:
            print("✗ Model names are NOT formatted!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
