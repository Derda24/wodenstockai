'use client';

import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, TrendingDown, AlertTriangle, Calendar, FileText } from 'lucide-react';

interface SalesRecord {
  product_name: string;
  quantity: number;
  date: string;
}

interface AnalysisData {
  totalSales: number;
  topProducts: Array<{ name: string; quantity: number; percentage: number }>;
  lowStockAlerts: Array<{ name: string; current: number; min: number; unit: string }>;
  dailyTrends: Array<{ date: string; totalSales: number; products: number }>;
  categoryBreakdown: Array<{ category: string; count: number; percentage: number }>;
}

export default function AIAnalysis() {
  const [analysisData, setAnalysisData] = useState<AnalysisData>({
    totalSales: 0,
    topProducts: [],
    lowStockAlerts: [],
    dailyTrends: [],
    categoryBreakdown: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');

  useEffect(() => {
    loadAnalysisData();
  }, [selectedPeriod]);

  const loadAnalysisData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`https://wodenstockai.onrender.com/api/analysis?period=${selectedPeriod}`);
      if (response.ok) {
        const data = await response.json();
        // Ensure all required fields exist with fallbacks
        setAnalysisData({
          totalSales: data.totalSales || 0,
          topProducts: data.topProducts || [],
          lowStockAlerts: data.lowStockAlerts || [],
          dailyTrends: data.dailyTrends || [],
          categoryBreakdown: data.categoryBreakdown || []
        });
      }
    } catch (error) {
      console.error('Error loading analysis data:', error);
      setHasError(true);
      // Keep default state on error
    } finally {
      setIsLoading(false);
    }
  };

  const getPeriodLabel = (period: string) => {
    switch (period) {
      case '7d': return 'Last 7 Days';
      case '30d': return 'Last 30 Days';
      case '90d': return 'Last 90 Days';
      default: return 'All Time';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error Loading Analysis</h3>
        <p className="mt-1 text-sm text-gray-500">Failed to load analysis data. Please try again.</p>
        <button
          onClick={() => {
            setHasError(false);
            loadAnalysisData();
          }}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Analysis</h1>
          <p className="text-gray-600 mt-1">Intelligent insights from your sales data</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="block px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Sales</p>
              <p className="text-2xl font-bold text-gray-900">{analysisData.totalSales || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Top Product</p>
                             <p className="text-2xl font-bold text-gray-900">
                 {analysisData.topProducts && analysisData.topProducts.length > 0 ? analysisData.topProducts[0].name : 'N/A'}
               </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Low Stock Items</p>
              <p className="text-2xl font-bold text-gray-900">{analysisData.lowStockAlerts?.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Period</p>
              <p className="text-lg font-bold text-gray-900">{getPeriodLabel(selectedPeriod)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Top Products Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Top Selling Products</h3>
          <p className="text-sm text-gray-600">Most popular items by quantity sold</p>
        </div>
        {analysisData.topProducts && analysisData.topProducts.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity Sold
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Market Share
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analysisData.topProducts.map((product, index) => (
                  <tr key={product.name}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                          index === 0 ? 'bg-yellow-100 text-yellow-800' :
                          index === 1 ? 'bg-gray-100 text-gray-800' :
                          index === 2 ? 'bg-orange-100 text-orange-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {index + 1}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {product.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.percentage?.toFixed(1) || '0.0'}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Sales Data</h3>
            <p className="mt-1 text-sm text-gray-500">Upload Excel files to see top selling products.</p>
          </div>
        )}
      </div>

      {/* Low Stock Alerts */}
      {analysisData.lowStockAlerts && analysisData.lowStockAlerts.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-red-900">Low Stock Alerts</h3>
            <p className="text-sm text-red-600">Items that need immediate attention</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-red-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-red-700 uppercase tracking-wider">
                    Item Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-red-700 uppercase tracking-wider">
                    Current Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-red-700 uppercase tracking-wider">
                    Minimum Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-red-700 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analysisData.lowStockAlerts.map((item) => (
                  <tr key={item.name} className="bg-red-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-900">
                      {item.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                      {item.current} {item.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                      {item.min} {item.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Critical
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Daily Trends */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Daily Sales Trends</h3>
          <p className="text-sm text-gray-600">Sales performance over time</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Sales
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Products Sold
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trend
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analysisData.dailyTrends && analysisData.dailyTrends.length > 0 ? (
                analysisData.dailyTrends.map((day, index) => {
                  const previousDay = analysisData.dailyTrends[index + 1];
                  const trend = previousDay ? day.totalSales - previousDay.totalSales : 0;
                  
                  return (
                    <tr key={day.date}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {new Date(day.date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {day.totalSales}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {day.products}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {trend > 0 ? (
                          <div className="flex items-center text-green-600">
                            <TrendingUp className="w-4 h-4 mr-1" />
                            <span className="text-sm">+{trend}</span>
                          </div>
                        ) : trend < 0 ? (
                          <div className="flex items-center text-red-600">
                            <TrendingDown className="w-4 h-4 mr-1" />
                            <span className="text-sm">{trend}</span>
                          </div>
                        ) : (
                          <span className="text-sm text-gray-500">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="text-center py-12">
                    <FileText className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No Trend Data</h3>
                    <p className="mt-1 text-sm text-gray-500">Upload Excel files to see daily sales trends.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Category Breakdown</h3>
          <p className="text-sm text-gray-600">Sales distribution by product category</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Products Sold
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Visual
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analysisData.categoryBreakdown && analysisData.categoryBreakdown.length > 0 ? (
                analysisData.categoryBreakdown.map((category) => (
                  <tr key={category.category}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {category.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {category.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {category.percentage?.toFixed(1) || '0.0'}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-brand-500 h-2 rounded-full"
                          style={{ width: `${category.percentage || 0}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="text-center py-12">
                    <FileText className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No Category Data</h3>
                    <p className="mt-1 text-sm text-gray-500">Upload Excel files to see category breakdown.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
