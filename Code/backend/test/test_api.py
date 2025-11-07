# Test API endpoints

import requests
import json

BASE_URL = 'http://localhost:5000/api'

print("🧪 Testing API endpoints...\n")

# Test 1: Health check
print("1️⃣ Testing /health...")
response = requests.get(f'{BASE_URL}/health')
print(f"Status: {response.status_code}")
print(f"Data: {json.dumps(response.json(), indent=2)}\n")

# Test 2: Energy by model
print("2️⃣ Testing /energy-by-model...")
response = requests.get(f'{BASE_URL}/energy-by-model')
print(f"Status: {response.status_code}")
data = response.json()
print(f"Found {len(data)} models")
if data:
    print(f"First model: {json.dumps(data[0], indent=2)}\n")

# Test 3: Timeline
print("3️⃣ Testing /energy-timeline...")
response = requests.get(f'{BASE_URL}/energy-timeline')
print(f"Status: {response.status_code}")
data = response.json()
print(f"Found {len(data)} time points")
if data:
    print(f"First point: {json.dumps(data[0], indent=2)}\n")

# Test 4: Efficiency
print("4️⃣ Testing /energy-efficiency...")
response = requests.get(f'{BASE_URL}/energy-efficiency')
print(f"Status: {response.status_code}")
data = response.json()
print(f"Found {len(data)} data points")
if data:
    print(f"First point: {json.dumps(data[0], indent=2)}\n")

# Test 5: Calculate CO2
print("5️⃣ Testing /calculate-co2...")
payload = {
    "model": "gemma_2b",
    "platform": "laptop1",
    "energy_source": "mix_france",
    "prompt": "Write a Python function"
}
response = requests.post(f'{BASE_URL}/calculate-co2', json=payload)
print(f"Status: {response.status_code}")
print(f"Result: {json.dumps(response.json(), indent=2)}\n")

# Test 6: Models list
print("6️⃣ Testing /models...")
response = requests.get(f'{BASE_URL}/models')
print(f"Status: {response.status_code}")
print(f"Models: {response.json()}\n")

# Test 7: Platforms for model
print("7️⃣ Testing /platforms/gemma_2b...")
response = requests.get(f'{BASE_URL}/platforms/gemma_2b')
print(f"Status: {response.status_code}")
print(f"Platforms: {response.json()}\n")

print("✅ All tests completed!")
