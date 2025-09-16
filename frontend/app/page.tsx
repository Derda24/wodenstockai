'use client';

import { useState, useEffect } from 'react';
import { 
  Box, 
  BarChart3, 
  TrendingUp, 
  Settings as SettingsIcon, 
  Upload,
  LogOut,
  Menu,
  X,
  Sparkles,
  Zap,
  Brain,
  Shield,
  Calendar
} from 'lucide-react';
import StockList from '@/components/StockList';
import AIAnalysis from '@/components/AIAnalysis';
import AIRecommendations from '@/components/AIRecommendations';
import AIScheduler from '@/components/AIScheduler';
import Settings from '@/components/Settings';
import LoginModal from '@/components/LoginModal';
import { LoadingScreen } from '@/components/loginscreen';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('stock');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLogin, setShowLogin] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Show loading screen for 2 seconds on app start
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleLogin = (success: boolean) => {
    if (success) {
      setIsAuthenticated(true);
      setShowLogin(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setShowLogin(true);
  };

  // Show loading screen first
  if (isLoading) {
    return <LoadingScreen isLoading={true} />;
  }

  if (!isAuthenticated) {
    return <LoginModal onLogin={handleLogin} />;
  }

  const tabs = [
    { 
      id: 'stock', 
      name: 'Stock Management', 
      icon: Box, 
      description: 'Manage inventory',
      gradient: 'from-blue-500 to-purple-600'
    },
    { 
      id: 'analysis', 
      name: 'AI Analytics', 
      icon: BarChart3, 
      description: 'Smart insights',
      gradient: 'from-emerald-500 to-teal-600'
    },
    { 
      id: 'recommendations', 
      name: 'AI Recommendations', 
      icon: Brain, 
      description: 'Smart suggestions',
      gradient: 'from-orange-500 to-red-600'
    },
    { 
      id: 'scheduler', 
      name: 'AI Scheduler', 
      icon: Calendar, 
      description: 'Weekly Programming',
      gradient: 'from-purple-500 to-pink-600'
    },
    { 
      id: 'settings', 
      name: 'Settings', 
      icon: SettingsIcon, 
      description: 'Configuration',
      gradient: 'from-gray-500 to-gray-700'
    },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'stock':
        return <StockList />;
      case 'analysis':
        return <AIAnalysis />;
      case 'recommendations':
        return <AIRecommendations />;
      case 'scheduler':
        return <AIScheduler />;
      case 'settings':
        return <Settings />;
      default:
        return <StockList />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Modern Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-soft border-b border-white/20 sticky top-0 z-40">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
            >
              {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <img
                  src="/AI-LOGO.png"
                  alt="Woden AI Logo"
                  className="w-12 h-12 rounded-2xl shadow-medium"
                />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-accent rounded-full animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                  WODEN Stock AI
                </h1>
                <p className="text-sm text-gray-500 font-medium">Intelligent Inventory Management</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-700">AI Active</span>
            </div>
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all duration-200 group"
            >
              <LogOut size={16} className="group-hover:scale-110 transition-transform duration-200" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Modern Sidebar */}
        <aside className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white/90 backdrop-blur-lg shadow-large lg:shadow-none border-r border-white/20 transform transition-all duration-300 ease-in-out`}>
          <div className="h-full flex flex-col">
            {/* Sidebar Header */}
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-800">Navigation</h2>
              <p className="text-sm text-gray-500">Choose your workspace</p>
            </div>
            
            {/* Navigation */}
            <nav className="flex-1 p-6">
              <ul className="space-y-3">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <li key={tab.id}>
                    <button
                      onClick={() => {
                        setActiveTab(tab.id);
                        setIsSidebarOpen(false);
                      }}
                      data-tab={tab.id}
                      className={`w-full group relative overflow-hidden rounded-2xl p-4 text-left transition-all duration-300 ${
                        isActive
                          ? `bg-gradient-to-r ${tab.gradient} text-white shadow-medium transform scale-105`
                          : 'text-gray-700 hover:bg-gray-50 hover:shadow-soft hover:scale-105'
                      }`}
                    >
                        <div className="flex items-center space-x-4">
                          <div className={`p-2 rounded-xl transition-all duration-200 ${
                            isActive 
                              ? 'bg-white/20' 
                              : 'bg-gray-100 group-hover:bg-gray-200'
                          }`}>
                            <Icon size={20} className={isActive ? 'text-white' : 'text-gray-600'} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`font-semibold transition-colors duration-200 ${
                              isActive ? 'text-white' : 'text-gray-900 group-hover:text-gray-700'
                            }`}>
                              {tab.name}
                            </p>
                            <p className={`text-sm transition-colors duration-200 ${
                              isActive ? 'text-white/80' : 'text-gray-500 group-hover:text-gray-600'
                            }`}>
                              {tab.description}
                            </p>
                          </div>
                          {isActive && (
                            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                          )}
                        </div>
                        
                        {/* Hover effect */}
                        <div className={`absolute inset-0 bg-gradient-to-r ${tab.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300 ${
                          isActive ? 'opacity-0' : ''
                        }`}></div>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>
            
            {/* Sidebar Footer */}
            <div className="p-6 border-t border-gray-100">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-4 border border-blue-100">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-800">AI Powered</p>
                    <p className="text-xs text-gray-600">Smart inventory management</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-2 sm:p-4 lg:p-8 overflow-x-hidden">
          <div className="max-w-7xl mx-auto">
            <div className="animate-fade-in">
              {renderContent()}
            </div>
          </div>
        </main>
      </div>

      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden animate-fade-in"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}
