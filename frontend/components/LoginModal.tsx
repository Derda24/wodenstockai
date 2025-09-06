'use client';

import { useState } from 'react';
import { Lock, User, Eye, EyeOff, Sparkles, Shield, Zap, ArrowRight, Brain } from 'lucide-react';

interface LoginModalProps {
  onLogin: (success: boolean) => void;
}

export default function LoginModal({ onLogin }: LoginModalProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('https://wodenstockai.onrender.com/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        // Store the token if provided
        if (data.token) {
          localStorage.setItem('authToken', data.token);
        }
        onLogin(true);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Invalid username or password. Only authorized users can access this system.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Connection error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="max-w-md w-full relative z-10">
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 animate-scale-in">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="relative mx-auto w-24 h-24 mb-6">
              <div className="w-24 h-24 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-large">
                <img src="/AI-LOGO.png" alt="WODEN AI" className="w-16 h-16 object-contain" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-accent rounded-full animate-bounce-subtle flex items-center justify-center">
                <Zap className="w-3 h-3 text-white" />
              </div>
            </div>
            
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent mb-2">
              WODEN Stock AI
            </h1>
            <p className="text-gray-300 text-lg font-medium">Intelligent Inventory Management</p>
            <div className="flex items-center justify-center space-x-2 mt-3">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-400">AI-Powered System</span>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-semibold text-gray-200 mb-2">
                  Username
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400 group-focus-within:text-primary-400 transition-colors duration-200" />
                  </div>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input w-full pl-12 pr-4 py-4 bg-white/10 border-white/20 text-white placeholder-gray-400 focus:bg-white/20 focus:border-primary-400 focus:ring-primary-400"
                    placeholder="Enter username"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-200 mb-2">
                  Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-primary-400 transition-colors duration-200" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input w-full pl-12 pr-12 py-4 bg-white/10 border-white/20 text-white placeholder-gray-400 focus:bg-white/20 focus:border-primary-400 focus:ring-primary-400"
                    placeholder="Enter password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center group/password"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-white transition-colors duration-200" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-white transition-colors duration-200" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-red-500/20 border border-red-400/30 rounded-xl p-4 backdrop-blur-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                  <p className="text-sm text-red-200 font-medium">{error}</p>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-4 text-lg font-semibold group relative overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="loading-spinner w-5 h-5"></div>
                  <span>Signing in...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <span>Sign In</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
                </div>
              )}
            </button>
          </form>

          {/* Admin Info */}
          <div className="mt-8 p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-2xl border border-white/10 backdrop-blur-sm">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-3">
                <Shield className="w-5 h-5 text-blue-400" />
                <p className="text-sm text-gray-300 font-medium">Admin Access Required</p>
              </div>
              <div className="space-y-2">
                <p className="text-xs text-gray-400">
                  Authorized users only. Contact system administrator for access.
                </p>
                <div className="text-xs text-gray-500">
                  <p>Demo credentials:</p>
                  <p>Username: <span className="font-mono text-gray-300">derda2412</span></p>
                  <p>Password: <span className="font-mono text-gray-300">woden2025</span></p>
                </div>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-white/5 rounded-xl">
              <Brain className="w-6 h-6 text-primary-400 mx-auto mb-2" />
              <p className="text-xs text-gray-400 font-medium">AI Analytics</p>
            </div>
            <div className="p-3 bg-white/5 rounded-xl">
              <Zap className="w-6 h-6 text-accent-400 mx-auto mb-2" />
              <p className="text-xs text-gray-400 font-medium">Smart Alerts</p>
            </div>
            <div className="p-3 bg-white/5 rounded-xl">
              <Shield className="w-6 h-6 text-success-400 mx-auto mb-2" />
              <p className="text-xs text-gray-400 font-medium">Secure</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
