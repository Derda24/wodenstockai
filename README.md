# 🚀 **Woden AI Stock Management System**

A comprehensive, AI-powered stock management system designed specifically for coffee shops and cafes. This system automatically manages raw materials inventory based on recipe-based products and daily sales data.

## ✨ **Key Features**

### 🏗️ **Complete Stock Management**
- **Raw Materials Tracking**: Coffee beans, milk, syrups, cups, napkins, etc.
- **Recipe-Based System**: Automatic ingredient consumption when products are sold
- **Real-Time Updates**: Live stock levels with automatic decrements
- **Stock Alerts**: Low stock and out-of-stock notifications

### 📊 **Smart Inventory Control**
- **Automatic Stock Updates**: Upload daily sales Excel → automatic ingredient consumption
- **Recipe Integration**: Products linked to ingredient requirements
- **Daily Consumables**: Automatic processing of napkins, garbage bags, etc.
- **Stock Analytics**: Comprehensive reporting and insights

### 🔐 **Secure Access**
- **Admin-Only Access**: Restricted to authorized personnel
- **User Management**: Multiple admin accounts supported
- **Audit Trail**: Track all stock changes and updates

## 🏗️ **System Architecture**

### **Backend (Python FastAPI)**
- **Stock Manager**: Core inventory management engine
- **Recipe Engine**: Product-to-ingredient mapping system
- **Excel Processor**: Daily sales file upload and processing
- **REST API**: Full-featured API for frontend integration

### **Frontend (Next.js + Tailwind CSS)**
- **Modern UI**: Beautiful, responsive interface
- **Real-Time Updates**: Live stock monitoring
- **File Upload**: Drag-and-drop Excel file processing
- **Dashboard**: Comprehensive overview and analytics

### **Data Storage**
- **JSON-Based**: Lightweight, fast, and portable
- **Stock Data**: `sample_stock.json` - Complete inventory
- **Recipes**: `recipes.json` - Product ingredient mappings

## 🚀 **Quick Start**

### **1. Start Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend will run on: `http://localhost:8000`

### **2. Start Frontend**
```bash
cd frontend
npm install
npm run dev
```
Frontend will run on: `http://localhost:3000`

### **3. Access System**
- **URL**: `http://localhost:3000`
- **Login**: Use admin credentials
- **Upload**: Daily sales Excel files
- **Monitor**: Real-time stock levels

## 📁 **File Structure**

```
woden_ai_stock/
├── backend/
│   ├── app/
│   │   └── stock_manager.py      # Core stock management
│   ├── main.py                   # FastAPI application
│   ├── sample_stock.json         # Stock data
│   ├── recipes.json              # Product recipes
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── app/                      # Next.js pages
│   ├── components/               # React components
│   └── package.json             # Node.js dependencies
└── README.md                     # This file
```

## 🔐 **Login Credentials**

### **Admin Users**
- **Username**: `derda2412` | **Password**: `woden2025`
- **Username**: `caner0119` | **Password**: `stock2025`

## 📊 **Stock Categories**

### **Raw Materials**
- **Kahve Çekirdeği**: Espresso, Filtre, Türk Kahvesi
- **Süt Türleri**: Torku Süt, Laktozsuz, Badem, Soya, Yulaf
- **Şurup & Püreler**: Vanilya, Badem, Fındık, Cookie, Çilek, etc.
- **Bardak & Kapaklar**: Small, Medium, Ice sizes
- **Kullan At Ürünleri**: Peçete, Pipet, Çöp Torbası, etc.

### **Ready-Made Products**
- **Beverages**: SU, Soda, Limonata
- **Supplies**: Buz, Limon, Filtre Kağıdı
- **Packaging**: Poşet, Kraft Çanta

## 🍳 **Recipe System**

### **Recipe-Based Products**
- **AMERICANO**: Coffee beans + Water + Cup + Lid
- **LATTE**: Coffee beans + Milk + Cup + Lid
- **CAPPUCCINO**: Coffee beans + Milk + Cup + Lid
- **TÜRK KAHVESİ**: Turkish coffee beans + Water

