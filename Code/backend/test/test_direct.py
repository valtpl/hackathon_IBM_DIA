from main import app
import json

# Create a test client
with app.test_client() as client:
    # Test health endpoint
    response = client.get('/api/health')
    print("Health endpoint:")
    print(json.dumps(response.get_json(), indent=2))
    print()
    
    # Test energy-by-model endpoint
    response = client.get('/api/energy-by-model')
    print("Energy by model endpoint:")
    data = response.get_json()
    if isinstance(data, list):
        print(f"Returned {len(data)} models")
        if len(data) > 0:
            print("First model:", json.dumps(data[0], indent=2))
    else:
        print(json.dumps(data, indent=2))
