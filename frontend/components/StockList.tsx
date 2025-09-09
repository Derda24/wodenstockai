'use client';

import { useState, useEffect } from 'react';
import { Plus, Minus, Search, Upload, RefreshCw, AlertTriangle, Calendar } from 'lucide-react';

interface StockItem {
  id: string;
  name: string;
  category: string;
  current_stock: number;
  min_stock: number;
  unit: string;
  package_size?: number;
  package_unit?: string;
  cost_per_unit?: number;
  is_ready_made?: boolean;
  usage_per_order?: number;
  usage_per_day?: number;
  usage_type?: string;
  can_edit: boolean;
  edit_reason: string;
  edit_message: string;
}

interface StockResponse {
  stock_data: StockItem[];
  total_items: number;
}

export default function StockList() {
  const [stockData, setStockData] = useState<StockItem[]>([]);
  const [filteredData, setFilteredData] = useState<StockItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [uploadMessage, setUploadMessage] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Get unique categories for filter
  const categories = ['All Categories', ...Array.from(new Set(stockData.map((item: StockItem) => item.category)))];

  const loadStockData = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://wodenstockai.onrender.com/api/stock');
      if (response.ok) {
        const data: StockResponse = await response.json();
        console.log('=== Stock data loaded ===');
        console.log('Raw data:', data);
        console.log('Stock items:', data.stock_data?.map(item => ({ 
          id: item.id, 
          name: item.name, 
          category: item.category, 
          can_edit: item.can_edit,
          current_stock: item.current_stock 
        })));
        setStockData(data.stock_data || []);
        setFilteredData(data.stock_data || []);
      } else {
        console.error('Failed to fetch stock data');
      }
    } catch (error) {
      console.error('Error loading stock data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStockData();
  }, []);

  useEffect(() => {
    let filtered = stockData;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter((item: StockItem) =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply category filter
    if (selectedCategory !== 'All Categories') {
      filtered = filtered.filter((item: StockItem) => item.category === selectedCategory);
    }

    setFilteredData(filtered);
  }, [searchTerm, selectedCategory, stockData]);

  const updateStock = async (itemId: string, change: number) => {
    console.log('=== updateStock called ===');
    console.log('itemId:', itemId);
    console.log('change:', change);
    console.log('Available items:', stockData.map(i => ({ id: i.id, name: i.name, can_edit: i.can_edit })));
    
    try {
      const item = stockData.find(i => i.id === itemId);
      console.log('Found item:', item);
      
      if (!item) {
        console.error('Item not found:', itemId);
        alert('Item not found in local data');
        return;
      }

      // Check if item can be edited
      console.log('Item can_edit:', item.can_edit);
      if (!item.can_edit) {
        console.log('Item cannot be edited, showing alert');
        alert(`Cannot edit ${item.name}: ${item.edit_reason || 'Editing is disabled'}`);
        return;
      }

      const newStock = Math.max(0, item.current_stock + change);
      
      console.log(`Updating stock for ${item.name}:`, {
        itemId,
        currentStock: item.current_stock,
        change,
        newStock,
        canEdit: item.can_edit
      });
      
      const formData = new FormData();
      formData.append('material_id', itemId);
      formData.append('new_stock', newStock.toString());
      formData.append('reason', change > 0 ? 'stock_added' : 'stock_used');

      const token = localStorage.getItem('authToken');
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      console.log('Sending request with headers:', headers);

      const response = await fetch('https://wodenstockai.onrender.com/api/stock/update', {
        method: 'POST',
        headers,
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const result = await response.json();
        console.log('Update successful:', result);
        
        // Update local state
        setStockData((prev: StockItem[]) => prev.map((item: StockItem) => 
          item.id === itemId 
            ? { ...item, current_stock: newStock }
            : item
        ));
        
        // Show success message
        alert(`Stock updated successfully for ${item.name}! New stock: ${newStock} ${item.unit}`);
      } else {
        const errorData = await response.json();
        console.error('Update failed:', errorData);
        alert(`Failed to update stock: ${errorData.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error updating stock:', error);
      alert(`Error updating stock: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const removeStockItem = async (itemName: string) => {
    try {
      if (!confirm(`Are you sure you want to remove "${itemName}" from the stock list?`)) {
        return;
      }

      const formData = new FormData();
      formData.append('item_name', itemName);

      const token = localStorage.getItem('authToken');
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('https://wodenstockai.onrender.com/api/stock/remove', {
        method: 'POST',
        headers,
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        // Reload stock data to reflect the removal
        loadStockData();
      } else {
        const errorData = await response.json();
        alert(errorData.message || 'Failed to remove item');
      }
    } catch (error) {
      console.error('Error removing stock item:', error);
      alert('Error removing stock item. Please try again.');
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      console.log('No file selected');
      setUploadMessage('No file selected');
      return;
    }

    console.log('Uploading file:', selectedFile.name, 'Size:', selectedFile.size);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    const token = localStorage.getItem('authToken');
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      console.log('Sending request to backend...');
      const response = await fetch('https://wodenstockai.onrender.com/api/sales/upload', {
        method: 'POST',
        headers,
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (response.ok) {
        const result = await response.json();
        console.log('Upload successful:', result);
        setUploadMessage(result.message);
        setShowUploadModal(false);
        setSelectedFile(null);
        
        // Reload stock data to show updates
        setTimeout(() => {
          loadStockData();
          setUploadMessage('');
        }, 3000);
      } else {
        const error = await response.json();
        console.error('Upload failed:', error);
        setUploadMessage(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadMessage('Error uploading file');
    }
  };

  const handleDailyConsumption = async () => {
    try {
      setUploadMessage('Applying daily consumption...');
      
      const response = await fetch('https://wodenstockai.onrender.com/api/daily-consumption/apply', {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        setUploadMessage(result.message);
        
        // Reload stock data to show updates
        setTimeout(() => {
          loadStockData();
          setUploadMessage('');
        }, 3000);
      } else {
        const error = await response.json();
        console.error('Daily consumption failed:', error);
        setUploadMessage(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Daily consumption error:', error);
      setUploadMessage('Error applying daily consumption');
    }
  };

  const getStockStatus = (item: StockItem) => {
    if (item.current_stock === 0) return 'out-of-stock';
    if (item.current_stock <= item.min_stock) return 'low-stock';
    return 'normal';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'out-of-stock': return 'text-red-600 bg-red-50';
      case 'low-stock': return 'text-orange-600 bg-orange-50';
      default: return 'text-green-600 bg-green-50';
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === 'out-of-stock') return <AlertTriangle className="w-4 h-4 text-red-600" />;
    if (status === 'low-stock') return <AlertTriangle className="w-4 h-4 text-orange-600" />;
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 px-2 sm:px-0">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stock List</h1>
          <p className="text-gray-600">Manage your inventory and upload daily sales</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <button
            onClick={() => setShowUploadModal(true)}
            data-upload-button
            className="inline-flex items-center justify-center px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base touch-manipulation"
          >
            <Upload className="w-4 h-4 mr-1 sm:mr-2" />
            <span className="hidden sm:inline">Upload Daily Sales Excel</span>
            <span className="sm:hidden">Upload Excel</span>
          </button>
          <button
            onClick={handleDailyConsumption}
            className="inline-flex items-center justify-center px-3 sm:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm sm:text-base touch-manipulation"
          >
            <Calendar className="w-4 h-4 mr-1 sm:mr-2" />
            <span className="hidden sm:inline">Apply Daily Consumption</span>
            <span className="sm:hidden">Daily Consumption</span>
          </button>
          <button
            onClick={loadStockData}
            className="inline-flex items-center justify-center px-3 sm:px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm sm:text-base touch-manipulation"
          >
            <RefreshCw className="w-4 h-4 mr-1 sm:mr-2" />
            <span className="hidden sm:inline">Refresh</span>
            <span className="sm:hidden">↻</span>
          </button>
        </div>
      </div>

      {/* Upload Success Message */}
      {uploadMessage && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800">{uploadMessage}</p>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search by name or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
            />
          </div>
        </div>
        <div className="w-full sm:w-48">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Stock Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Mobile scroll indicator */}
        <div className="sm:hidden bg-blue-50 border-b border-blue-200 px-4 py-2">
          <p className="text-xs text-blue-600 text-center">
            ← Swipe horizontally to see all columns →
          </p>
        </div>
        <div className="overflow-x-auto overflow-y-auto max-h-[70vh]">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                  Item Name
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                  Category
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                  Current Stock
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                  Min Level
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[80px]">
                  Unit
                </th>
                <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">
                  Stock Update
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredData.map((item) => {
                const status = getStockStatus(item);
                return (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(status)}
                        <span className="ml-2 font-medium text-gray-900 text-sm sm:text-base">
                          {item.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="hidden sm:inline">{item.category}</span>
                      <span className="sm:hidden text-xs">{item.category.substring(0, 8)}...</span>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                        {item.current_stock} {item.unit}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.min_stock} {item.unit}
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.unit}
                    </td>
                    <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                       <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-2">
                         <input
                           type="number"
                           min="0"
                           step="0.01"
                           placeholder={`Enter new value (current: ${item.current_stock})`}
                           className="w-full sm:w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           onKeyPress={(e) => {
                             if (e.key === 'Enter') {
                               console.log('=== Enter key pressed ===');
                               console.log('Item:', item.name, 'ID:', item.id, 'can_edit:', item.can_edit);
                               const target = e.target as HTMLInputElement;
                               console.log('Input value:', target.value);
                               if (target.value && target.value.trim() !== '') {
                                 const newValue = parseFloat(target.value);
                                 console.log('Parsed new value:', newValue);
                                 if (!isNaN(newValue) && newValue >= 0) {
                                   const change = newValue - item.current_stock;
                                   console.log('Calculated change:', change);
                                   updateStock(item.id, change);
                                   target.value = '';
                                 } else {
                                   alert('Please enter a valid number (0 or greater)');
                                 }
                               } else {
                                 alert('Please enter a new stock value before pressing Enter');
                               }
                             }
                           }}
                         />
                         <div className="flex space-x-1 w-full sm:w-auto">
                           <button
                             onClick={(e) => {
                               console.log('=== Update button clicked ===');
                               console.log('Item:', item.name, 'ID:', item.id, 'can_edit:', item.can_edit);
                               
                               // Find the input field in the same row
                               const row = e.currentTarget.closest('tr');
                               const input = row?.querySelector('input[type="number"]') as HTMLInputElement;
                               
                               console.log('Row found:', row);
                               console.log('Input element found:', input);
                               console.log('Input value:', input?.value);
                               
                               if (input && input.value && input.value.trim() !== '') {
                                 const newValue = parseFloat(input.value);
                                 console.log('Parsed new value:', newValue);
                                 if (!isNaN(newValue) && newValue >= 0) {
                                   const change = newValue - item.current_stock;
                                   console.log('Calculated change:', change);
                                   updateStock(item.id, change);
                                   input.value = '';
                                 } else {
                                   alert('Please enter a valid number (0 or greater)');
                                 }
                               } else {
                                 alert('Please enter a new stock value before clicking Update');
                               }
                             }}
                             className="flex-1 sm:flex-none inline-flex items-center justify-center px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 touch-manipulation"
                           >
                             <span className="hidden sm:inline">Update</span>
                             <span className="sm:hidden">✓</span>
                           </button>
                           <button
                             onClick={() => removeStockItem(item.name)}
                             className="flex-1 sm:flex-none inline-flex items-center justify-center px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 touch-manipulation"
                           >
                             <span className="hidden sm:inline">Remove</span>
                             <span className="sm:hidden">×</span>
                           </button>
                         </div>
                       </div>
                     </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {filteredData.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No items found matching your criteria.</p>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Daily Sales Excel</h3>
            
                         <div className="mb-4">
               <input
                 type="file"
                 accept=".xlsx,.xls"
                 onChange={(e) => {
                   const file = e.target.files?.[0] || null;
                   console.log('File selected:', file?.name, 'Size:', file?.size);
                   setSelectedFile(file);
                 }}
                 className="w-full p-2 border border-gray-300 rounded-lg"
               />
             </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setSelectedFile(null);
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleFileUpload}
                disabled={!selectedFile}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
