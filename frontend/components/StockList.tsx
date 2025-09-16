'use client';

import { useState, useEffect } from 'react';
import { Plus, Minus, Search, Upload, RefreshCw, AlertTriangle, Calendar, X } from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

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
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: '',
    category: '',
    current_stock: 0,
    min_stock: 0,
    unit: 'ml',
    is_ready_made: false,
    cost_per_unit: 0,
    package_size: 0,
    package_unit: 'ml'
  });

  // Get unique categories for filter
  const categories = ['All Categories', ...Array.from(new Set(stockData.map((item: StockItem) => item.category)))];

  const loadStockData = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.STOCK.GET);
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

      const response = await fetch(API_ENDPOINTS.STOCK.UPDATE, {
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

      const response = await fetch(API_ENDPOINTS.STOCK.REMOVE, {
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
      const response = await fetch(API_ENDPOINTS.SALES.UPLOAD, {
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
        setTimeout(async () => {
          loadStockData();
          setUploadMessage('');
          
          // Trigger AI data refresh
          try {
            await fetch(API_ENDPOINTS.ANALYSIS.REFRESH, { method: 'POST' });
            console.log('AI Analytics data refreshed automatically');
          } catch (refreshError) {
            console.warn('Could not refresh AI data:', refreshError);
          }
          
          // Show notification that data has been refreshed
          const notification = document.createElement('div');
          notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-2';
          notification.innerHTML = `
            <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span>Excel uploaded successfully! AI Analytics data refreshed automatically.</span>
            <button onclick="this.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">×</button>
          `;
          document.body.appendChild(notification);
          
          // Auto-remove notification after 5 seconds
          setTimeout(() => {
            if (notification.parentElement) {
              notification.remove();
            }
          }, 5000);
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
      
      const response = await fetch(API_ENDPOINTS.DAILY_CONSUMPTION.APPLY, {
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

  const handleAddProduct = async () => {
    try {
      // Validate required fields
      if (!newProduct.name || !newProduct.category) {
        alert('Please fill in all required fields (Name and Category)');
        return;
      }

      const response = await fetch(API_ENDPOINTS.STOCK.ADD_PRODUCT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newProduct)
      });

      if (response.ok) {
        const result = await response.json();
        setUploadMessage(`Product "${newProduct.name}" added successfully!`);
        
        // Reset form
        setNewProduct({
          name: '',
          category: '',
          current_stock: 0,
          min_stock: 0,
          unit: 'ml',
          is_ready_made: false,
          cost_per_unit: 0,
          package_size: 0,
          package_unit: 'ml'
        });
        setShowAddProductModal(false);
        
        // Reload stock data
        setTimeout(() => {
          loadStockData();
          setUploadMessage('');
        }, 2000);
      } else {
        const error = await response.json();
        console.error('Add product failed:', error);
        setUploadMessage(`Error: ${error.detail || 'Failed to add product'}`);
      }
    } catch (error) {
      console.error('Add product error:', error);
      setUploadMessage('Error adding product');
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
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0 w-full overflow-visible">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Stock List</h1>
          <p className="text-sm sm:text-base text-gray-600">Manage your inventory and upload daily sales</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <button
            onClick={() => setShowAddProductModal(true)}
            className="inline-flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm sm:text-base touch-manipulation min-h-[44px]"
          >
            <Plus className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Add New Product</span>
            <span className="sm:hidden">Add Product</span>
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            data-upload-button
            className="inline-flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm sm:text-base touch-manipulation min-h-[44px]"
          >
            <Upload className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Upload Daily Sales Excel</span>
            <span className="sm:hidden">Upload Excel</span>
          </button>
          <button
            onClick={handleDailyConsumption}
            className="inline-flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm sm:text-base touch-manipulation min-h-[44px]"
          >
            <Calendar className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Apply Daily Consumption</span>
            <span className="sm:hidden">Daily Consumption</span>
          </button>
          <button
            onClick={loadStockData}
            className="inline-flex items-center justify-center px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm sm:text-base touch-manipulation min-h-[44px]"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
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
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base touch-manipulation min-h-[44px]"
            />
          </div>
        </div>
        <div className="w-full sm:w-48">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base touch-manipulation min-h-[44px]"
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Stock Display - Mobile Cards / Desktop Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden w-full">
        {/* Mobile Card Layout */}
        <div className="block sm:hidden">
          <div className="overflow-y-auto max-h-[75vh] p-4 space-y-4">
            {filteredData.map((item) => {
              const status = getStockStatus(item);
              return (
                <div key={item.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  {/* Header with status */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      {getStatusIcon(status)}
                      <h3 className="ml-2 font-semibold text-gray-900 text-sm truncate flex-1">
                        {item.name}
                      </h3>
                    </div>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                      {item.current_stock} {item.unit}
                    </span>
                  </div>
                  
                  {/* Details */}
                  <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                    <div>
                      <span className="text-gray-500">Category:</span>
                      <p className="font-medium text-gray-900">{item.category}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Min Level:</span>
                      <p className="font-medium text-gray-900">{item.min_stock} {item.unit}</p>
                    </div>
                  </div>
                  
                  {/* Stock Update Section */}
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Update Stock
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder={`New value (${item.current_stock})`}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent touch-manipulation"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            const target = e.target as HTMLInputElement;
                            if (target.value && target.value.trim() !== '') {
                              const newValue = parseFloat(target.value);
                              if (!isNaN(newValue) && newValue >= 0) {
                                const change = newValue - item.current_stock;
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
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-2">
                      <button
                        onClick={(e) => {
                          const input = e.currentTarget.parentElement?.previousElementSibling?.querySelector('input[type="number"]') as HTMLInputElement;
                          if (input && input.value && input.value.trim() !== '') {
                            const newValue = parseFloat(input.value);
                            if (!isNaN(newValue) && newValue >= 0) {
                              const change = newValue - item.current_stock;
                              updateStock(item.id, change);
                              input.value = '';
                            } else {
                              alert('Please enter a valid number (0 or greater)');
                            }
                          } else {
                            alert('Please enter a new stock value before clicking Update');
                          }
                        }}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 touch-manipulation min-h-[44px]"
                      >
                        ✓ Update
                      </button>
                      <button
                        onClick={() => removeStockItem(item.name)}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 touch-manipulation min-h-[44px]"
                      >
                        × Remove
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
            
            {filteredData.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No items found matching your criteria.</p>
              </div>
            )}
          </div>
        </div>

        {/* Desktop Table Layout */}
        <div className="hidden sm:block">
          <div className="overflow-x-auto overflow-y-auto max-h-[70vh] w-full" style={{WebkitOverflowScrolling: 'touch', scrollbarWidth: 'thin'}}>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Min Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stock Update
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredData.map((item) => {
                  const status = getStockStatus(item);
                  return (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(status)}
                          <span className="ml-2 font-medium text-gray-900">
                            {item.name}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {item.category}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                          {item.current_stock} {item.unit}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {item.min_stock} {item.unit}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {item.unit}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            placeholder={`New value (${item.current_stock})`}
                            className="w-20 px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                const target = e.target as HTMLInputElement;
                                if (target.value && target.value.trim() !== '') {
                                  const newValue = parseFloat(target.value);
                                  if (!isNaN(newValue) && newValue >= 0) {
                                    const change = newValue - item.current_stock;
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
                          <button
                            onClick={(e) => {
                              const row = e.currentTarget.closest('tr');
                              const input = row?.querySelector('input[type="number"]') as HTMLInputElement;
                              if (input && input.value && input.value.trim() !== '') {
                                const newValue = parseFloat(input.value);
                                if (!isNaN(newValue) && newValue >= 0) {
                                  const change = newValue - item.current_stock;
                                  updateStock(item.id, change);
                                  input.value = '';
                                } else {
                                  alert('Please enter a valid number (0 or greater)');
                                }
                              } else {
                                alert('Please enter a new stock value before clicking Update');
                              }
                            }}
                            className="inline-flex items-center justify-center px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          >
                            Update
                          </button>
                          <button
                            onClick={() => removeStockItem(item.name)}
                            className="inline-flex items-center justify-center px-3 py-2 text-xs bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          >
                            Remove
                          </button>
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
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Upload Daily Sales Excel</h3>
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                  }}
                  className="text-gray-400 hover:text-gray-600 touch-manipulation"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Excel File
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => {
                    const file = e.target.files?.[0] || null;
                    console.log('File selected:', file?.name, 'Size:', file?.size);
                    setSelectedFile(file);
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent touch-manipulation"
                />
                {selectedFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {selectedFile.name}
                  </p>
                )}
              </div>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                  }}
                  className="flex-1 px-4 py-3 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 touch-manipulation min-h-[44px]"
                >
                  Cancel
                </button>
                <button
                  onClick={handleFileUpload}
                  disabled={!selectedFile}
                  className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation min-h-[44px]"
                >
                  Upload
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add New Product Modal */}
      {showAddProductModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">Add New Product</h2>
                <button
                  onClick={() => setShowAddProductModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Product Name *
                  </label>
                  <input
                    type="text"
                    value={newProduct.name}
                    onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                    className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent touch-manipulation text-base"
                    placeholder="Enter product name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <select
                    value={newProduct.category}
                    onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                    className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent touch-manipulation text-base"
                  >
                    <option value="">Select category</option>
                    <option value="surup_pureler">Syrups & Purees</option>
                    <option value="ham_maddeler">Raw Materials</option>
                    <option value="sut_urunleri">Dairy Products</option>
                    <option value="unlu_mamuller">Bakery Products</option>
                    <option value="icecekler">Beverages</option>
                    <option value="diger">Other</option>
                  </select>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Current Stock
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={newProduct.current_stock}
                      onChange={(e) => setNewProduct({...newProduct, current_stock: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent touch-manipulation text-base"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Min Stock Level
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={newProduct.min_stock}
                      onChange={(e) => setNewProduct({...newProduct, min_stock: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent touch-manipulation text-base"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Unit
                    </label>
                    <select
                      value={newProduct.unit}
                      onChange={(e) => setNewProduct({...newProduct, unit: e.target.value})}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent touch-manipulation text-base"
                    >
                      <option value="ml">ml</option>
                      <option value="kg">kg</option>
                      <option value="g">g</option>
                      <option value="adet">adet</option>
                      <option value="lt">lt</option>
                      <option value="paket">paket</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cost per Unit
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={newProduct.cost_per_unit}
                      onChange={(e) => setNewProduct({...newProduct, cost_per_unit: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent touch-manipulation text-base"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="flex items-center p-3 bg-gray-50 rounded-lg">
                    <input
                      type="checkbox"
                      checked={newProduct.is_ready_made}
                      onChange={(e) => setNewProduct({...newProduct, is_ready_made: e.target.checked})}
                      className="mr-3 w-4 h-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">Ready-made product (not a raw material)</span>
                  </label>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <button
                  onClick={() => setShowAddProductModal(false)}
                  className="flex-1 px-4 py-3 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 touch-manipulation min-h-[44px]"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddProduct}
                  className="flex-1 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 touch-manipulation min-h-[44px]"
                >
                  Add Product
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
