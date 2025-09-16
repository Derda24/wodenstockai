'use client';

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Lightbulb, 
  Target, 
  BarChart3, 
  Calendar, 
  Star, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Users,
  ArrowUpRight,
  Brain,
  Sparkles,
  Activity,
  PieChart,
  ShoppingCart,
  Award,
  RefreshCw
} from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

interface Recommendation {
  id: string;
  type: 'campaign' | 'product' | 'stock' | 'pricing';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  implementation: string;
  expectedResult: string;
  priority: number;
  category?: string;
  urgency?: 'critical' | 'high' | 'medium' | 'low';
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
  priority?: string;
  category?: string;
}

export default function AIRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [campaigns, setCampaigns] = useState<CampaignSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedTab, setSelectedTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadRecommendations();
    loadCampaigns();
  }, []);

  // Auto-refresh when component becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadRecommendations();
        loadCampaigns();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const loadRecommendations = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.RECOMMENDATIONS.GET);
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      loadMockRecommendations();
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.RECOMMENDATIONS.CAMPAIGNS);
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data.campaigns || []);
      }
    } catch (error) {
      console.error('Error loading campaigns:', error);
      loadMockCampaigns();
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([loadRecommendations(), loadCampaigns()]);
    setRefreshing(false);
  };

  const loadMockRecommendations = () => {
    const mockRecommendations: Recommendation[] = [
      {
        id: '1',
        type: 'campaign',
        title: '☀️ Yaz Kahve Promosyonu',
        description: 'Sıcak aylarda satışları artırmak için dondurulmuş kahve ürünlerine odaklanan yaz temalı bir kampanya başlatın',
        impact: 'high',
        implementation: 'Sosyal medya içeriği oluşturun, dondurulmuş içeceklerde indirim sunun, yeni yaz tatları tanıtın',
        expectedResult: 'Yaz aylarında dondurulmuş kahve satışlarında %25-30 artış bekleniyor',
        priority: 1,
        category: 'pazarlama',
        urgency: 'high'
      },
      {
        id: '2',
        type: 'stock',
        title: '🚨 Acil Stok: Menta Cubano Şurup',
        description: 'Menta Cubano Şurup tamamen tükendi ve acil yeniden stoklanması gerekiyor',
        impact: 'high',
        implementation: 'Menta Cubano Şurup için hemen tedarikçilerden sipariş verin',
        expectedResult: 'İş kesintisini önleyin ve müşteri memnuniyetini koruyun',
        priority: 1,
        category: 'stok',
        urgency: 'critical'
      },
      {
        id: '3',
        type: 'product',
        title: '📈 ICED AMERICANO - Yıldız Ürün',
        description: 'ICED AMERICANO toplam satışların %17.2\'sini oluşturuyor. Bu ürünü daha da büyütmek için özel kampanyalar düşünün',
        impact: 'high',
        implementation: 'ICED AMERICANO için özel promosyonlar, sosyal medya kampanyaları ve müşteri sadakat programları oluşturun',
        expectedResult: 'Bu ürünün satışlarında %20-30 daha artış bekleniyor',
        priority: 1,
        category: 'pazarlama',
        urgency: 'medium'
      }
    ];
    setRecommendations(mockRecommendations);
  };

  const loadMockCampaigns = () => {
    const mockCampaigns: CampaignSuggestion[] = [
      {
        id: '1',
        name: '☀️ Yaz Serinleme Kampanyası',
        description: 'Sıcak aylarda soğuk içecek satışlarını artırmak için özel yaz kampanyası',
        targetProducts: ['ICED AMERICANO', 'ICED FILTER COFFEE', 'COLD BREW', 'ICED LATTE'],
        duration: '3 ay (Haziran-Ağustos)',
        expectedIncrease: 'Soğuk içecek satışlarında %40 artış',
        cost: 'Düşük - Sosyal medya ve in-store promosyonlar',
        status: 'suggested',
        priority: 'high',
        category: 'sezon'
      },
      {
        id: '2',
        name: '🎯 SU Yıldız Kampanyası',
        description: 'SU ürününün başarısını sürdürmek için özel promosyonlar ve pazarlama kampanyaları',
        targetProducts: ['SU'],
        duration: '4 hafta',
        expectedIncrease: 'SU satışlarında %25-40 artış',
        cost: 'Orta - Sosyal medya ve in-store promosyonlar',
        status: 'suggested',
        priority: 'high',
        category: 'pazarlama'
      },
      {
        id: '3',
        name: '🎁 Kombo Paket Kampanyası',
        description: 'En popüler ürünleri birleştirerek kombo paketler oluşturma kampanyası',
        targetProducts: ['SU', 'ICED AMERICANO', 'TÜRK KAHVESİ'],
        duration: 'Sürekli',
        expectedIncrease: 'Ortalama sipariş değerinde %20 artış',
        cost: 'Düşük - Menü düzenlemesi ve fiyatlandırma',
        status: 'suggested',
        priority: 'medium',
        category: 'pazarlama'
      }
    ];
    setCampaigns(mockCampaigns);
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getUrgencyColor = (urgency?: string) => {
    switch (urgency) {
      case 'critical': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getPriorityIcon = (priority: number) => {
    if (priority === 1) return <AlertTriangle className="w-4 h-4 text-red-500" />;
    if (priority === 2) return <Zap className="w-4 h-4 text-orange-500" />;
    return <Target className="w-4 h-4 text-gray-500" />;
  };

  const getCategoryIcon = (category?: string) => {
    switch (category) {
      case 'stok': return <ShoppingCart className="w-4 h-4" />;
      case 'pazarlama': return <TrendingUp className="w-4 h-4" />;
      case 'sezon': return <Calendar className="w-4 h-4" />;
      case 'operasyon': return <Activity className="w-4 h-4" />;
      case 'strateji': return <Target className="w-4 h-4" />;
      default: return <Lightbulb className="w-4 h-4" />;
    }
  };

  const filteredRecommendations = recommendations.filter((rec) => {
    if (selectedFilter === 'all') return true;
    return rec.type === selectedFilter;
  });

  const highPriorityRecommendations = recommendations.filter(r => r.priority === 1);
  const criticalRecommendations = recommendations.filter(r => r.urgency === 'critical');

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
      <div className="flex flex-col space-y-4 lg:flex-row lg:items-center lg:justify-between lg:space-y-0">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">AI Önerileri</h1>
              <p className="text-sm sm:text-base text-gray-600">Verilerinize dayalı akıllı iş önerileri ve kampanya fikirleri</p>
            </div>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 touch-manipulation min-h-[44px]"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Yenile</span>
            <span className="sm:hidden">↻</span>
          </button>
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="w-full sm:w-auto px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 touch-manipulation text-base"
          >
            <option value="all">Tüm Öneriler</option>
            <option value="campaign">Kampanyalar</option>
            <option value="stock">Stok</option>
            <option value="product">Ürünler</option>
            <option value="pricing">Fiyatlandırma</option>
          </select>
        </div>
      </div>

      {/* AI Insights Dashboard */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-4 sm:p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-xs sm:text-sm font-medium">Toplam Öneriler</p>
              <p className="text-2xl sm:text-3xl font-bold">{recommendations.length}</p>
            </div>
            <Lightbulb className="w-6 h-6 sm:w-8 sm:h-8 text-blue-200" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-xl p-4 sm:p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-xs sm:text-sm font-medium">Kritik Öneriler</p>
              <p className="text-2xl sm:text-3xl font-bold">{criticalRecommendations.length}</p>
            </div>
            <AlertTriangle className="w-6 h-6 sm:w-8 sm:h-8 text-red-200" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-4 sm:p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-xs sm:text-sm font-medium">Aktif Kampanyalar</p>
              <p className="text-2xl sm:text-3xl font-bold">{campaigns.length}</p>
            </div>
            <Target className="w-6 h-6 sm:w-8 sm:h-8 text-green-200" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-4 sm:p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-xs sm:text-sm font-medium">Yüksek Öncelik</p>
              <p className="text-2xl sm:text-3xl font-bold">{highPriorityRecommendations.length}</p>
            </div>
            <Star className="w-6 h-6 sm:w-8 sm:h-8 text-purple-200" />
          </div>
        </div>
      </div>

      {/* Critical Alerts */}
      {criticalRecommendations.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 sm:p-6">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-red-600" />
            <h3 className="text-base sm:text-lg font-semibold text-red-900">Kritik Uyarılar</h3>
          </div>
          <div className="space-y-3">
            {criticalRecommendations.map((rec) => (
              <div key={rec.id} className="bg-white border border-red-200 rounded-lg p-4">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between space-y-3 sm:space-y-0">
                  <div className="flex-1">
                    <h4 className="font-semibold text-red-900 text-sm sm:text-base">{rec.title}</h4>
                    <p className="text-red-700 text-xs sm:text-sm mt-1">{rec.description}</p>
                  </div>
                  <button className="w-full sm:w-auto px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors touch-manipulation min-h-[44px]">
                    Hemen Uygula
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Campaign Suggestions */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-6 h-6 text-brand-500" />
            <div>
              <h3 className="text-xl font-bold text-gray-900">Kampanya Önerileri</h3>
              <p className="text-gray-600">AI tarafından verilerinize dayalı olarak üretilen pazarlama kampanyaları</p>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {campaigns && campaigns.length > 0 ? campaigns.map((campaign) => (
              <div key={campaign.id} className="bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-all duration-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    {getCategoryIcon(campaign.category)}
                    <h4 className="font-bold text-gray-900 text-lg">{campaign.name}</h4>
                  </div>
                  <div className="flex space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      campaign.priority === 'high' ? 'bg-red-100 text-red-800' :
                      campaign.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {campaign.priority === 'high' ? 'Yüksek' : campaign.priority === 'medium' ? 'Orta' : 'Düşük'}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      campaign.status === 'suggested' ? 'bg-blue-100 text-blue-800' :
                      campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {campaign.status === 'suggested' ? 'Önerilen' : campaign.status === 'active' ? 'Aktif' : 'Tamamlandı'}
                    </span>
                  </div>
                </div>
                
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">{campaign.description}</p>
                
                <div className="space-y-3 mb-6">
                  <div className="flex items-center space-x-2 text-sm">
                    <Target className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Hedef: </span>
                    <span className="font-medium">{campaign.targetProducts?.join(', ') || 'Tüm Ürünler'}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Süre: </span>
                    <span className="font-medium">{campaign.duration || 'Belirlenecek'}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <TrendingUp className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Beklenen: </span>
                    <span className="font-medium text-green-600">{campaign.expectedIncrease || 'Belirlenecek'}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <DollarSign className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Maliyet: </span>
                    <span className="font-medium">{campaign.cost || 'Belirlenecek'}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="flex-1 bg-gradient-to-r from-brand-500 to-brand-600 text-white px-4 py-2 rounded-lg hover:from-brand-600 hover:to-brand-700 transition-all duration-200 font-medium">
                    Kampanyayı Başlat
                  </button>
                  <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                    Detaylar
                  </button>
                </div>
              </div>
            )) : (
              <div className="col-span-full text-center py-12">
                <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <div className="text-gray-500 text-lg">Kampanya önerisi bulunamadı</div>
                <div className="text-gray-400 text-sm mt-2">Verilerinizi yükleyerek AI önerilerini aktifleştirin</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
          <div className="flex items-center space-x-3">
            <Brain className="w-6 h-6 text-brand-500" />
            <div>
              <h3 className="text-xl font-bold text-gray-900">Stratejik Öneriler</h3>
              <p className="text-gray-600">İş optimizasyonu için AI destekli akıllı öneriler</p>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Öncelik
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Kategori
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Başlık
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Etki
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  İşlemler
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRecommendations && filteredRecommendations.length > 0 ? filteredRecommendations.map((recommendation) => (
                <tr key={recommendation.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getPriorityIcon(recommendation.priority)}
                      <span className="text-sm font-medium text-gray-900">
                        {recommendation.priority === 1 ? 'Kritik' :
                         recommendation.priority === 2 ? 'Yüksek' : 'Orta'}
                      </span>
                      {recommendation.urgency && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUrgencyColor(recommendation.urgency)}`}>
                          {recommendation.urgency === 'critical' ? 'Acil' :
                           recommendation.urgency === 'high' ? 'Yüksek' :
                           recommendation.urgency === 'medium' ? 'Orta' : 'Düşük'}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getCategoryIcon(recommendation.category)}
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {recommendation.category || 'Genel'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-semibold text-gray-900">{recommendation.title || 'Untitled'}</div>
                      <div className="text-sm text-gray-500 mt-1 max-w-md">{recommendation.description || 'No description available'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getImpactColor(recommendation.impact)}`}>
                      {recommendation.impact === 'high' ? 'Yüksek' :
                       recommendation.impact === 'medium' ? 'Orta' : 'Düşük'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-brand-600 hover:text-brand-900 font-medium">
                        Detaylar
                      </button>
                      <button className="text-green-600 hover:text-green-900 font-medium">
                        Uygula
                      </button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="text-center py-12">
                    <Brain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <div className="text-gray-500 text-lg">Öneri bulunamadı</div>
                    <div className="text-gray-400 text-sm mt-2">Verilerinizi yükleyerek AI önerilerini aktifleştirin</div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
          <Activity className="w-6 h-6 text-brand-500" />
          <span>Hızlı İşlemler</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center space-x-3 p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-brand-500 hover:bg-brand-50 transition-all duration-200 group">
            <TrendingUp className="w-8 h-8 text-gray-400 group-hover:text-brand-500" />
            <div className="text-left">
              <div className="font-semibold text-gray-700 group-hover:text-brand-700">Yeni Kampanya Oluştur</div>
              <div className="text-sm text-gray-500">AI destekli kampanya planlama</div>
            </div>
          </button>
          <button className="flex items-center justify-center space-x-3 p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-brand-500 hover:bg-brand-50 transition-all duration-200 group">
            <BarChart3 className="w-8 h-8 text-gray-400 group-hover:text-brand-500" />
            <div className="text-left">
              <div className="font-semibold text-gray-700 group-hover:text-brand-700">Detaylı Rapor Oluştur</div>
              <div className="text-sm text-gray-500">Kapsamlı iş analizi raporu</div>
            </div>
          </button>
          <button className="flex items-center justify-center space-x-3 p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-brand-500 hover:bg-brand-50 transition-all duration-200 group">
            <Calendar className="w-8 h-8 text-gray-400 group-hover:text-brand-500" />
            <div className="text-left">
              <div className="font-semibold text-gray-700 group-hover:text-brand-700">İnceleme Planla</div>
              <div className="text-sm text-gray-500">Stratejik değerlendirme toplantısı</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
