'use client';

import { useState } from 'react';
import { Lock, User, Eye, EyeOff, Sparkles, Shield, Zap, ArrowRight, Brain } from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

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
      const response = await fetch(API_ENDPOINTS.AUTH.LOGIN, {
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
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-100/70 rounded-[40%] blur-3xl animate-[blobMorph_14s_ease-in-out_infinite]"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-primary-50/80 rounded-[50%] blur-3xl animate-[blobMorph_18s_ease-in-out_infinite]"></div>
      </div>

      <div className="max-w-md w-full relative z-10">
        <div className="bg-white rounded-3xl shadow-large border border-gray-100 p-8 animate-scale-in">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="relative mx-auto w-24 h-24 mb-6">
              {/* Animated synaptic orb */}
              <div className="pointer-events-none absolute -inset-5 rounded-full bg-primary-200/30 blur-xl" />
              <div className="pointer-events-none absolute -inset-3 rounded-full orb-ring animate-[orbSpin_16s_linear_infinite]" />
              <div className="pointer-events-none absolute inset-0">{
                [0,1,2].map(i => (
                  <span key={i} className="particle absolute w-1.5 h-1.5 rounded-full bg-primary-500" style={{ top: `${28 + i*16}%`, left: `${36 + i*14}%`, animationDelay: `${i*0.25}s` }} />
                ))
              }</div>
              <div className="w-24 h-24 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-medium">
                <img src="/AI-LOGO.png" alt="WODEN AI" className="w-16 h-16 object-contain" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-accent rounded-full animate-bounce-subtle flex items-center justify-center">
                <Zap className="w-3 h-3 text-white" />
              </div>
            </div>
            
            <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 mb-1">WODEN AI</h1>
            <p className="text-gray-600 text-base font-medium">WODEN Stock AI — Inventory, Insights, Scheduling</p>
            <div className="flex items-center justify-center space-x-2 mt-3">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">AI‑Powered System</span>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
                  Username
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400 group-focus-within:text-primary-500 transition-colors duration-200" />
                  </div>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input w-full pl-12 pr-4 py-4 bg-white border-gray-200 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-300 focus:ring-primary-500"
                    placeholder="Enter username"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-primary-500 transition-colors duration-200" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input w-full pl-12 pr-12 py-4 bg-white border-gray-200 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-300 focus:ring-primary-500"
                    placeholder="Enter password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center group/password"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-700 transition-colors duration-200" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-700 transition-colors duration-200" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <p className="text-sm text-red-700 font-medium">{error}</p>
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
            <div className="mt-8 p-4 bg-red-50 rounded-2xl border border-red-200">
              <div className="text-center">
                <div className="flex items-center justify-center space-x-2 mb-3">
                  <Shield className="w-5 h-5 text-red-500" />
                  <p className="text-sm text-gray-800 font-medium">Secure Access Required</p>
                </div>
                <div className="space-y-2">
                  <p className="text-xs text-gray-600">
                    Authorized personnel only. Contact system administrator for access credentials.
                  </p>
                  <div className="text-xs text-gray-600">
                    <p className="text-red-600">⚠️ Security Notice:</p>
                    <p>Credentials are not displayed for security reasons.</p>
                    <p>Please contact your administrator for login details.</p>
                  </div>
                </div>
              </div>
            </div>

          {/* Features */}
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-white rounded-xl border border-gray-100">
              <Brain className="w-6 h-6 text-primary-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600 font-medium">AI Analytics</p>
            </div>
            <div className="p-3 bg-white rounded-xl border border-gray-100">
              <Zap className="w-6 h-6 text-accent-500 mx-auto mb-2" />
              <p className="text-xs text-gray-600 font-medium">Smart Alerts</p>
            </div>
            <div className="p-3 bg-white rounded-xl border border-gray-100">
              <Shield className="w-6 h-6 text-success-500 mx-auto mb-2" />
              <p className="text-xs text-gray-600 font-medium">Secure</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
