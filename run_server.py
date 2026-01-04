"""
KEEP-ALIVE API Server
Forces the server to stay running
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.server import app
import threading
import time

print("\n" + "="*70)
print("  🚀 NAVIGATION ASSISTANT API SERVER - STAY ALIVE MODE")
print("="*70 + "\n")

def keep_alive():
    """Keep the main thread alive"""
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n✅ Shutting down...")
        os._exit(0)

# Start server in a thread
def run_server():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)

print("⚙️  Starting Flask server thread...")
server_thread = threading.Thread(target=run_server, daemon=False)
server_thread.start()

# Wait for server to start
time.sleep(3)

print("\n" + "="*70)
print("  ✅ SERVER IS RUNNING AND WILL STAY ALIVE")
print("="*70)
print("\n🌐 Open in your browser:")
print("   http://127.0.0.1:5000/health")
print("   http://127.0.0.1:5000/test")
print("\n📱 For mobile app:")
print("   http://192.168.1.7:5000")
print("\n⚠️  Press Ctrl+C to stop the server")
print("="*70 + "\n")

# Keep main thread alive
keep_alive()
