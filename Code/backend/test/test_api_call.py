"""Quick test of IBM Watson ML API call with 88 features"""
import sys
sys.path.insert(0, '.')

from main import predict_energy_ibm_wml

# Test the function
try:
    result = predict_energy_ibm_wml(
        prompt_text="Hello, how are you doing today?",
        model="alpaca_llama3_70b",
        platform="server"
    )
    
    if result is not None:
        print(f"\n✓ SUCCESS! Predicted energy: {result} kWh")
    else:
        print("\n⚠ Prediction returned None (fallback to statistical method)")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
