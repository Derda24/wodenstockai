'use client';

import { useState } from 'react';
import { Lock, User, Eye, EyeOff } from 'lucide-react';

interface LoginModalProps {
  onLogin: (success: boolean) => void;
}

// Admin users - only these 2 can access
const ADMIN_USERS = [
  { username: 'derda2412', password: 'woden2025' },
  { username: 'caner0119', password: 'stock2025' }
];

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

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Check credentials
    const isValidUser = ADMIN_USERS.some(
      user => user.username === username && user.password === password
    );

    if (isValidUser) {
      onLogin(true);
    } else {
      setError('Invalid username or password. Only authorized users can access this system.');
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-brand-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
                 {/* Logo and Title */}
         <div className="text-center mb-8">
           <div className="mx-auto w-24 h-24 bg-white rounded-full shadow-lg flex items-center justify-center mb-4">
             <img src="/AI-LOGO.png" alt="WODEN AI" className="w-16 h-16" />
           </div>
           <h1 className="text-3xl font-bold text-brand-500 mb-2">WODEN Stock AI</h1>
           <p className="text-gray-600">Intelligent Stock Management System</p>
         </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-6">
            <div className="mx-auto w-12 h-12 bg-brand-100 rounded-full flex items-center justify-center mb-3">
              <Lock className="w-6 h-6 text-brand-500" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Admin Access</h2>
            <p className="text-sm text-gray-600 mt-1">Enter your credentials to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-colors"
                  placeholder="Enter username"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-colors"
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-brand-500 text-white py-3 px-4 rounded-lg font-medium hover:bg-brand-600 focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Admin Info */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="text-center">
              <p className="text-xs text-gray-500">
                Authorized users only. Contact system administrator for access.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
