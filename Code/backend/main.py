import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from ibm_watson_machine_learning import APIClient
import re
import string

# Load environment variables from .env file in the same directory as this script
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"DEBUG: Loading .env from: {env_path}")
print(f"DEBUG: .env exists: {os.path.exists(env_path)}")
result = load_dotenv(env_path)
print(f"DEBUG: load_dotenv result: {result}")

# Test direct read
with open(env_path, 'r') as f:
    print(f"DEBUG: .env content:\n{f.read()[:200]}")

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# IBM Watson ML credentials
wml_url = os.getenv('IBM_WML_URL')
wml_apikey = os.getenv('IBM_WML_APIKEY')
wml_space_id = os.getenv('IBM_WML_SPACE_ID')
wml_deployment_id = os.getenv('IBM_WML_DEPLOYMENT_ID')

print(f"DEBUG: IBM_WML_URL = {wml_url}")
print(f"DEBUG: IBM_WML_APIKEY = {wml_apikey[:20] if wml_apikey else None}...")
print(f"DEBUG: IBM_WML_SPACE_ID = {wml_space_id}")
print(f"DEBUG: IBM_WML_DEPLOYMENT_ID = {wml_deployment_id}")

wml_credentials = {
    "url": wml_url,
    "apikey": wml_apikey
}

# Initialize IBM Watson ML client
wml_client = None
try:
    if wml_url and wml_apikey and wml_space_id:
        wml_client = APIClient(wml_credentials)
        wml_client.set.default_space(wml_space_id)
        print("✓ IBM Watson ML client initialized successfully")
    else:
        print("✗ IBM Watson ML credentials missing in .env file")
except Exception as e:
    print(f"✗ Warning: Could not initialize IBM Watson ML client: {e}")

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def analyze_prompt(prompt_text):
    """Analyze prompt and extract features for IBM Watson ML prediction (simplified version)"""
    
    # Word count
    words = prompt_text.split()
    word_count = len(words)
    
    # Sentence count (split by . ? !)
    sentences = re.split(r'[.?!]+', prompt_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(1, len(sentences))
    
    # Average word length
    avg_word_length = sum(len(word.strip(string.punctuation)) for word in words) / word_count if word_count > 0 else 0
    
    # Unique word count
    unique_words = set(word.lower().strip(string.punctuation) for word in words)
    unique_word_count = len(unique_words)
    
    # Average sentence length (in characters)
    avg_sentence_length = sum(len(s) for s in sentences) / sentence_count if sentence_count > 0 else 0
    
    # Punctuation count
    punctuation_count = sum(1 for char in prompt_text if char in string.punctuation)
    
    # Long word count (words with more than 6 characters)
    long_word_count = sum(1 for word in words if len(word.strip(string.punctuation)) > 6)
    
    # Verb count (simplified: words ending in common verb patterns)
    verb_patterns = ['ing', 'ed', 'ate', 'ize', 'ise']
    verb_count = sum(1 for word in words if any(word.lower().endswith(pattern) for pattern in verb_patterns))
    
    # Monosyllable count (simplified: words with no vowel clusters)
    monosyllable_count = sum(1 for word in words if len(re.findall(r'[aeiou]+', word.lower())) == 1)
    
    # Syllable count (approximation)
    syllable_count = sum(max(1, len(re.findall(r'[aeiou]+', word.lower()))) for word in words)
    
    # Character counts
    char_count = len(prompt_text)
    letter_count = sum(1 for c in prompt_text if c.isalpha())
    
    # Polysyllable count (words with 3+ vowel clusters)
    polysyllable_count = sum(1 for word in words if len(re.findall(r'[aeiou]+', word.lower())) >= 3)
    
    # Question and exclamation marks
    question_marks = prompt_text.count('?')
    exclamation_marks = prompt_text.count('!')
    
    # Word diversity
    word_diversity = unique_word_count / word_count if word_count > 0 else 0
    
    # Lexical diversity
    lexical_diversity = unique_word_count / word_count if word_count > 0 else 0
    
    # Lexicon count (total words including punctuation)
    lexicon_count = word_count
    
    # Derived features
    word_count_squared = word_count ** 2
    avg_sentence_length_cubed = avg_sentence_length ** 3
    
    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_word_length': round(avg_word_length, 2),
        'unique_word_count': unique_word_count,
        'avg_sentence_length': round(avg_sentence_length, 2),
        'punctuation_count': punctuation_count,
        'long_word_count': long_word_count,
        'verb_count': verb_count,
        'monosyllabcount': monosyllable_count,
        'syllable_count': syllable_count,
        'char_count': char_count,
        'letter_count': letter_count,
        'polysyllabcount': polysyllable_count,
        'question_marks': question_marks,
        'exclamation_marks': exclamation_marks,
        'word_diversity': round(word_diversity, 4),
        'lexical_diversity': round(lexical_diversity, 4),
        'lexicon_count': lexicon_count,
        'word_count_squared': word_count_squared,
        'avg_sentence_length_cubed': round(avg_sentence_length_cubed, 2)
    }