### **Ready-Made Products**
- **POĞAÇA**: No ingredients consumed
- **PROFITEROL**: No ingredients consumed
- **CHEESECAKE**: No ingredients consumed

## 📈 **How It Works**

### **1. Daily Sales Upload**
- Upload Excel file with daily sales
- System identifies each product sold
- Automatically calculates ingredient requirements

### **2. Automatic Stock Updates**
- **Recipe Products**: Consume ingredients based on recipes
- **Ready-Made**: No ingredient consumption
- **Daily Items**: Automatic napkin, garbage bag usage

### **3. Stock Monitoring**
- Real-time inventory levels
- Low stock alerts
- Out-of-stock notifications
- Stock recommendations

## 🔧 **API Endpoints**

### **Stock Management**
- `GET /api/stock` - Get current stock list
- `POST /api/stock/update` - Update stock manually
- `GET /api/summary` - Stock summary statistics

### **Sales Processing**
- `POST /api/sales/upload` - Upload daily sales Excel
- `GET /api/analysis` - Stock analysis data
- `GET /api/recommendations` - Stock recommendations

### **Monitoring**
- `GET /api/alerts` - Current stock alerts
- `GET /api/campaigns` - Marketing suggestions

## 📊 **Excel File Format**

### **Required Columns**
```csv
Product,Quantity,Date
AMERICANO,5,2025-01-27
LATTE,3,2025-01-27
ESPRESSO,2,2025-01-27
```

### **Supported Formats**
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

## 🚨 **Stock Alerts**

### **Alert Types**
- **Low Stock**: Below minimum threshold
- **Out of Stock**: Zero inventory
- **Daily Consumption**: Fixed daily usage items

### **Alert Actions**
- Immediate restock recommendations
- Priority-based action items
- Stock level monitoring

## 🔮 **Future Enhancements**

### **AI-Powered Features**
- **Demand Forecasting**: Predict future stock needs
- **Smart Reordering**: Automatic purchase suggestions
- **Cost Optimization**: Minimize waste and costs
- **Trend Analysis**: Sales pattern recognition

### **Advanced Analytics**
- **Profit Margins**: Ingredient cost tracking
- **Waste Analysis**: Expired/unsold product tracking
- **Supplier Management**: Vendor performance metrics
- **Seasonal Trends**: Holiday and weather impact

## 🛠️ **Technical Details**

### **Backend Technologies**
- **Python 3.9+**: Core application logic
- **FastAPI**: High-performance web framework
- **Pandas**: Excel file processing
- **OpenPyXL**: Excel file handling

### **Frontend Technologies**
- **Next.js 13**: React framework
- **Tailwind CSS**: Utility-first CSS
- **TypeScript**: Type-safe development
- **Lucide React**: Icon library

### **Data Processing**
- **JSON Storage**: Fast, portable data format
- **Recipe Engine**: Flexible ingredient mapping
- **Stock Calculations**: Real-time inventory math
- **Error Handling**: Comprehensive validation

## 📞 **Support & Contact**

### **System Requirements**
- **Python**: 3.9 or higher
- **Node.js**: 16 or higher
- **Memory**: 4GB RAM minimum
- **Storage**: 1GB free space

### **Browser Support**
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 🎯 **Business Benefits**

### **Operational Efficiency**
- **Automated Stock Management**: No manual calculations
- **Real-Time Visibility**: Always know your inventory
- **Reduced Waste**: Precise ingredient tracking
- **Faster Service**: Quick stock level checks

### **Cost Control**
- **Ingredient Optimization**: Minimize over-purchasing
- **Waste Reduction**: Track expiration and usage
- **Supplier Management**: Better negotiation leverage
- **Profit Tracking**: Cost-per-product analysis

### **Customer Experience**
- **Consistent Quality**: Proper ingredient availability
- **Faster Service**: No stock-out delays
- **Menu Reliability**: Accurate product availability
- **Professional Image**: Organized inventory management

---

## 🚀 **Ready to Transform Your Stock Management?**

This system represents the future of cafe inventory management. With AI-powered insights, automated stock updates, and comprehensive monitoring, you'll never worry about running out of ingredients again.

**Start managing your stock like a pro today!** 🎉
