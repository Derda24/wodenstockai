'use client';

import { useState } from 'react';
import { 
  Box, 
  BarChart3, 
  TrendingUp, 
  Settings as SettingsIcon, 
  Upload,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import StockList from '@/components/StockList';
import AIAnalysis from '@/components/AIAnalysis';
import AIRecommendations from '@/components/AIRecommendations';
import Settings from '@/components/Settings';
import LoginModal from '@/components/LoginModal';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('stock');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLogin, setShowLogin] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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

  if (!isAuthenticated) {
    return <LoginModal onLogin={handleLogin} />;
  }

  const tabs = [
    { id: 'stock', name: 'Stock List', icon: Box },
    { id: 'analysis', name: 'AI Analysis', icon: BarChart3 },
    { id: 'recommendations', name: 'AI Recommendations', icon: TrendingUp },
    { id: 'settings', name: 'Settings', icon: SettingsIcon },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'stock':
        return <StockList />;
      case 'analysis':
        return <AIAnalysis />;
      case 'recommendations':
        return <AIRecommendations />;
      case 'settings':
        return <Settings />;
      default:
        return <StockList />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
                         <div className="flex items-center space-x-3">
               <img src="/logo.svg" alt="WODEN AI" className="h-10 w-10" />
               <h1 className="text-xl font-bold text-brand-500">WODEN Stock AI</h1>
             </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white shadow-lg lg:shadow-none border-r border-gray-200 transform transition-transform duration-200 ease-in-out`}>
          <nav className="mt-8 px-4">
            <ul className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <li key={tab.id}>
                    <button
                      onClick={() => {
                        setActiveTab(tab.id);
                        setIsSidebarOpen(false);
                      }}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors duration-200 ${
                        activeTab === tab.id
                          ? 'bg-brand-500 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <Icon size={20} />
                      <span className="font-medium">{tab.name}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>

      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}
