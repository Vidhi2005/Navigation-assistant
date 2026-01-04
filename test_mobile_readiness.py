"""
MOBILE APP TEST - Check if Node.js and dependencies are ready
"""

import subprocess
import os
import sys

print("="*60)
print("MOBILE APP READINESS CHECK")
print("="*60)

mobile_app_path = r"C:\Users\agraw\Desktop\navigation-assistant\mobile_app"

# Test 1: Check if mobile_app directory exists
print("\n[1/4] Checking mobile_app directory...")
if os.path.exists(mobile_app_path):
    print(f"  ✅ Found: {mobile_app_path}")
else:
    print(f"  ❌ Not found: {mobile_app_path}")
    sys.exit(1)

# Test 2: Check if package.json exists
print("\n[2/4] Checking package.json...")
package_json = os.path.join(mobile_app_path, "package.json")
if os.path.exists(package_json):
    print("  ✅ package.json exists")
    with open(package_json, 'r') as f:
        import json
        pkg = json.load(f)
        print(f"  📱 App name: {pkg.get('name', 'N/A')}")
        print(f"  📦 Dependencies: {len(pkg.get('dependencies', {}))} packages")
else:
    print("  ❌ package.json not found")
    sys.exit(1)

# Test 3: Check if Node.js is installed
print("\n[3/4] Checking Node.js...")
try:
    result = subprocess.run(['node', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ Node.js installed: {result.stdout.strip()}")
    else:
        print("  ❌ Node.js not found")
except:
    print("  ❌ Node.js not installed")
    print("\n  📥 Install from: https://nodejs.org/")

# Test 4: Check if npm is installed
print("\n[4/4] Checking npm...")
try:
    result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ npm installed: {result.stdout.strip()}")
    else:
        print("  ❌ npm not found")
except:
    print("  ❌ npm not installed")

print("\n" + "="*60)
print("NEXT STEPS FOR MOBILE APP")
print("="*60)
print("\n1. Install dependencies:")
print("   cd mobile_app")
print("   npm install")
print("\n2. Configure API endpoint:")
print("   Edit: mobile_app/src/services/APIService.js")
print("   Change: const API_BASE_URL = 'http://YOUR_IP:5000'")
print("   Find your IP: ipconfig")
print("\n3. Run on Android:")
print("   npm run android")
print("\n4. Or run on iOS (Mac only):")
print("   npm run ios")
print("\n" + "="*60)
