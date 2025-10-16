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
      {/* Teal brand gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-amber-50/30" />
      {/* Morphing blobs */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-primary-100/70 blur-3xl rounded-[40%] animate-[blobMorph_14s_ease-in-out_infinite]" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-primary-50/80 blur-3xl rounded-[50%] animate-[blobMorph_18s_ease-in-out_infinite]" />
      
      {/* Main content container */}
      <div className="relative z-10 text-center px-6 py-12">
        {/* AI Logo - Clean and prominent */}
        <div className="mb-12 flex justify-center">
          <div className="relative">
            {/* Orb ring */}
            <div className="absolute -inset-6 rounded-full orb-ring animate-[orbSpin_16s_linear_infinite]" />
            {/* Main logo */}
            <img src="/woden-logo-premium.svg" alt="Woden AI Logo" className="relative w-32 h-32 md:w-40 md:h-40 rounded-2xl shadow-2xl" />
          </div>
        </div>
        
        {/* Title and subtitle */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
            WODEN Stock AI
          </h1>
          <p className="text-lg md:text-2xl text-gray-600 font-medium">
            Intelligent Inventory Management
          </p>
        </div>

        {/* Loading text with better animation */}
        <div className="mb-8">
          <div
            className="text-base md:text-lg font-medium text-gray-700 transition-opacity duration-700"
            style={{ opacity: showLoadingText ? 1 : 0.4 }}
          >
            Loading your dashboard...
          </div>
        </div>
        
        {/* Elegant loading spinner */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
            <div className="absolute inset-0 w-12 h-12 border-4 border-transparent border-t-primary-300 rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}}></div>
          </div>
        </div>
      </div>
    </div>
  );
} 