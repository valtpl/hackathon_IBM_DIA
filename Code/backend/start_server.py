import sys
import traceback

try:
    print("Starting backend server...")
    from main import app
    print("App imported successfully")
    print("Starting Flask...")
    app.run(debug=False, port=5000, host='0.0.0.0', use_reloader=False)
except Exception as e:
    print(f"\n\nERROR STARTING SERVER:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n\nPress Enter to exit...")
    input()
