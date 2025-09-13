import { useEffect, useState } from 'react';

interface LoadingScreenProps {
  isLoading: boolean;
}

export function LoadingScreen({ isLoading }: LoadingScreenProps) {
  const [showLoadingText, setShowLoadingText] = useState(true);
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setShowLoadingText(prev => !prev);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Fallback image URL in case local image fails to load
  const fallbackImageUrl = "/AI-LOGO.png";

  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden">
      {/* Beautiful gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Subtle pattern overlay */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
      </div>
      
      {/* Main content container */}
      <div className="relative z-10 text-center text-white px-6 py-12">
        {/* AI Logo - Clean and prominent */}
        <div className="mb-12 flex justify-center">
          <div className="relative">
            {/* Glow effect behind logo */}
            <div className="absolute inset-0 bg-white/20 rounded-full blur-xl scale-150 animate-pulse"></div>
            {/* Main logo */}
            <img
              src="/AI-LOGO.png"
              alt="Woden AI Logo"
              className="relative w-32 h-32 md:w-40 md:h-40 rounded-2xl shadow-2xl"
              style={{
                filter: 'drop-shadow(0 0 30px rgba(255, 255, 255, 0.4))'
              }}
            />
          </div>
        </div>
        
        {/* Title and subtitle */}
        <div className="mb-12">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-white drop-shadow-2xl">
            WODEN Stock AI
          </h1>
          <p className="text-xl md:text-3xl text-gray-200 drop-shadow-lg font-light">
            Intelligent Inventory Management
          </p>
        </div>

        {/* Loading text with better animation */}
        <div className="mb-8">
          <div
            className="text-lg md:text-xl font-medium text-gray-200 transition-opacity duration-700"
            style={{ opacity: showLoadingText ? 1 : 0.4 }}
          >
            Loading your dashboard...
          </div>
        </div>
        
        {/* Elegant loading spinner */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
            <div className="absolute inset-0 w-12 h-12 border-4 border-transparent border-t-white/40 rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}}></div>
          </div>
        </div>
      </div>
    </div>
  );
} 