def predict_energy_ibm_wml(prompt_text, model, platform):
    """Predict energy consumption using IBM Watson ML with 88 features"""
    
    print(f"\n=== IBM Watson ML Prediction ===")
    print(f"Prompt: {prompt_text[:50]}...")
    print(f"Model: {model}, Platform: {platform}")
    
    # Analyze prompt
    prompt_features = analyze_prompt(prompt_text)
    print(f"Basic prompt features extracted")
    
    # Task flags - set to None instead of calculated values
    task_alpaca = None
    task_codefeedback = None
    
    # Model flags (one-hot encoding)
    model_flags = {
        'model_codellama_7b': 1 if model == 'codellama_7b' else 0,
        'model_codellama_70b': 1 if model == 'codellama_70b' else 0,
        'model_gemma_2b': 1 if model in ['gemma_2b', 'alpaca_gemma_2b'] else 0,
        'model_gemma_7b': 1 if model in ['gemma_7b', 'alpaca_gemma_7b'] else 0,
        'model_llama3_8b': 1 if model == 'alpaca_llama3_8b' else 0,
        'model_llama3_70b': 1 if model == 'alpaca_llama3_70b' else 0,
    }
    
    # Hardware flags (one-hot encoding)
    hardware_flags = {
        'hardware_laptop1': 1 if platform == 'laptop1' else 0,
        'hardware_laptop2': 1 if platform == 'laptop2' else 0,
        'hardware_workstation': 1 if platform == 'workstation' else 0,
        'hardware_server': 1 if platform == 'server' else 0,
    }
    
    # Build complete 88-feature vector following the exact order from the model schema
    # Features we don't calculate are set to None (null)
    features = [
        None,  # 1. model_name (integer)
        None,  # 2. created_at (other)
        None,  # 3. total_duration (double)
        None,  # 4. load_duration (double)
        None,  # 5. prompt_token_length (double)
        None,  # 6. prompt_duration (double)
        None,  # 7. response_token_length (double)
        None,  # 8. response_duration (double)
        prompt_text,  # 9. prompt (other)
        None,  # 10. response (other)
        None,  # 11. energy_consumption_monitoring (double)
        None,  # 12. energy_consumption_llm_cpu (double)
        None,  # 13. type (other)
        None,  # 14. clock_duration (other)
        None,  # 15. start_time (other)
        None,  # 16. end_time (other)
        None,  # 17. energy_consumption_llm (double)
        float(prompt_features['word_count']),  # 18. word_count (double)
        float(prompt_features['sentence_count']),  # 19. sentence_count (double)
        float(prompt_features['avg_word_length']),  # 20. avg_word_length (double)
        float(prompt_features['word_diversity']),  # 21. word_diversity (double)
        float(prompt_features['unique_word_count']),  # 22. unique_word_count (double)
        float(prompt_features['avg_sentence_length']),  # 23. avg_sentence_length (double)
        float(prompt_features['punctuation_count']),  # 24. punctuation_count (double)
        None,  # 25. stop_word_count (double)
        float(prompt_features['long_word_count']),  # 26. long_word_count (double)
        None,  # 27. named_entity_count (double)
        None,  # 28. noun_count (double)
        float(prompt_features['verb_count']),  # 29. verb_count (double)
        None,  # 30. adj_count (double)
        None,  # 31. adverb_count (double)
        None,  # 32. pronoun_count (double)
        None,  # 33. prop_adverbs (double)
        None,  # 34. prop_pronouns (double)
        None,  # 35. sentiment_polarity (double)
        None,  # 36. sentiment_subjectivity (double)
        None,  # 37. flesch_reading_ease (double)
        None,  # 38. flesch_kincaid_grade (double)
        None,  # 39. gunning_fog (double)
        None,  # 40. smog_index (double)
        None,  # 41. automated_readability_index (double)
        None,  # 42. coleman_liau_index (double)
        None,  # 43. linsear_write_formula (double)
        None,  # 44. dale_chall_readability_score (double)
        None,  # 45. text_standard (other)
        None,  # 46. spache_readability (double)
        None,  # 47. mcalpine_eflaw (double)
        None,  # 48. reading_time (double)
        None,  # 49. fernandez_huerta (double)
        None,  # 50. szigriszt_pazos (double)
        None,  # 51. gutierrez_polini (double)
        None,  # 52. crawford (double)
        None,  # 53. osman (double)
        None,  # 54. gulpease_index (double)
        None,  # 55. wiener_sachtextformel (double)
        float(prompt_features['syllable_count']),  # 56. syllable_count (double)
        float(prompt_features['lexicon_count']),  # 57. lexicon_count (double)
        float(prompt_features['char_count']),  # 58. char_count (double)
        float(prompt_features['letter_count']),  # 59. letter_count (double)
        float(prompt_features['polysyllabcount']),  # 60. polysyllabcount (double)
        float(prompt_features['monosyllabcount']),  # 61. monosyllabcount (double)
        float(prompt_features['question_marks']),  # 62. question_marks (double)
        float(prompt_features['exclamation_marks']),  # 63. exclamation_marks (double)
        None,  # 64. sentence_embedding_variance (double)
        None,  # 65. personal_pronouns (double)
        None,  # 66. named_entities (double)
        None,  # 67. adjectives (double)
        None,  # 68. adverbs (double)
        None,  # 69. length_x_complexity (double)
        None,  # 70. questions_about_entities (double)
        None,  # 71. desc_complexity_ratio (double)
        float(prompt_features['word_count_squared']),  # 72. word_count_squared (double)
        float(prompt_features['avg_sentence_length_cubed']),  # 73. avg_sentence_length_cubed (double)
        float(prompt_features['lexical_diversity']),  # 74. lexical_diversity (double)
        None,  # 75. energy_consumption_llm_gpu (double)
        task_alpaca,  # 76. task_alpaca (integer)
        task_codefeedback,  # 77. task_codefeedback (integer)
        model_flags['model_codellama_7b'],  # 78. model_codellama_7b (integer)
        model_flags['model_codellama_70b'],  # 79. model_codellama_70b (integer)
        model_flags['model_gemma_2b'],  # 80. model_gemma_2b (integer)
        model_flags['model_gemma_7b'],  # 81. model_gemma_7b (integer)
        model_flags['model_llama3_8b'],  # 82. model_llama3_8b (integer)
        model_flags['model_llama3_70b'],  # 83. model_llama3_70b (integer)
        hardware_flags['hardware_laptop1'],  # 84. hardware_laptop1 (integer)
        hardware_flags['hardware_laptop2'],  # 85. hardware_laptop2 (integer)
        hardware_flags['hardware_workstation'],  # 86. hardware_workstation (integer)
        hardware_flags['hardware_server'],  # 87. hardware_server (integer)
        f"{model}_{platform}"  # 88. original_filename (other)
    ]
    
    print(f"Feature vector created with {len(features)} features")
    
    # Call IBM Watson ML API
    try:
        if wml_client is None:
            print("ERROR: IBM Watson ML client is None!")
            raise Exception("IBM Watson ML client not initialized")
            
        payload = {
            "input_data": [{
                "values": [features]
            }]
        }
        
        print(f"Calling IBM Watson ML API...")
        deployment_id = os.getenv('IBM_WML_DEPLOYMENT_ID')
        print(f"Deployment ID: {deployment_id}")
        
        result = wml_client.deployments.score(deployment_id, payload)
        print(f"API Response: {result}")
        
        # Extract prediction (energy in kWh)
        predicted_energy_kwh = result['predictions'][0]['values'][0][0]
        print(f"✓ Predicted energy: {predicted_energy_kwh} kWh")
        print(f"=================================\n")
        
        return predicted_energy_kwh
        
    except Exception as e:
        print(f"✗ Error calling IBM Watson ML API: {e}")
        print(f"=================================\n")
        # Fallback to statistical method
        return None


