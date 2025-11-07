"""Test IBM Watson ML API with 10 different prompts - RAW output"""
import sys
sys.path.insert(0, '.')

from main import predict_energy_ibm_wml

# 10 test prompts with different lengths and complexities
test_prompts = [
    "yes",
    "say yes",
    "Hello",
    "Hello how are you?",
    "What is machine learning?",
    "Explain the concept of artificial intelligence",
    "Write a detailed explanation of supervised learning algorithms",
    "Can you describe the differences between neural networks and traditional machine learning approaches?",
    "Provide a comprehensive analysis of the environmental impact of large language models including carbon footprint calculations",
    "Write a complete technical documentation explaining how transformer architectures work in modern natural language processing systems, including attention mechanisms, positional encodings, and multi-head attention layers"
]

print("="*100)
print("RAW IBM WATSON ML API PREDICTIONS - 10 PROMPTS")
print("="*100)
print(f"\nModel: alpaca_llama3_8b")
print(f"Platform: laptop2")
print(f"\n{'#':<4} {'Words':<6} {'Chars':<6} {'Energy (kWh)':<20} {'Prompt Preview':<50}")
print("-"*100)

results = []

for i, prompt in enumerate(test_prompts, 1):
    word_count = len(prompt.split())
    char_count = len(prompt)
    
    try:
        # Get raw prediction from IBM Watson ML
        energy_kwh = predict_energy_ibm_wml(
            prompt_text=prompt,
            model="alpaca_llama3_8b",
            platform="laptop2"
        )
        
        if energy_kwh is not None:
            results.append({
                'id': i,
                'words': word_count,
                'chars': char_count,
                'energy_kwh': energy_kwh,
                'prompt': prompt
            })
            
            preview = prompt[:47] + "..." if len(prompt) > 50 else prompt
            print(f"{i:<4} {word_count:<6} {char_count:<6} {energy_kwh:<20.18f} {preview:<50}")
        else:
            print(f"{i:<4} {word_count:<6} {char_count:<6} {'FAILED':<20} {prompt[:50]:<50}")
            
    except Exception as e:
        print(f"{i:<4} {word_count:<6} {char_count:<6} ERROR: {str(e)[:15]:<20} {prompt[:50]:<50}")

# Summary statistics
print("\n" + "="*100)
print("DETAILED RAW VALUES")
print("="*100)

for r in results:
    print(f"\n#{r['id']} - {r['words']} words, {r['chars']} chars")
    print(f"Prompt: \"{r['prompt']}\"")
    print(f"Raw Energy (kWh): {r['energy_kwh']:.18f}")
    print(f"Raw Energy (Wh):  {r['energy_kwh'] * 1000:.15f}")
    print(f"Raw Energy (mWh): {r['energy_kwh'] * 1000000:.12f}")

# Ratios
if len(results) >= 2:
    print("\n" + "="*100)
    print("ENERGY PROGRESSION ANALYSIS (RAW)")
    print("="*100)
    
    min_energy = results[0]['energy_kwh']
    max_energy = results[-1]['energy_kwh']
    
    print(f"\nShortest prompt ({results[0]['words']} words): {min_energy:.18f} kWh")
    print(f"Longest prompt ({results[-1]['words']} words):  {max_energy:.18f} kWh")
    print(f"Ratio (longest/shortest): {max_energy/min_energy:.6f}x")
    
    print(f"\n{'From':<4} {'To':<4} {'Ratio':<10} {'Increase %':<12}")
    print("-"*35)
    for i in range(len(results)-1):
        ratio = results[i+1]['energy_kwh'] / results[i]['energy_kwh']
        increase = ((results[i+1]['energy_kwh'] - results[i]['energy_kwh']) / results[i]['energy_kwh']) * 100
        print(f"#{i+1:<3} #{i+2:<3} {ratio:<10.4f} {increase:>10.2f}%")

print("\n" + "="*100)
