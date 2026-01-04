"""
Simple API Server Starter
Runs the Flask server with proper error handling
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "="*70)
print("  NAVIGATION ASSISTANT API SERVER")
print("="*70)
print("\n⚙️  Starting server... (Press Ctrl+C to stop)\n")

try:
    # Import and run
    from api.server import app
    print("✅ App imported successfully\n")
    print("="*70)
    print("  SERVER IS RUNNING")
    print("="*70)
    print("\n🌐 Access in your browser:")
    print("   http://127.0.0.1:5000/health")
    print("   http://127.0.0.1:5000/test")
    print("\n📱 For mobile app, use this IP:")
    print("   http://192.168.1.7:5000")
    print("\n⚠️  KEEP THIS WINDOW OPEN - Server is running...")
    print("="*70 + "\n")
    
    # Run server (blocks here until Ctrl+C)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
    
except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("  ✅ Server stopped by user")
    print("="*70 + "\n")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