def load_all_csv_files():
    """Load all CSV files from the data directory"""
    csv_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.csv')])  # Sort for deterministic order
    all_data = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, file))
            # Extract model and platform from filename
            filename = file.replace('.csv', '')
            parts = filename.split('_')
            
            # Parse filename based on patterns
            # Examples: 
            # - codefeedback_codellama_70b_workstation.csv
            # - alpaca_gemma_2b_laptop1.csv
            # - alpaca_llama3_70b_server.csv
            
            if 'codellama' in filename:
                # Format: [prefix]_codellama_[size]_[platform]
                idx = parts.index('codellama')
                model_name = 'codellama_' + parts[idx + 1]  # e.g., "codellama_7b"
                platform = parts[idx + 2]
            elif 'llama3' in filename:
                # Format: [prefix]_llama3_[size]_[platform]
                idx = parts.index('llama3')
                model_name = 'alpaca_llama3_' + parts[idx + 1]
                platform = parts[idx + 2]
            elif 'gemma' in filename:
                # Format: [prefix]_gemma_[size]_[platform]
                idx = parts.index('gemma')
                model_name = 'gemma_' + parts[idx + 1] if parts[0] != 'alpaca' else 'alpaca_gemma_' + parts[idx + 1]
                platform = parts[idx + 2]
            else:
                print(f"Skipping unknown format: {file}")
                continue
            
            # Add metadata
            df['model'] = model_name
            df['platform'] = platform
            df['source_file'] = file
            
            all_data.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    if all_data:
        df_combined = pd.concat(all_data, ignore_index=True)
        # Sort for deterministic order
        if 'model' in df_combined.columns:
            df_combined = df_combined.sort_values(by=['model', 'platform']).reset_index(drop=True)
        return df_combined
    return pd.DataFrame()

