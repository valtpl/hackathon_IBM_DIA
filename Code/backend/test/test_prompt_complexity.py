"""Test IBM Watson ML predictions with different prompt complexities"""
import sys
sys.path.insert(0, '.')

from main import predict_energy_ibm_wml

# Test cases: simple vs complex prompts
test_cases = [
    {
        "name": "Very simple",
        "prompt": "say yes",
        "model": "alpaca_llama3_8b",
        "platform": "laptop2"
    },
    {
        "name": "Simple",
        "prompt": "Hello, how are you?",
        "model": "alpaca_llama3_8b",
        "platform": "laptop2"
    },
    {
        "name": "Medium",
        "prompt": "Can you explain what machine learning is and how it works?",
        "model": "alpaca_llama3_8b",
        "platform": "laptop2"
    },
    {
        "name": "Complex",
        "prompt": "Write a detailed explanation of the differences between supervised and unsupervised learning algorithms, including examples of each type and their practical applications in real-world scenarios.",
        "model": "alpaca_llama3_8b",
        "platform": "laptop2"
    },
    {
        "name": "Very complex (70B model)",
        "prompt": "Write a detailed explanation of the differences between supervised and unsupervised learning algorithms, including examples of each type and their practical applications in real-world scenarios.",
        "model": "alpaca_llama3_70b",
        "platform": "server"
    }
]

print("="*80)
print("Testing IBM Watson ML Predictions with Different Prompt Complexities")
print("="*80)

results = []

for test in test_cases:
    print(f"\n{test['name'].upper()}: \"{test['prompt'][:60]}...\"")
    print(f"Model: {test['model']}, Platform: {test['platform']}")
    print("-" * 80)
    
    try:
        energy_kwh = predict_energy_ibm_wml(
            prompt_text=test['prompt'],
            model=test['model'],
            platform=test['platform']
        )
        
        if energy_kwh is not None:
            # Calculate CO2 with wind energy (7 g/kWh)
            co2_grams = energy_kwh * 7
            
            results.append({
                'name': test['name'],
                'words': len(test['prompt'].split()),
                'energy_kwh': energy_kwh,
                'energy_wh': energy_kwh * 1000,
                'co2_grams': co2_grams,
                'model': test['model'],
                'platform': test['platform']
            })
            
            print(f"✓ Energy: {energy_kwh:.6f} kWh = {energy_kwh * 1000:.4f} Wh")
            print(f"✓ CO2 (wind, 7g/kWh): {co2_grams:.6f} g")
        else:
            print(f"✗ Prediction failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

# Summary comparison
print("\n" + "="*80)
print("SUMMARY COMPARISON")
print("="*80)
print(f"{'Complexity':<20} {'Words':<8} {'Energy (Wh)':<15} {'CO2 (g)':<15} {'Model':<20}")
print("-" * 80)

for r in results:
    print(f"{r['name']:<20} {r['words']:<8} {r['energy_wh']:<15.6f} {r['co2_grams']:<15.6f} {r['model']:<20}")

# Calculate ratios
if len(results) >= 2:
    simple_energy = results[0]['energy_wh']
    complex_energy = results[-1]['energy_wh']
    
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    print(f"Simplest prompt: {results[0]['words']} words → {simple_energy:.6f} Wh")
    print(f"Most complex prompt: {results[-1]['words']} words → {complex_energy:.6f} Wh")
    print(f"Ratio (complex/simple): {complex_energy/simple_energy:.2f}x")
    print(f"\nThe complex prompt consumes {complex_energy/simple_energy:.2f}x more energy!")
