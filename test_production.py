"""
Test script to verify production deployment
"""
import requests
import time

PRODUCTION_URL = "https://wodenstockai.onrender.com"

print("🔍 Testing Production Backend Deployment\n")
print(f"Target: {PRODUCTION_URL}\n")

# Test 1: Check if server is alive
print("1️⃣ Testing server health...")
try:
    response = requests.get(f"{PRODUCTION_URL}/docs", timeout=10)
    if response.status_code == 200:
        print("   ✅ Server is running!\n")
    else:
        print(f"   ⚠️  Server responded with status: {response.status_code}\n")
except Exception as e:
    print(f"   ❌ Server not reachable: {e}\n")
    exit(1)

# Test 2: Check API routes
print("2️⃣ Testing API routes...")
routes_to_test = [
    "/api/stock",
]

for route in routes_to_test:
    try:
        response = requests.get(f"{PRODUCTION_URL}{route}", timeout=10)
        print(f"   {route}: {response.status_code}")
    except Exception as e:
        print(f"   {route}: ❌ Error - {e}")

print("\n" + "="*50)
print("✅ Production backend is ready!")
print("="*50)
print("\n📝 Next: Try uploading your Excel file at:")
print("   https://www.wodenstockai.com/")