# Load data once at startup
print("Loading CSV data...")
df_all = load_all_csv_files()
print(f"Loaded {len(df_all)} rows from {df_all['source_file'].nunique()} files")

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'total_rows': len(df_all),
        'models': df_all['model'].unique().tolist() if not df_all.empty else [],
        'platforms': df_all['platform'].unique().tolist() if not df_all.empty else []
    })

@app.route('/api/energy-by-model', methods=['GET'])
def energy_by_model():
    """Get average energy consumption by model and platform"""
    if df_all.empty:
        return jsonify({'error': 'No data available'}), 500
    
    try:
        # Check if required column exists
        if 'energy_consumption_llm_total' not in df_all.columns:
            print(f"Available columns: {df_all.columns.tolist()}")
            return jsonify({'error': 'Missing energy_consumption_llm_total column'}), 500
        
        # Group by model and platform, calculate mean energy consumption (already in kWh)
        grouped = df_all.groupby(['model', 'platform'])['energy_consumption_llm_total'].mean().reset_index()
        
        # Pivot to get platforms as columns
        pivot = grouped.pivot(index='model', columns='platform', values='energy_consumption_llm_total').fillna(0)
        
        # Convert to format needed for frontend
        result = []
        for model in pivot.index:
            row = {'model': model}
            # Map platform names (case-insensitive matching)
            for col in pivot.columns:
                col_lower = col.lower()
                value = round(pivot.loc[model, col], 6)  # Keep more decimals since values are small
                
                if 'workstation' in col_lower:
                    row['Workstation'] = value
                elif 'server' in col_lower:
                    row['Server'] = value
                elif 'laptop1' in col_lower:
                    row['Laptop1'] = value
                elif 'laptop2' in col_lower:
                    row['Laptop2'] = value
            
            # Ensure all platforms exist (set to 0 if missing)
            for platform in ['Workstation', 'Server', 'Laptop1', 'Laptop2']:
                if platform not in row:
                    row[platform] = 0
            
            result.append(row)
        
        print(f"Returning {len(result)} models with energy data")
        return jsonify(result)
    
    except Exception as e:
        print(f"Error in energy_by_model: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify(result)

@app.route('/api/energy-timeline', methods=['GET'])
def energy_timeline():
    """Get energy consumption over time"""
    if df_all.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Sample data for timeline (take first N records from different configurations)
    sample_size = 6
    
    # Get sample data for different model-platform combinations using actual model names
    configs = [
        ('codellama_70b', 'workstation', 'CodeLlama_WS'),
        ('gemma_2b', 'laptop2', 'Gemma2B_L1'),
        ('alpaca_llama3_70b', 'server', 'Llama3_70B_S')
    ]
    
    result = []
    for i in range(sample_size):
        row = {'time': f"Sample {i+1}"}
        
        for model, platform, key in configs:
            filtered = df_all[(df_all['model'] == model) & (df_all['platform'] == platform)]
            if not filtered.empty and len(filtered) > i:
                row[key] = round(filtered.iloc[i]['energy_consumption_llm_total'], 6)
            else:
                row[key] = 0
        
        result.append(row)
    
    return jsonify(result[:sample_size])

@app.route('/api/gpu-cpu-distribution', methods=['GET'])
def gpu_cpu_distribution():
    """Get GPU vs CPU energy consumption by model (workstation GPU vs laptop1/server CPU)"""
    if df_all.empty:
        return jsonify({'error': 'No data available'}), 500
    
    result = []
    
    # Get all unique models
    models = df_all['model'].unique()
    
    for model in sorted(models):
        # Get GPU consumption from workstation (GPU-dominant platform)
        workstation_data = df_all[(df_all['model'] == model) & (df_all['platform'] == 'workstation')]
        
        # Get CPU consumption from laptop1 or server (CPU-dominant platforms)
        laptop1_data = df_all[(df_all['model'] == model) & (df_all['platform'] == 'laptop1')]
        server_data = df_all[(df_all['model'] == model) & (df_all['platform'] == 'server')]
        
        # Use laptop1 if available, otherwise server
        cpu_data = laptop1_data if not laptop1_data.empty else server_data
        
        # Only include models that have both workstation (GPU) and laptop1/server (CPU) data
        if not workstation_data.empty and not cpu_data.empty:
            gpu_energy = workstation_data['energy_consumption_llm_gpu'].mean()
            cpu_energy = cpu_data['energy_consumption_llm_cpu'].mean()
            
            # Format model name for display (remove prefixes, clean up)
            model_display = model.replace('alpaca_', '').replace('codefeedback_', '').replace('_', ' ')
            # Capitalize properly
            if 'gemma' in model_display:
                model_display = model_display.replace('gemma', 'Gemma')
            if 'llama3' in model_display:
                model_display = model_display.replace('llama3', 'Llama3')
            if 'codellama' in model_display:
                model_display = model_display.replace('codellama', 'CodeLlama')
            
            result.append({
                'model': model_display.strip().title(),
                'GPU': round(gpu_energy * 1000, 2),  # Convert to Wh
                'CPU': round(cpu_energy * 1000, 2)   # Convert to Wh
            })
    
    return jsonify(result)

@app.route('/api/energy-efficiency', methods=['GET'])
def energy_efficiency():
    """Get energy efficiency data (response length vs energy)"""
    if df_all.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Helper function to format model names for frontend
    def format_model_name(model):
        # Convert from "alpaca_gemma_2b" or "gemma_2b" to "Gemma 2B"
        # Convert from "codellama_70b" to "CodeLlama 70B"
        # Convert from "alpaca_llama3_8b" to "Llama3 8B"
        model_lower = model.lower()
        if 'gemma' in model_lower and '2b' in model_lower:
            return 'Gemma 2B'
        elif 'gemma' in model_lower and '7b' in model_lower:
            return 'Gemma 7B'
        elif 'llama3' in model_lower and '8b' in model_lower:
            return 'Llama3 8B'
        elif 'llama3' in model_lower and '70b' in model_lower:
            return 'Llama3 70B'
        elif 'codellama' in model_lower and '70b' in model_lower:
            return 'CodeLlama 70B'
        elif 'codellama' in model_lower and '7b' in model_lower:
            return 'CodeLlama 7B'
        else:
            return model
    
    # Log unique raw model names in data
    raw_models = df_all['model'].unique()
    print(f"\n=== Raw model names in data ===")
    for raw_model in raw_models:
        print(f"  - '{raw_model}'")
    print("=" * 40)
    
    # Sort dataframe for deterministic iteration
    df_sorted = df_all.sort_values(by=['model', 'energy_consumption_llm_total', 'word_count'])
    
    # Use all available data, no sampling
    result = []
    for _, row in df_sorted.iterrows():
        if pd.notna(row.get('word_count')) and pd.notna(row.get('energy_consumption_llm_total')):
            raw_model_name = row['model']
            formatted_name = format_model_name(raw_model_name)
            result.append({
                'responseLength': int(row['word_count']),
                'energy': round(row['energy_consumption_llm_total'], 6),
                'model': formatted_name,
                'duration': round(row.get('total_duration', 0) / 1e9, 1) if pd.notna(row.get('total_duration')) else 0
            })
    
    # Group by model and select many points for each model
    from collections import defaultdict
    models_data = defaultdict(list)
    for item in result:
        models_data[item['model']].append(item)
    
    print(f"\n=== Models found after formatting ===")
    for model_name in sorted(models_data.keys()):
        print(f"  - '{model_name}' with {len(models_data[model_name])} points")
    print("=" * 40)
    
    # Select up to 30 diverse points per model - in deterministic order
    # Filter to keep only Gemma 2B and Gemma 7B
    final_result = []
    target_models = ['Gemma 2B', 'Gemma 7B']
    for model in sorted(models_data.keys()):  # Sort model names for consistency
        if model not in target_models:
            continue  # Skip models that are not Gemma 2B or Gemma 7B
        points = models_data[model]
        # Sort by energy first, then by responseLength for stable sorting
        sorted_points = sorted(points, key=lambda x: (x['energy'], x['responseLength']))
        
        if len(sorted_points) <= 30:
            final_result.extend(sorted_points)
        else:
            # Take evenly distributed points
            step = len(sorted_points) / 30
            indices = [int(i * step) for i in range(30)]
            final_result.extend([sorted_points[i] for i in indices if i < len(sorted_points)])
    
    print(f"Total points returned: {len(final_result)}")
    for model in sorted(set(item['model'] for item in final_result)):
        count = len([item for item in final_result if item['model'] == model])
        model_points = [item for item in final_result if item['model'] == model]
        energies = [item['energy'] for item in model_points[:5]]  # First 5 energies
        print(f"  {model}: {count} points - First 5 energies: {energies}")
    
    return jsonify(final_result)

@app.route('/api/calculate-co2', methods=['POST'])
def calculate_co2():
    """Calculate CO2 for a specific prompt based on model, platform, and energy source using IBM Watson ML"""
    
    data = request.json
    model = data.get('model')
    platform = data.get('platform')
    energy_source = data.get('energy_source')
    prompt_text = data.get('prompt', '')
    
    print(f"\n>>> /api/calculate-co2 called")
    print(f"Model: {model}, Platform: {platform}, Energy: {energy_source}")
    print(f"Prompt: '{prompt_text}'")
    
    if not all([model, platform, energy_source, prompt_text]):
        print(f"ERROR: Missing parameters!")
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Energy source CO2 factors (g CO2/kWh)
    co2_factors = {
        'mix_france': 32,
        'nuclear': 6,
        'wind': 7,
        'solar': 41,
        'hydro': 6,
        'gas': 490,
        'coal': 820,
        'mix_eu': 275
    }
    
    co2_per_kwh = co2_factors.get(energy_source, 32)
    print(f"CO2 factor: {co2_per_kwh} g/kWh")
    
    # Try to predict energy using IBM Watson ML
    predicted_energy_kwh = predict_energy_ibm_wml(prompt_text, model, platform)
    
    # If IBM ML prediction fails, fallback to statistical method
    if predicted_energy_kwh is None:
        print("⚠ Fallback to statistical method")
        # Find similar prompts in the dataset
        filtered = df_all[(df_all['model'] == model) & (df_all['platform'] == platform)]
        
        if filtered.empty:
            # If no exact match, use average for the model
            filtered = df_all[df_all['model'] == model]
        
        if filtered.empty:
            # Fallback: use overall average
            predicted_energy_kwh = df_all['energy_consumption_llm_total'].mean()
        else:
            # Use average energy consumption for this configuration
            predicted_energy_kwh = filtered['energy_consumption_llm_total'].mean()
        
        print(f"Statistical prediction: {predicted_energy_kwh} kWh")
    
    # Calculate CO2 in grams (g CO2)
    # Formula: energy_kwh * co2_factor (g CO2/kWh) = g CO2
    co2_grams = predicted_energy_kwh * co2_per_kwh
    
    print(f"Final calculation: {predicted_energy_kwh} kWh × {co2_per_kwh} g/kWh = {co2_grams} g CO2")
    print(f"<<< Response sent\n")
    
    return jsonify({
        'co2_kg': round(co2_grams / 1000, 6),  # Pour compatibilité (sera converti en g dans le frontend)
        'co2_grams': round(co2_grams, 6),  # Valeur en grammes avec 6 décimales (pour précision en mg)
        'energy_kwh': round(predicted_energy_kwh, 6),
        'co2_per_kwh': co2_per_kwh,
        'energy_source': energy_source,
        'method': 'ibm_watson_ml' if predicted_energy_kwh is not None else 'statistical'
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models"""
    if df_all.empty:
        return jsonify([])
    
    models = df_all['model'].unique().tolist()
    return jsonify(sorted(models))

@app.route('/api/platforms/<model>', methods=['GET'])
def get_platforms_for_model(model):
    """Get available platforms for a specific model"""
    if df_all.empty:
        return jsonify([])
    
    platforms = df_all[df_all['model'] == model]['platform'].unique().tolist()
    return jsonify(sorted(platforms))

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Available models: {df_all['model'].unique().tolist()}")
    print(f"Available platforms: {df_all['platform'].unique().tolist()}")
    app.run(debug=False, port=5000, host='0.0.0.0')

