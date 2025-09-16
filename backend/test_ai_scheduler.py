"""
Test script for AI Scheduler functionality
"""

import requests
import json
from datetime import datetime, date, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "test_token_123"  # You'll need to get a real token

def test_baristas_endpoint():
    """Test the baristas GET endpoint"""
    print("Testing baristas endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/baristas")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} baristas")
            for barista in data[:3]:  # Show first 3
                print(f"  - {barista.get('name', 'Unknown')} ({barista.get('type', 'unknown')})")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing baristas endpoint: {e}")

def test_schedules_endpoint():
    """Test the schedules GET endpoint"""
    print("\nTesting schedules endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/schedules")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} schedules")
            for schedule in data[:2]:  # Show first 2
                print(f"  - Week {schedule.get('week_start')} to {schedule.get('week_end')} ({schedule.get('status')})")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing schedules endpoint: {e}")

def test_generate_schedule():
    """Test the AI schedule generation endpoint"""
    print("\nTesting AI schedule generation...")
    
    try:
        # Get current week start (Monday)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        form_data = {
            'week_start': week_start.isoformat()
        }
        
        headers = {
            'Authorization': f'Bearer {TEST_TOKEN}'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schedules/generate",
            data=form_data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Schedule generated successfully!")
            print(f"  - Schedule ID: {data.get('schedule_id')}")
            print(f"  - Baristas: {data.get('baristas_count')}")
            print(f"  - Shifts: {data.get('shifts_count')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing schedule generation: {e}")

if __name__ == "__main__":
    print("AI Scheduler API Test")
    print("=" * 50)
    
    # Test endpoints
    test_baristas_endpoint()
    test_schedules_endpoint()
    test_generate_schedule()
    
    print("\nTest completed!")
