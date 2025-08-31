'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, Lightbulb, Target, BarChart3, Calendar, Star, Zap } from 'lucide-react';

interface Recommendation {
  id: string;
  type: 'campaign' | 'product' | 'stock' | 'pricing';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  implementation: string;
  expectedResult: string;
  priority: number;
}

interface CampaignSuggestion {
  id: string;
  name: string;
  description: string;
  targetProducts: string[];
  duration: string;
  expectedIncrease: string;
  cost: string;
  status: 'suggested' | 'active' | 'completed';
}

export default function AIRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [campaigns, setCampaigns] = useState<CampaignSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    loadRecommendations();
    loadCampaigns();
  }, []);

     const loadRecommendations = async () => {
     try {
       const response = await fetch('https://wodenstockai.onrender.com/api/recommendations');
       if (response.ok) {
         const data = await response.json();
         setRecommendations(data.recommendations || []);
       }
     } catch (error) {
       console.error('Error loading recommendations:', error);
       // Load mock data for demo
       loadMockRecommendations();
     }
   };

   const loadCampaigns = async () => {
     try {
       const response = await fetch('https://wodenstockai.onrender.com/api/campaigns');
       if (response.ok) {
         const data = await response.json();
         setCampaigns(data.campaigns || []);
       }
     } catch (error) {
       console.error('Error loading campaigns:', error);
       // Load mock data for demo
       loadMockCampaigns();
     } finally {
       setIsLoading(false);
     }
   };

  const loadMockRecommendations = () => {
    const mockRecommendations: Recommendation[] = [
      {
        id: '1',
        type: 'campaign',
        title: 'Summer Coffee Promotion',
        description: 'Launch a summer-themed campaign focusing on iced coffee products to boost sales during hot months.',
        impact: 'high',
        implementation: 'Create social media content, offer discounts on iced beverages, introduce new summer flavors.',
        expectedResult: 'Expected 25-30% increase in iced coffee sales during summer months.',
        priority: 1
      },
      {
        id: '2',
        type: 'stock',
        title: 'Optimize Torku Süt Inventory',
        description: 'Torku Süt is used in 37 recipes and has high consumption. Consider increasing stock levels.',
        impact: 'high',
        implementation: 'Increase minimum stock level from current to 20% higher, set up automatic reorder alerts.',
        expectedResult: 'Prevent stockouts and maintain smooth operations.',
        priority: 1
      },
      {
        id: '3',
        type: 'product',
        title: 'Introduce New Tea Varieties',
        description: 'Based on SİYAH ÇAY popularity, consider adding premium tea options and herbal varieties.',
        impact: 'medium',
        implementation: 'Research suppliers, test new flavors, create marketing materials for tea category.',
        expectedResult: 'Expand customer base and increase average order value.',
        priority: 2
      },
      {
        id: '4',
        type: 'pricing',
        title: 'Bundle Pricing Strategy',
        description: 'Create combo deals for frequently ordered items like coffee + pastry combinations.',
        impact: 'medium',
        implementation: 'Analyze order patterns, design attractive bundles, create promotional materials.',
        expectedResult: 'Increase average order value by 15-20%.',
        priority: 3
      }
    ];
    setRecommendations(mockRecommendations);
  };

  const loadMockCampaigns = () => {
    const mockCampaigns: CampaignSuggestion[] = [
      {
        id: '1',
        name: 'Iced Coffee Summer Blitz',
        description: 'Promote iced coffee products with refreshing summer themes and special pricing.',
        targetProducts: ['ICED AMERICANO', 'ICED FILTER COFFEE', 'COLD BREW'],
        duration: '3 months (June-August)',
        expectedIncrease: '30% in cold beverage sales',
        cost: 'Low - mainly social media and in-store promotion',
        status: 'suggested'
      },
      {
        id: '2',
        name: 'Turkish Coffee Heritage',
        description: 'Celebrate Turkish coffee culture with traditional brewing demonstrations and special events.',
        targetProducts: ['TÜRK KAHVESİ', 'FİLTRE KAHVE'],
        duration: '2 weeks',
        expectedIncrease: '25% in traditional coffee sales',
        cost: 'Medium - event planning and marketing materials',
        status: 'suggested'
      },
      {
        id: '3',
        name: 'Weekend Brunch Special',
        description: 'Create weekend brunch packages combining coffee with breakfast items.',
        targetProducts: ['ESPRESSO', 'LATTE', 'AMERİCANO', 'POĞAÇA'],
        duration: 'Ongoing (weekends)',
        expectedIncrease: '40% in weekend morning sales',
        cost: 'Low - menu adjustments and staff training',
        status: 'suggested'
      }
    ];
    setCampaigns(mockCampaigns);
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityIcon = (priority: number) => {
    if (priority === 1) return <Star className="w-4 h-4 text-yellow-500" />;
    if (priority === 2) return <Zap className="w-4 h-4 text-blue-500" />;
    return <Target className="w-4 h-4 text-gray-500" />;
  };

  const filteredRecommendations = recommendations.filter((rec: { type: any; }) => {
    if (selectedFilter === 'all') return true;
    return rec.type === selectedFilter;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                 <div>
           <h1 className="text-2xl font-bold text-gray-900">AI Önerileri</h1>
           <p className="text-gray-600 mt-1">İş büyümesi ve optimizasyon için akıllı öneriler</p>
         </div>
        <div className="mt-4 sm:mt-0">
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="block px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
          >
                         <option value="all">Tüm Öneriler</option>
             <option value="campaign">Kampanya Fikirleri</option>
             <option value="product">Ürün Önerileri</option>
             <option value="stock">Stok Optimizasyonu</option>
             <option value="pricing">Fiyatlandırma Stratejileri</option>
          </select>
        </div>
      </div>

      {/* AI Insights Summary */}
      <div className="bg-gradient-to-r from-brand-500 to-brand-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <Lightbulb className="w-8 h-8" />
                     <h2 className="text-xl font-bold">AI İş İçgörüleri</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
                         <div className="text-2xl font-bold">{recommendations.length}</div>
             <div className="text-brand-100">Aktif Öneriler</div>
           </div>
           <div className="text-center">
             <div className="text-2xl font-bold">{campaigns.length}</div>
             <div className="text-brand-100">Kampanya Önerileri</div>
           </div>
           <div className="text-center">
             <div className="text-2xl font-bold">
               {recommendations.filter(r => r.impact === 'high').length}
             </div>
             <div className="text-brand-100">Yüksek Etkili Fikirler</div>
          </div>
        </div>
      </div>

      {/* Campaign Suggestions */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
                     <h3 className="text-lg font-semibold text-gray-900">Kampanya Önerileri</h3>
           <p className="text-sm text-gray-600">Verilerinize dayalı AI tarafından üretilen pazarlama kampanyası fikirleri</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns && campaigns.length > 0 ? campaigns.map((campaign) => (
              <div key={campaign.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{campaign.name}</h4>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    campaign.status === 'suggested' ? 'bg-blue-100 text-blue-800' :
                    campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {campaign.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{campaign.description}</p>
                <div className="space-y-2 text-sm">
                                     <div><span className="font-medium">Hedef:</span> {campaign.targetProducts?.join(', ') || 'Tüm Ürünler'}</div>
                   <div><span className="font-medium">Süre:</span> {campaign.duration || 'Belirlenecek'}</div>
                   <div><span className="font-medium">Beklenen:</span> {campaign.expectedIncrease || 'Belirlenecek'}</div>
                   <div><span className="font-medium">Maliyet:</span> {campaign.cost || 'Belirlenecek'}</div>
                </div>
                <div className="mt-4 flex space-x-2">
                                     <button className="flex-1 bg-brand-500 text-white px-3 py-2 rounded text-sm hover:bg-brand-600 transition-colors">
                     Kampanyayı Başlat
                   </button>
                   <button className="px-3 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors">
                     Detaylar
                   </button>
                </div>
              </div>
            )) : (
                             <div className="col-span-full text-center py-8">
                 <div className="text-gray-400 text-sm">Kampanya önerisi bulunamadı</div>
               </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
                     <h3 className="text-lg font-semibold text-gray-900">Stratejik Öneriler</h3>
           <p className="text-sm text-gray-600">İş optimizasyonu için AI destekli öneriler</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Öncelik
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Tür
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Başlık
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   Etki
                 </th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                   İşlemler
                 </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRecommendations && filteredRecommendations.length > 0 ? filteredRecommendations.map((recommendation) => (
                <tr key={recommendation.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getPriorityIcon(recommendation.priority)}
                      <span className="text-sm font-medium text-gray-900">
                                                 {recommendation.priority === 1 ? 'Kritik' :
                          recommendation.priority === 2 ? 'Önemli' : 'İyi Olur'}
                      </span>
                    </div>
                  </td>
                                     <td className="px-6 py-4 whitespace-nowrap">
                     <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                       {recommendation.type?.replace(/\b\w/g, (l: string) => l.toUpperCase()) || 'Unknown'}
                     </span>
                   </td>
                  <td className="px-6 py-4">
                    <div>
                                             <div className="text-sm font-medium text-gray-900">{recommendation.title || 'Untitled'}</div>
                       <div className="text-sm text-gray-500 mt-1">{recommendation.description || 'No description available'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getImpactColor(recommendation.impact)}`}>
                      {recommendation.impact.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                                             <button className="text-brand-600 hover:text-brand-900">Detayları Gör</button>
                       <button className="text-green-600 hover:text-green-900">Uygula</button>
                    </div>
                  </td>
                </tr>
              )) : (
                                 <tr>
                   <td colSpan={5} className="text-center py-8">
                     <div className="text-gray-400 text-sm">Öneri bulunamadı</div>
                   </td>
                 </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
                 <h3 className="text-lg font-semibold text-gray-900 mb-4">Hızlı İşlemler</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-brand-500 hover:bg-brand-50 transition-colors">
            <TrendingUp className="w-6 h-6 text-gray-400" />
                         <span className="text-gray-600">Yeni Kampanya Oluştur</span>
           </button>
           <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-brand-500 hover:bg-brand-50 transition-colors">
             <BarChart3 className="w-6 h-6 text-gray-400" />
             <span className="text-gray-600">Rapor Oluştur</span>
           </button>
           <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-brand-500 hover:bg-brand-50 transition-colors">
             <Calendar className="w-6 h-6 text-gray-400" />
             <span className="text-gray-600">İnceleme Planla</span>
          </button>
        </div>
      </div>
    </div>
  );
}
