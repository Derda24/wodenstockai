'use client';

import { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Calendar, 
  FileText,
  Brain,
  Zap,
  Target,
  Activity,
  DollarSign,
  Package,
  Users,
  Clock,
  Sparkles,
  Upload
} from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

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

  // Auto-refresh when component becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadAnalysisData();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const loadAnalysisData = async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      console.log(`Loading analysis data for period: ${selectedPeriod}`);
      const response = await fetch(`${API_ENDPOINTS.ANALYSIS.GET}?period=${selectedPeriod}`);
      console.log('Analysis API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Analysis API response data:', data);
        console.log('Top products data:', data.topProducts);
        console.log('Category breakdown data:', data.categoryBreakdown);
        
        // Ensure all required fields exist with fallbacks
        setAnalysisData({
          totalSales: data.totalSales || 0,
          topProducts: data.topProducts || [],
          lowStockAlerts: data.lowStockAlerts || [],
          dailyTrends: data.dailyTrends || [],
          categoryBreakdown: data.categoryBreakdown || []
        });
      } else {
        console.error('Analysis API error:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('Error response:', errorText);
        setHasError(true);
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
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="relative mx-auto w-16 h-16 mb-4">
            <div className="loading-spinner w-16 h-16"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Brain className="w-8 h-8 text-primary-500" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">AI is analyzing your data</h3>
          <p className="text-gray-500">Processing sales insights...</p>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="text-center py-16">
        <div className="mx-auto w-20 h-20 bg-red-100 rounded-2xl flex items-center justify-center mb-6">
          <AlertTriangle className="w-10 h-10 text-red-500" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Analysis Failed</h3>
        <p className="text-gray-600 mb-6">Unable to load analysis data. Please try again.</p>
        <button
          onClick={() => {
            setHasError(false);
            loadAnalysisData();
          }}
          className="btn-primary"
        >
          <Activity className="w-4 h-4 mr-2" />
          Retry Analysis
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Modern Header */}
      <div className="relative">
        <div className="flex flex-col space-y-4 lg:flex-row lg:items-center lg:justify-between lg:space-y-0">
          <div className="mb-6 lg:mb-0">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-medium">
                <Brain className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">AI Analytics</h1>
                <p className="text-gray-600 text-sm sm:text-lg">Intelligent insights powered by AI</p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-4">
              <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs sm:text-sm font-medium text-green-700">AI Active</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1 bg-blue-100 rounded-full">
                <Sparkles className="w-3 h-3 sm:w-4 sm:h-4 text-blue-600" />
                <span className="text-xs sm:text-sm font-medium text-blue-700">Real-time Analysis</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
            <div className="relative">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="w-full sm:w-auto appearance-none bg-white border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm font-medium text-gray-700 shadow-soft focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 touch-manipulation"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="all">All Time</option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <Calendar className="w-4 h-4 text-gray-400" />
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={loadAnalysisData}
                disabled={isLoading}
                className="flex-1 sm:flex-none flex items-center justify-center space-x-2 px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-700 shadow-soft hover:shadow-medium focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation min-h-[44px]"
              >
                <Activity className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">{isLoading ? 'Refreshing...' : 'Refresh'}</span>
                <span className="sm:hidden">{isLoading ? '...' : '↻'}</span>
              </button>
              
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(API_ENDPOINTS.ANALYSIS.TEST_DATA, { method: 'POST' });
                    const result = await response.json();
                    console.log('Test data created:', result);
                    alert('Test sales data created! Refresh the analysis to see it.');
                    loadAnalysisData();
                  } catch (error) {
                    console.error('Error creating test data:', error);
                    alert('Error creating test data. Check console for details.');
                  }
                }}
                className="flex-1 sm:flex-none flex items-center justify-center space-x-2 px-4 py-3 bg-blue-500 text-white rounded-xl text-sm font-medium shadow-soft hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 transition-all duration-200 touch-manipulation min-h-[44px]"
              >
                <Sparkles className="w-4 h-4" />
                <span className="hidden sm:inline">Create Test Data</span>
                <span className="sm:hidden">Test</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modern Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Sales Card */}
        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-medium">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-green-600">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm font-medium">+12%</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Total Sales</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">{analysisData.totalSales || 0}</p>
            <p className="text-xs text-gray-500">Items sold this period</p>
          </div>
        </div>

        {/* Top Product Card */}
        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-medium">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-emerald-600">
                <Zap className="w-4 h-4" />
                <span className="text-sm font-medium">Top</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Best Seller</p>
            <p className="text-lg font-bold text-gray-900 mb-2 truncate">
              {analysisData.topProducts && analysisData.topProducts.length > 0 ? analysisData.topProducts[0].name : 'N/A'}
            </p>
            <p className="text-xs text-gray-500">
              {analysisData.topProducts && analysisData.topProducts.length > 0 
                ? `${analysisData.topProducts[0].quantity} units sold`
                : 'No data available'
              }
            </p>
          </div>
        </div>

        {/* Low Stock Alerts Card */}
        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center shadow-medium">
              <AlertTriangle className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-red-600">
                <Activity className="w-4 h-4" />
                <span className="text-sm font-medium">Alert</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Low Stock Items</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">{analysisData.lowStockAlerts?.length || 0}</p>
            <p className="text-xs text-gray-500">Need immediate attention</p>
          </div>
        </div>

        {/* Period Card */}
        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-medium">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-purple-600">
                <Clock className="w-4 h-4" />
                <span className="text-sm font-medium">Active</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Analysis Period</p>
            <p className="text-lg font-bold text-gray-900 mb-2">{getPeriodLabel(selectedPeriod)}</p>
            <p className="text-xs text-gray-500">Current time range</p>
          </div>
        </div>
      </div>

      {/* Top Products Table */}
      <div className="card-elevated">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Top Selling Products</h3>
              <p className="text-sm text-gray-600">Most popular items by quantity sold</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-100 rounded-full">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-medium text-emerald-700">AI Ranked</span>
          </div>
        </div>
        
        {analysisData.topProducts && analysisData.topProducts.length > 0 ? (
          <div className="space-y-3">
            {analysisData.topProducts.map((product, index) => (
              <div key={product.name} className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-soft transition-all duration-200 group">
                <div className="flex items-center space-x-4 mb-3 sm:mb-0">
                  <div className="relative">
                    <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center font-bold text-white shadow-medium ${
                      index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                      index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                      index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-500' :
                      'bg-gradient-to-br from-blue-400 to-blue-500'
                    }`}>
                      {index + 1}
                    </div>
                    {index < 3 && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-gradient-accent rounded-full flex items-center justify-center">
                        <Zap className="w-1.5 h-1.5 sm:w-2 sm:h-2 text-white" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors duration-200 truncate">
                      {product.name}
                    </h4>
                    <p className="text-sm text-gray-500">
                      {product.quantity} units sold
                    </p>
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <div className="text-xl sm:text-2xl font-bold text-gray-900">
                    {product.percentage?.toFixed(1) || '0.0'}%
                  </div>
                  <div className="text-sm text-gray-500">Market Share</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Sales Data</h3>
            <p className="text-gray-600 mb-6">Upload Excel files to see top selling products.</p>
            <button 
              className="btn-primary"
              onClick={() => {
                // Navigate to Stock List tab where upload functionality exists
                const stockTab = document.querySelector('[data-tab="stock"]') as HTMLButtonElement;
                if (stockTab) {
                  stockTab.click();
                  // Trigger upload modal after a short delay
                  setTimeout(() => {
                    const uploadButton = document.querySelector('[data-upload-button]') as HTMLButtonElement;
                    if (uploadButton) {
                      uploadButton.click();
                    }
                  }, 500);
                }
              }}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Data
            </button>
          </div>
        )}
      </div>

      {/* Low Stock Alerts */}
      {analysisData.lowStockAlerts && analysisData.lowStockAlerts.length > 0 && (
        <div className="card-elevated border-l-4 border-red-500">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-red-900">Low Stock Alerts</h3>
                <p className="text-sm text-red-600">Items that need immediate attention</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1 bg-red-100 rounded-full">
              <Activity className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-700">Critical</span>
            </div>
          </div>
          
          <div className="space-y-3">
            {analysisData.lowStockAlerts.map((item) => (
              <div key={item.name} className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 bg-gradient-to-r from-red-50 to-red-25 rounded-xl border border-red-200 hover:shadow-soft transition-all duration-200 group">
                <div className="flex items-center space-x-4 mb-3 sm:mb-0">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                    <Package className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-red-900 group-hover:text-red-700 transition-colors duration-200 truncate">
                      {item.name}
                    </h4>
                    <p className="text-sm text-red-600">
                      <span className="block sm:inline">Current: {item.current} {item.unit}</span>
                      <span className="hidden sm:inline"> | </span>
                      <span className="block sm:inline">Min: {item.min} {item.unit}</span>
                    </p>
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <div className="badge-danger mb-1">
                    Critical
                  </div>
                  <div className="text-sm text-red-600">
                    {Math.round(((item.current / item.min) - 1) * 100)}% below minimum
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Daily Trends */}
      <div className="card-elevated">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Daily Sales Trends</h3>
              <p className="text-sm text-gray-600">Sales performance over time</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1 bg-blue-100 rounded-full">
            <Activity className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-700">Live Data</span>
          </div>
        </div>
        
        {analysisData.dailyTrends && analysisData.dailyTrends.length > 0 ? (
          <div className="space-y-3">
            {analysisData.dailyTrends.map((day, index) => {
              const previousDay = analysisData.dailyTrends[index + 1];
              const trend = previousDay ? day.totalSales - previousDay.totalSales : 0;
              
              return (
                <div key={day.date} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-soft transition-all duration-200 group">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-200">
                        {new Date(day.date).toLocaleDateString('en-US', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {day.products} different products sold
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {day.totalSales}
                    </div>
                    <div className="text-sm text-gray-500 mb-2">Total Sales</div>
                    {trend !== 0 && (
                      <div className={`flex items-center justify-end space-x-1 ${
                        trend > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {trend > 0 ? (
                          <TrendingUp className="w-4 h-4" />
                        ) : (
                          <TrendingDown className="w-4 h-4" />
                        )}
                        <span className="text-sm font-medium">
                          {trend > 0 ? '+' : ''}{trend}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Trend Data</h3>
            <p className="text-gray-600 mb-6">Upload Excel files to see daily sales trends.</p>
            <button 
              className="btn-primary"
              onClick={() => {
                // Navigate to Stock List tab where upload functionality exists
                const stockTab = document.querySelector('[data-tab="stock"]') as HTMLButtonElement;
                if (stockTab) {
                  stockTab.click();
                  // Trigger upload modal after a short delay
                  setTimeout(() => {
                    const uploadButton = document.querySelector('[data-upload-button]') as HTMLButtonElement;
                    if (uploadButton) {
                      uploadButton.click();
                    }
                  }, 500);
                }
              }}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Data
            </button>
          </div>
        )}
      </div>

      {/* Category Breakdown */}
      <div className="card-elevated">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Category Breakdown</h3>
              <p className="text-sm text-gray-600">Sales distribution by product category</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1 bg-purple-100 rounded-full">
            <Brain className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-700">AI Categorized</span>
          </div>
        </div>
        
        {analysisData.categoryBreakdown && analysisData.categoryBreakdown.length > 0 ? (
          <div className="space-y-4">
            {analysisData.categoryBreakdown.map((category, index) => (
              <div key={category.category} className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-soft transition-all duration-200 group">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white shadow-medium ${
                      index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                      index === 1 ? 'bg-gradient-to-br from-blue-400 to-blue-500' :
                      index === 2 ? 'bg-gradient-to-br from-green-400 to-green-500' :
                      'bg-gradient-to-br from-purple-400 to-purple-500'
                    }`}>
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors duration-200">
                        {category.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {category.count} products sold
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {category.percentage?.toFixed(1) || '0.0'}%
                    </div>
                    <div className="text-sm text-gray-500">Market Share</div>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-3 rounded-full transition-all duration-1000 ease-out ${
                      index === 0 ? 'bg-gradient-to-r from-yellow-400 to-yellow-500' :
                      index === 1 ? 'bg-gradient-to-r from-blue-400 to-blue-500' :
                      index === 2 ? 'bg-gradient-to-r from-green-400 to-green-500' :
                      'bg-gradient-to-r from-purple-400 to-purple-500'
                    }`}
                    style={{ width: `${category.percentage || 0}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Category Data</h3>
            <p className="text-gray-600 mb-6">Upload Excel files to see category breakdown.</p>
            <button 
              className="btn-primary"
              onClick={() => {
                // Navigate to Stock List tab where upload functionality exists
                const stockTab = document.querySelector('[data-tab="stock"]') as HTMLButtonElement;
                if (stockTab) {
                  stockTab.click();
                  // Trigger upload modal after a short delay
                  setTimeout(() => {
                    const uploadButton = document.querySelector('[data-upload-button]') as HTMLButtonElement;
                    if (uploadButton) {
                      uploadButton.click();
                    }
                  }, 500);
                }
              }}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Data
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
