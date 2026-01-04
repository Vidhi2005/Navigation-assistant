"""
Production-ready server
Keeps server running stable
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.server import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 NAVIGATION ASSISTANT API SERVER")
    print("="*70 + "\n")
    
    print("🌐 Server URLs:")
    print("   http://127.0.0.1:5000")
    print("   http://192.168.1.7:5000")
    print("\n📱 Open in browser to see the dashboard!")
    print("⚠️  Press Ctrl+C to stop")
    print("\n" + "="*70 + "\n")
    
    try:
        # Use Flask with threading
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")
