#!/usr/bin/env python3
"""
Script to inspect Excel files and understand their structure
"""

import pandas as pd
from pathlib import Path
import sys

def inspect_excel_file(file_path):
    """Inspect the contents of an Excel file"""
    try:
        print(f"\n🔍 Inspecting: {file_path.name}")
        print("=" * 50)
        
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name="data")
        
        print(f"📊 Sheet: 'data'")
        print(f"📏 Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"🏷️  Columns: {list(df.columns)}")
        
        # Show first few rows
        print(f"\n📋 First 5 rows:")
        print(df.head().to_string(index=False))
        
        # Check for duplicates
        if 'Ürün Adı' in df.columns:
            product_counts = df['Ürün Adı'].value_counts()
            duplicates = product_counts[product_counts > 1]
            
            if not duplicates.empty:
                print(f"\n⚠️  Duplicate products found:")
                for product, count in duplicates.items():
                    print(f"   • {product}: {count} times")
                    
                # Show the duplicate rows
                print(f"\n📋 Duplicate rows:")
                for product in duplicates.index:
                    duplicate_rows = df[df['Ürün Adı'] == product]
                    print(f"\n   {product} (appears {len(duplicate_rows)} times):")
                    for idx, row in duplicate_rows.iterrows():
                        print(f"     Row {idx+1}: {row.to_dict()}")
            else:
                print(f"\n✅ No duplicate products found")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error reading {file_path.name}: {e}")

def main():
    """Main function"""
    print("🔍 Excel File Inspector")
    print("=" * 60)
    
    # Excel files to inspect
    excel_files = [
        Path("27.08.2025.xlsx"),
        Path("28.08.2025.xlsx"),
        Path("29.08.2025.xlsx")
    ]
    
    for excel_file in excel_files:
        if excel_file.exists():
            inspect_excel_file(excel_file)
        else:
            print(f"❌ {excel_file.name} not found")

if __name__ == "__main__":
    main()
