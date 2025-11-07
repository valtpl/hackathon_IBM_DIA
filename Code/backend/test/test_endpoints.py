from main import app
import json

# Create a test client
with app.test_client() as client:
    # Test timeline endpoint
    print("=" * 50)
    print("TIMELINE ENDPOINT:")
    print("=" * 50)
    response = client.get('/api/energy-timeline')
    data = response.get_json()
    print(json.dumps(data, indent=2))
    
    print("\n" + "=" * 50)
    print("EFFICIENCY ENDPOINT:")
    print("=" * 50)
    # Test efficiency endpoint
    response = client.get('/api/energy-efficiency')
    data = response.get_json()
    print(json.dumps(data, indent=2))
