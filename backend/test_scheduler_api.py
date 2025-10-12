#!/usr/bin/env python3
"""
Test AI Scheduler API endpoint
"""

import requests
import json
from datetime import datetime, timedelta

def test_scheduler_api():
    """Test the scheduler API endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/api/schedules/generate"
    
    # Test data
    week_start = datetime.now().strftime("%Y-%m-%d")
    
    # Sample preferences
    preferences = {
        "1": {  # Derda
            "dayOff": 6,  # Pazar
            "preferredOpening": [0, 1],  # Pazartesi, Salı
            "preferredClosing": [2, 3]   # Çarşamba, Perşembe
        },
        "2": {  # Ahmet
            "dayOff": 4,  # Cuma
            "preferredOpening": [0, 1, 2],  # Pazartesi, Salı, Çarşamba
            "preferredClosing": [5, 6]   # Cumartesi, Pazar
        },
        "3": {  # İlker
            "dayOff": 1,  # Salı
            "preferredOpening": [2, 3],  # Çarşamba, Perşembe
            "preferredClosing": [4, 5]   # Cuma, Cumartesi
        }
    }
    
    # Prepare form data
    data = {
        'week_start': week_start,
        'preferences': json.dumps(preferences)
    }
    
    print(f"🧪 Testing AI Scheduler API...")
    print(f"📅 Week Start: {week_start}")
    print(f"👥 Preferences: {len(preferences)} baristas")
    
    try:
        # Make request
        response = requests.post(url, data=data, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📋 Schedule ID: {result.get('schedule_id', 'N/A')}")
            print(f"📅 Week: {result.get('week_start', 'N/A')} - {result.get('week_end', 'N/A')}")
            print(f"🔄 Shifts: {len(result.get('shifts', []))}")
            
            # Show sample shifts
            shifts = result.get('shifts', [])
            if shifts:
                print(f"\n📝 Sample Shifts:")
                for i, shift in enumerate(shifts[:5]):  # Show first 5
                    print(f"  {i+1}. {shift.get('shift_type', 'unknown')} - Day {shift.get('day_of_week', '?')} - {shift.get('barista_id', 'unknown')}")
            
            # Show full schedule if available
            if 'schedule' in result:
                schedule = result['schedule']
                print(f"\n📅 Schedule Keys: {list(schedule.keys())}")
                if 'schedule' in schedule:
                    weekly_schedule = schedule['schedule']
                    print(f"📅 Weekly Schedule Keys: {list(weekly_schedule.keys())}")
                    for day, day_schedule in weekly_schedule.items():
                        print(f"  {day}:")
                        print(f"    Keys: {list(day_schedule.keys())}")
                        if isinstance(day_schedule, dict):
                            for shift_type, shifts_list in day_schedule.items():
                                if isinstance(shifts_list, list):
                                    if shifts_list:
                                        names = [s.get('employee', 'unknown') if isinstance(s, dict) else str(s) for s in shifts_list]
                                        print(f"    {shift_type}: {', '.join(names)}")
                                    else:
                                        print(f"    {shift_type}: []")
                                else:
                                    print(f"    {shift_type}: {shifts_list}")
                        else:
                            print(f"    Data: {day_schedule}")
            
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running!")
        print("💡 Start backend with: python main.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_scheduler_api()
