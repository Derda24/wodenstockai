#!/usr/bin/env python3

from app.services.supabase_service import SupabaseService
import json

def test_supabase_integration():
    print("=== Testing Supabase Integration ===")
    
    try:
        # Initialize service
        service = SupabaseService()
        print("✅ Supabase service initialized")
        
        # Test stock data
        stock_data = service.get_flat_stock_list()
        print(f"✅ Stock data: {len(stock_data)} items")
        
        # Test sales data
        sales_data = service.get_sales_data(7)
        print(f"✅ Sales data: {sales_data['total_sales']} total sales")
        print(f"✅ Top products: {len(sales_data['top_products'])} products")
        print(f"✅ Daily trends: {len(sales_data['daily_trends'])} days")
        print(f"✅ Categories: {len(sales_data['category_breakdown'])} categories")
        
        # Test recent sales records
        recent_sales = service.client.table('sales_history').select('*').order('created_at', desc=True).limit(3).execute()
        print(f"✅ Recent sales records: {len(recent_sales.data)} found")
        
        for i, record in enumerate(recent_sales.data):
            items = json.loads(record['items_sold'])
            print(f"   Record {i+1}: Date={record['date']}, Total={record['total_sales']}, Items={len(items)}")
        
        print("\n🎉 Supabase integration is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_integration()
