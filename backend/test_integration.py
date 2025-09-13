#!/usr/bin/env python3

import requests
import json

def test_complete_integration():
    print("=== Testing Complete Integration ===")
    
    try:
        # Test backend API
        print("1. Testing Backend API...")
        response = requests.get("http://localhost:8000/api/analysis?period=7d")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend API working: {data['totalSales']} total sales")
            print(f"   ✅ Top products: {len(data['topProducts'])} items")
            print(f"   ✅ Low stock alerts: {len(data['lowStockAlerts'])} items")
            print(f"   ✅ Categories: {len(data['categoryBreakdown'])} categories")
        else:
            print(f"   ❌ Backend API failed: {response.status_code}")
            return False
        
        # Test frontend
        print("\n2. Testing Frontend...")
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
        else:
            print(f"   ❌ Frontend failed: {response.status_code}")
            return False
        
        # Test CORS
        print("\n3. Testing CORS...")
        headers = {"Origin": "http://localhost:3000"}
        response = requests.get("http://localhost:8000/api/analysis?period=7d", headers=headers)
        if response.status_code == 200:
            print("   ✅ CORS is working")
        else:
            print(f"   ❌ CORS failed: {response.status_code}")
            return False
        
        print("\n🎉 Complete integration is working!")
        print("\n📊 Data Summary:")
        print(f"   - Total Sales: {data['totalSales']}")
        print(f"   - Top Product: {data['topProducts'][0]['name']} ({data['topProducts'][0]['percentage']}%)")
        print(f"   - Low Stock Items: {len(data['lowStockAlerts'])}")
        print(f"   - Categories: {[cat['category'] for cat in data['categoryBreakdown']]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_complete_integration()
