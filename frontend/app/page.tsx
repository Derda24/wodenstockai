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
  const [kpis, setKpis] = useState({ baristas: 0, lowStock: 0, weekCoverage: '—' });

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

  // Load KPIs (lightweight fetches)
  useEffect(() => {
    const load = async () => {
      try {
        // Low stock from alerts endpoint
        const alerts = await fetch('/api/alerts').then(r => r.ok ? r.json() : null).catch(() => null);
        const low = alerts?.low_stock_count ?? 0;
        // Baristas count
        const baristas = await fetch('/api/baristas').then(r => r.ok ? r.json() : []).catch(() => []);
        // Week coverage (placeholder until detailed calc exists)
        const weekCoverage = baristas?.length ? '100%' : '—';
        setKpis({ baristas: baristas.length || 0, lowStock: low, weekCoverage });
      } catch {}
    };
    load();
  }, []);

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-amber-50/20">
      {/* Elegant Header */}
      <header className="bg-white/95 backdrop-blur-sm sticky top-0 z-40 border-b border-slate-200/50 shadow-sm">
        <div className="relative overflow-hidden">
          {/* Subtle background gradient */}
          <div className="absolute inset-0 bg-gradient-to-r from-slate-50/50 via-white to-amber-50/30" />
        </div>
        <div className="relative flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hidden"
            >
              {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <img
                  src="/woden-logo-premium.svg"
                  alt="Woden AI Logo"
                  className="w-10 h-10 rounded-xl shadow-sm"
                />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-amber-400 to-amber-500 rounded-full animate-pulse shadow-sm"></div>
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  WODEN Stock AI
                </h1>
                <p className="text-xs sm:text-sm text-slate-600 font-medium">AI‑powered inventory, insights, and scheduling</p>
              </div>
            </div>
          </div>

          {/* Compact AI Status Indicator */}
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200/50">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-sm"></div>
              <span className="text-sm font-medium text-emerald-700">AI Active</span>
            </div>
            
            <button
              onClick={handleLogout}
              className="hidden lg:flex items-center space-x-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all duration-200 group"
            >
              <LogOut size={16} className="group-hover:scale-110 transition-transform duration-200" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>


      <div id="app" className="flex flex-col lg:flex-row">
        {/* Modern Sidebar - Hidden on mobile, shown on desktop */}
        <aside className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white/95 backdrop-blur-sm shadow-xl lg:shadow-none border-r border-slate-200/50 transform transition-all duration-300 ease-in-out hidden lg:block`}>
          <div className="h-full flex flex-col">
            {/* Sidebar Header */}
            <div className="p-6 border-b border-slate-200/50">
              <h2 className="text-lg font-semibold text-slate-800">Navigation</h2>
              <p className="text-sm text-slate-500">Choose your workspace</p>
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
            <div className="p-6 border-t border-slate-200/50">
              <div className="bg-gradient-to-r from-slate-50 to-amber-50/50 rounded-2xl p-4 border border-slate-200/50">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl flex items-center justify-center shadow-sm">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">AI Powered</p>
                    <p className="text-xs text-slate-600">Smart inventory management</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Mobile Header */}
        <div className="lg:hidden bg-white/95 backdrop-blur-sm border-b border-slate-200/50 px-4 py-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">
              {tabs.find(tab => tab.id === activeTab)?.name || 'Dashboard'}
            </h2>
            <button
              onClick={() => setActiveTab('settings')}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all duration-200"
            >
              <SettingsIcon size={20} />
            </button>
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1 p-2 sm:p-4 lg:p-8 overflow-x-hidden pb-20 lg:pb-8">
          <div className="max-w-7xl mx-auto">
            <div className="animate-fade-in">
              {renderContent()}
            </div>
          </div>
        </main>

        {/* Mobile Tab Navigation */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-t border-slate-200/50 z-50">
          <div className="flex">
            {tabs.slice(0, 4).map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex flex-col items-center py-3 px-2 transition-all duration-200 ${
                    isActive 
                      ? 'text-slate-700 bg-slate-100' 
                      : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <Icon size={20} className="mb-1" />
                  <span className="text-xs font-medium">{tab.name.split(' ')[0]}</span>
                </button>
              );
            })}
          </div>
        </div>
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
