"""
ROBUST API SERVER - Won't exit until you manually stop it
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Disable some signals that might cause early exit
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from api.server import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 NAVIGATION ASSISTANT API SERVER")
    print("="*70 + "\n")
    
    try:
        print("⚙️  Starting Flask server...\n")
        
        # Run with proper settings
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
