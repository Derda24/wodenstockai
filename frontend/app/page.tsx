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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Modern Header */}
      <header className="bg-surface sticky top-0 z-40">
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 opacity-80 bg-gradient-secondary" />
          <div className="absolute -top-28 -right-32 w-80 h-80 blob-bg bg-primary-100/70 blur-3xl" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 blob-bg bg-primary-50/70 blur-3xl" />
        </div>
        <div className="relative flex items-center justify-between px-6 py-6">
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
                  src="/AI-LOGO.png"
                  alt="Woden AI Logo"
                  className="w-12 h-12 rounded-2xl shadow-medium"
                />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-accent rounded-full animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-gray-900">
                  WODEN Stock AI
                </h1>
                <p className="text-xs sm:text-sm lg:text-base text-gray-600 font-medium">AI‑powered inventory, insights, and scheduling</p>
                <div className="mt-3 flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full max-w-sm">
                  <a href="#app" className="btn-primary w-full sm:w-auto">Open App</a>
                  <button onClick={() => setActiveTab('scheduler')} className="btn-secondary w-full sm:w-auto">See Demo</button>
                </div>
                <div className="mt-4 hidden sm:flex flex-wrap items-center gap-2 text-[10px] sm:text-xs text-gray-600">
                  <span className="px-2 py-1 rounded-full bg-white shadow-soft border">Inventory</span>
                  <span className="px-2 py-1 rounded-full bg-white shadow-soft border">Analytics</span>
                  <span className="px-2 py-1 rounded-full bg-white shadow-soft border">Recommendations</span>
                  <span className="px-2 py-1 rounded-full bg-white shadow-soft border">Scheduler</span>
                </div>
              </div>
            </div>
          </div>
          {/* Animated Orb */}
          <div className="block relative w-40 lg:w-56 h-40 lg:h-56 mr-2">
            <div className="absolute inset-0 rounded-full orb-ring animate-[orbSpin_18s_linear_infinite]" />
            <div className="absolute inset-2 rounded-full orb-core shadow-glow" />
            <div className="absolute inset-0">{
              [0,1,2,3,4].map(i => (
                <span key={i} className="particle absolute w-1 h-1 lg:w-1.5 lg:h-1.5 rounded-full bg-primary-500" style={{ top: `${20 + i*12}%`, left: `${30 + i*10}%`, animationDelay: `${i*0.3}s` }} />
              ))
            }</div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-primary-50 rounded-xl border border-primary-200">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-700">AI Active</span>
            </div>
            {/* KPI chips */}
            <div className="hidden lg:flex items-center space-x-2">
              <div className="px-3 py-1.5 rounded-xl bg-white shadow-soft border border-gray-100 text-xs text-gray-700">Baristas: <span className="font-semibold text-gray-900">{kpis.baristas}</span></div>
              <div className="px-3 py-1.5 rounded-xl bg-white shadow-soft border border-gray-100 text-xs text-gray-700">Low Stock: <span className="font-semibold text-danger-600">{kpis.lowStock}</span></div>
              <div className="px-3 py-1.5 rounded-xl bg-white shadow-soft border border-gray-100 text-xs text-gray-700">Coverage: <span className="font-semibold text-primary-700">{kpis.weekCoverage}</span></div>
            </div>
            <button
              onClick={() => setActiveTab('scheduler')}
              className="hidden lg:inline-flex items-center space-x-2 px-5 py-3 rounded-xl text-sm font-semibold text-white bg-primary-500 hover:bg-primary-600 shadow-soft focus:ring-2 focus:ring-primary-500 transition-all"
            >
              <Calendar className="w-4 h-4" />
              <span>Generate AI Schedule</span>
            </button>
            
            <button
              onClick={handleLogout}
              className="hidden lg:flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all duration-200 group"
            >
              <LogOut size={16} className="group-hover:scale-110 transition-transform duration-200" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Value Strip */}
      <section className="bg-surface-light/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {[{
            icon: Box, title: 'Inventory', desc: 'Recipe-based stock'
          },{
            icon: BarChart3, title: 'Analytics', desc: 'Sales insights'
          },{
            icon: Brain, title: 'Recommendations', desc: 'AI suggestions'
          },{
            icon: Calendar, title: 'Scheduler', desc: 'Weekly programming'
          }].map((item, idx) => {
            const Icon = item.icon as any;
            return (
              <div key={idx} className="card rounded-2xl border border-primary-50/40 bg-white/80 backdrop-blur-sm flex items-center space-x-3 p-3 sm:p-4">
                <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-primary-50 flex items-center justify-center">
                  <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-primary-600" />
                </div>
                <div>
                  <div className="text-xs sm:text-sm font-semibold text-gray-800">{item.title}</div>
                  <div className="text-[11px] sm:text-xs text-gray-500">{item.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <div id="app" className="flex flex-col lg:flex-row">
        {/* Modern Sidebar - Hidden on mobile, shown on desktop */}
        <aside className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white/90 backdrop-blur-lg shadow-large lg:shadow-none border-r border-white/20 transform transition-all duration-300 ease-in-out hidden lg:block`}>
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

        {/* Mobile Header */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              {tabs.find(tab => tab.id === activeTab)?.name || 'Dashboard'}
            </h2>
            <button
              onClick={() => setActiveTab('settings')}
              className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
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
        <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
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
                      ? 'text-primary-600 bg-primary-50' 
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
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
