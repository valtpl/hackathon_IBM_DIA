"""Test IBM Watson ML API to check expected features"""
import os
from dotenv import load_dotenv
from ibm_watson_machine_learning import APIClient

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Get credentials
wml_url = os.getenv('IBM_WML_URL')
wml_apikey = os.getenv('IBM_WML_APIKEY')
wml_space_id = os.getenv('IBM_WML_SPACE_ID')
wml_deployment_id = os.getenv('IBM_WML_DEPLOYMENT_ID')

print("=== IBM Watson ML Configuration ===")
print(f"URL: {wml_url}")
print(f"API Key: {wml_apikey[:20]}...")
print(f"Space ID: {wml_space_id}")
print(f"Deployment ID: {wml_deployment_id}")

# Initialize client
wml_credentials = {
    "url": wml_url,
    "apikey": wml_apikey
}

try:
    wml_client = APIClient(wml_credentials)
    wml_client.set.default_space(wml_space_id)
    print("\n✓ IBM Watson ML client initialized successfully")
    
    # Get deployment details
    print("\n=== Deployment Details ===")
    deployment_details = wml_client.deployments.get_details(wml_deployment_id)
    print(f"Deployment name: {deployment_details.get('entity', {}).get('name', 'N/A')}")
    print(f"Status: {deployment_details.get('entity', {}).get('status', {}).get('state', 'N/A')}")
    
    # Get model details
    model_id = deployment_details.get('entity', {}).get('asset', {}).get('id')
    if model_id:
        print(f"\nModel ID: {model_id}")
        try:
            model_details = wml_client.repository.get_model_details(model_id)
            print("\n=== Model Details ===")
            
            # Try to get input schema
            if 'entity' in model_details:
                entity = model_details['entity']
                
                # Check for schema information
                if 'schemas' in entity:
                    schemas = entity['schemas']
                    print(f"\nSchemas found: {schemas.keys()}")
                    
                    if 'input' in schemas:
                        input_schema = schemas['input']
                        print(f"\n=== Input Schema ===")
                        print(f"Input schema: {input_schema}")
                        
                        # Try to get field count
                        if isinstance(input_schema, list) and len(input_schema) > 0:
                            fields = input_schema[0].get('fields', [])
                            print(f"\nNumber of input features expected: {len(fields)}")
                            print(f"\nFeature names:")
                            for i, field in enumerate(fields, 1):
                                print(f"  {i}. {field.get('name', 'N/A')} ({field.get('type', 'N/A')})")
                
                # Check for training data reference
                if 'training_data_references' in entity:
                    print(f"\nTraining data references: {entity['training_data_references']}")
                    
        except Exception as e:
            print(f"\n⚠ Could not get model details: {e}")
    
    # Test with different feature counts
    print("\n\n=== Testing Different Feature Counts ===")
    
    for num_features in [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10]:
        test_features = [1.0] * num_features
        payload = {
            "input_data": [{
                "values": [test_features]
            }]
        }
        
        try:
            print(f"\nTrying {num_features} features...")
            result = wml_client.deployments.score(wml_deployment_id, payload)
            print(f"✓ SUCCESS with {num_features} features!")
            print(f"Response: {result}")
            break
        except Exception as e:
            error_msg = str(e)
            if "Number of features" in error_msg:
                print(f"✗ Failed with {num_features} features")
            else:
                print(f"✗ Different error with {num_features} features: {error_msg[:100]}")
                
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
