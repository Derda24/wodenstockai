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
      {/* Background with gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
        
        {/* Logo/Image */}
        <div className="absolute inset-0 flex items-center justify-center">
          <img
            src={imageError ? fallbackImageUrl : "/AI-LOGO.png"}
            alt="Woden AI Logo"
            className="w-32 h-32 md:w-48 md:h-48 opacity-30 blur-sm"
            onError={() => setImageError(true)}
            style={{
              filter: 'blur(4px)',
              transform: 'scale(1.1)'
            }}
          />
        </div>
      </div>
      
      {/* Radial gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/20 via-transparent to-black/20" />
      
      {/* Content with enhanced visibility */}
      <div className="relative z-10 text-center text-white px-4 backdrop-blur-sm bg-black/10 rounded-xl p-8">
        <div className="mb-8 animate-pulse">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 text-white drop-shadow-lg">
            WODEN Stock AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-100 drop-shadow">
            Intelligent Inventory Management
          </p>
        </div>

        <div
          className="text-lg font-medium text-gray-100 drop-shadow transition-opacity duration-500"
          style={{ opacity: showLoadingText ? 1 : 0.5 }}
        >
          Loading your dashboard...
        </div>
        
        {/* Loading spinner */}
        <div className="mt-8 flex justify-center">
          <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
        </div>
      </div>
    </div>
  );
} 