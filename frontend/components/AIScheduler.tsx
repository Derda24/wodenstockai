'use client';

import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Users, 
  Clock, 
  Plus, 
  Edit, 
  Trash2, 
  RefreshCw,
  Settings,
  Download,
  Send,
  CheckCircle,
  AlertTriangle,
  Coffee,
  User,
  Zap,
  Brain,
  BarChart3,
  Target,
  X
} from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

interface Barista {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  type: 'full-time' | 'part-time';
  max_hours: number;
  preferred_shifts: string[];
  skills: string[];
  is_active: boolean;
}

interface Shift {
  id: string;
  barista_id: string;
  day_of_week: number; // 0=Monday, 6=Sunday
  shift_type: 'morning' | 'evening' | 'off' | 'part-time';
  start_time?: string;
  end_time?: string;
  hours: number;
  notes?: string;
}

interface WeeklySchedule {
  id: string;
  week_start: string;
  week_end: string;
  status: 'draft' | 'published' | 'archived';
  created_by: string;
  notes?: string;
  shifts: Shift[];
}

export default function AIScheduler() {
  const [baristas, setBaristas] = useState<Barista[]>([]);
  const [schedules, setSchedules] = useState<WeeklySchedule[]>([]);
  const [currentSchedule, setCurrentSchedule] = useState<WeeklySchedule | null>(null);
  const [currentShifts, setCurrentShifts] = useState<Shift[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeView, setActiveView] = useState<'calendar' | 'baristas' | 'settings'>('calendar');
  const [selectedWeek, setSelectedWeek] = useState(new Date());
  const [error, setError] = useState<string | null>(null);
  const [showPreferences, setShowPreferences] = useState(false);
  const [baristaPreferences, setBaristaPreferences] = useState<{[key: string]: {
    dayOff: number;
    preferredOpening: number[];
    preferredClosing: number[];
  }}>({});

  // Load real data from API
  useEffect(() => {
    loadBaristas();
    loadSchedules();
  }, []);

  const loadBaristas = async () => {
    try {
      setError(null);
      const response = await fetch(API_ENDPOINTS.SCHEDULER.BARISTAS.GET, { method: 'GET', cache: 'no-store' as RequestCache });
      let data: any = null;
      try {
        data = await response.json();
      } catch (e) {
        console.error('Baristas API returned non-JSON response');
      }

      if (Array.isArray(data)) {
        setBaristas(data);
        console.log(`Loaded ${data.length} baristas from API`);
      } else if (response.ok) {
        // ok but unexpected shape
        console.warn('Baristas API ok but unexpected payload, using mock');
        setError('Using mock data - Unexpected API payload');
        loadMockBaristas();
      } else {
        console.error('Failed to load baristas from API, using mock data', { status: response.status });
        setError('Using mock data - API not available');
        loadMockBaristas();
      }
    } catch (error) {
      console.error('Error loading baristas:', error);
      setError('Using mock data - API not available');
      loadMockBaristas();
    } finally {
      setIsLoading(false);
    }
  };

  const loadSchedules = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.SCHEDULER.SCHEDULES.GET);
      if (response.ok) {
        const data = await response.json();
        setSchedules(data);
        // Pick latest schedule (assumes API returns sorted desc by week_start)
        if (Array.isArray(data) && data.length > 0) {
          const latest = data[0];
          setCurrentSchedule(latest);
          // Load its shifts
          if (latest.id) {
            await loadShifts(latest.id);
          }
        }
      }
    } catch (error) {
      console.error('Error loading schedules:', error);
    }
  };

  const loadShifts = async (scheduleId: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.SCHEDULER.SCHEDULES.SHIFTS(scheduleId), { method: 'GET', cache: 'no-store' as RequestCache });
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setCurrentShifts(data as Shift[]);
        }
      }
    } catch (error) {
      console.error('Error loading shifts:', error);
    }
  };

  const loadMockBaristas = () => {
    const mockBaristas: Barista[] = [
      {
        id: '1',
        name: 'Enes',
        email: 'ahmet@woden.com',
        phone: '+90 555 123 4567',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'cashier', 'cleaning'],
        is_active: true
      },
      {
        id: '2',
        name: 'Ahmet',
        email: 'mehmet@woden.com',
        phone: '+90 555 234 5678',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'management'],
        is_active: true
      },
      {
        id: '3',
        name: 'Boran',
        email: 'ayse@woden.com',
        phone: '+90 555 345 6789',
        type: 'part-time',
        max_hours: 25,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cashier'],
        is_active: true
      },
      {
        id: '4',
        name: 'İlker',
        email: 'fatma@woden.com',
        phone: '+90 555 456 7890',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'cashier', 'cleaning'],
        is_active: true
      },
      {
        id: '5',
        name: 'Can',
        email: 'ali@woden.com',
        phone: '+90 555 567 8901',
        type: 'part-time',
        max_hours: 30,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cleaning'],
        is_active: true
      },
      {
        id: '6',
        name: 'Derda',
        email: 'zeynep@woden.com',
        phone: '+90 555 678 9012',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'cashier', 'management'],
        is_active: true
      }
    ];
    setBaristas(mockBaristas);
  };

  const getWeekStart = (date: Date) => {
    const start = new Date(date);
    const day = start.getDay();
    const diff = start.getDate() - day + (day === 0 ? -6 : 1); // Monday
    start.setDate(diff);
    return start;
  };

  const generateAISchedule = async () => {
    // First show preferences if not already shown
    if (!showPreferences) {
      initializePreferences();
      setShowPreferences(true);
      return;
    }

    try {
      setIsLoading(true);
      const weekStart = getWeekStart(selectedWeek).toISOString().split('T')[0];
      
      const formData = new FormData();
      formData.append('week_start', weekStart);
      formData.append('preferences', JSON.stringify(baristaPreferences));
      
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(API_ENDPOINTS.SCHEDULER.SCHEDULES.GENERATE, {
        method: 'POST',
        body: formData,
        headers
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('AI Schedule generated:', result);
        // Reload schedules to show the new one
        if (result?.schedule_id) {
          // Immediately reflect new schedule
          setCurrentSchedule({
            id: result.schedule_id,
            week_start: result.week_start,
            week_end: result.week_end,
            status: 'draft',
            created_by: 'AI Scheduler',
            notes: result.message,
            shifts: []
          } as WeeklySchedule);
        }
        if (Array.isArray(result?.shifts)) {
          setCurrentShifts(result.shifts as Shift[]);
        } else if (result?.schedule_id) {
          await loadShifts(result.schedule_id);
        } else {
          await loadSchedules();
        }
        setShowPreferences(false);
        alert('AI Schedule generated successfully!');
        // Trigger subtle confetti pulse
        try {
          const el = document.createElement('div');
          el.className = 'fixed inset-0 pointer-events-none';
          el.innerHTML = '<div style="position:absolute;inset:0;animation:fadeConfetti 1s ease-out forwards;">\
            <svg width="0" height="0"><defs><filter id="goo"><feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/><feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo"/><feBlend in="SourceGraphic" in2="goo"/></filter></defs></svg>\
          </div>';
          document.body.appendChild(el);
          setTimeout(() => document.body.removeChild(el), 1200);
        } catch {}
      } else {
        const text = await response.text().catch(() => '');
        console.error('Failed to generate schedule', { status: response.status, body: text });
        alert(`Failed to generate schedule (status ${response.status}).`);
      }
    } catch (error) {
      console.error('Error generating schedule:', error);
      alert('Error generating schedule. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getWeekDates = (date: Date) => {
    const start = new Date(date);
    const day = start.getDay();
    const diff = start.getDate() - day + (day === 0 ? -6 : 1); // Monday
    start.setDate(diff);
    
    const dates = [];
    for (let i = 0; i < 7; i++) {
      const current = new Date(start);
      current.setDate(start.getDate() + i);
      dates.push(current);
    }
    return dates;
  };

  const getShiftsForDay = (dayIndex: number) => {
    if (!currentShifts || currentShifts.length === 0) return [] as any[];
    return currentShifts.filter((s: any) => s.day_of_week === dayIndex);
  };

  const getOffBaristasForDay = (dayIndex: number) => {
    const dayShifts = currentShifts.filter((s: any) => s.day_of_week === dayIndex);
    const workingIds = new Set(dayShifts.map((s: any) => s.barista_id));
    return baristas.filter(b => !workingIds.has(b.id));
  };

  const exportScheduleCSV = () => {
    try {
      const dayNamesTr = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar'];
      const headers = ['Gün','Vardiya','Başlangıç','Bitiş','Barista'];
      const rows: string[] = [];
      rows.push(headers.join(','));
      for (let d = 0; d < 7; d++) {
        const shifts = getShiftsForDay(d) as any[];
        shifts.forEach(shift => {
          const barista = getBaristaById(shift.barista_id);
          const shiftName = shift.shift_type === 'morning' ? 'Açılış' : (shift.shift_type === 'evening' ? 'Kapanış' : shift.shift_type);
          const start = (shift.start_time || '').toString().slice(0,5);
          const end = (shift.end_time || '').toString().slice(0,5);
          rows.push([
            dayNamesTr[d],
            shiftName,
            start,
            end,
            (barista?.name || 'Bilinmiyor').replace(/,/g,' ')
          ].join(','));
        });
        // Off list
        const offs = getOffBaristasForDay(d);
        if (offs.length > 0) {
          rows.push([dayNamesTr[d],'İzinli','-','-', offs.map(b=>b.name.replace(/,/g,' ')).join(' / ')].join(','));
        }
      }
      const csvContent = rows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const weekStartStr = currentSchedule?.week_start || getWeekStart(selectedWeek).toISOString().split('T')[0];
      a.download = `weekly_schedule_${weekStartStr}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed:', e);
      alert('Export failed.');
    }
  };

  const getBaristaById = (baristaId: string) => {
    return baristas.find(b => b.id === baristaId);
  };

  const initializePreferences = () => {
    const preferences: {[key: string]: {
      dayOff: number;
      preferredOpening: number[];
      preferredClosing: number[];
    }} = {};
    
    baristas.forEach(barista => {
      preferences[barista.id] = {
        dayOff: -1,
        preferredOpening: [],
        preferredClosing: []
      };
    });
    
    setBaristaPreferences(preferences);
  };

  const updateBaristaPreference = (baristaId: string, type: 'dayOff' | 'preferredOpening' | 'preferredClosing', value: number | number[]) => {
    setBaristaPreferences(prev => ({
      ...prev,
      [baristaId]: {
        ...prev[baristaId],
        [type]: value
      }
    }));
  };

  const toggleDayPreference = (baristaId: string, type: 'preferredOpening' | 'preferredClosing', dayIndex: number) => {
    const current = baristaPreferences[baristaId]?.[type] || [];
    const updated = current.includes(dayIndex) 
      ? current.filter(d => d !== dayIndex)
      : [...current, dayIndex];
    
    updateBaristaPreference(baristaId, type, updated);
  };

  const weekDates = getWeekDates(selectedWeek);
  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="relative mx-auto w-16 h-16 mb-4">
            <div className="loading-spinner w-16 h-16"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Calendar className="w-8 h-8 text-primary-500" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">AI is preparing your scheduler</h3>
          <p className="text-gray-500">Setting up barista management...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Error Banner */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800">Development Mode</h3>
              <p className="text-sm text-yellow-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-purple-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading AI Scheduler...</p>
          </div>
        </div>
      )}

      {/* Main Content - Only show when not loading */}
      {!isLoading && (
        <>
          {/* Modern Header */}
      <div className="relative">
        <div className="flex flex-col space-y-4 lg:flex-row lg:items-center lg:justify-between lg:space-y-0">
          <div className="mb-6 lg:mb-0">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-medium">
                <Calendar className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">AI Scheduler</h1>
                <p className="text-gray-600 text-sm sm:text-lg">Weekly Barista Programming</p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-4">
              <div className="flex items-center space-x-2 px-3 py-1 bg-purple-100 rounded-full">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                <span className="text-xs sm:text-sm font-medium text-purple-700">AI Active</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1 bg-pink-100 rounded-full">
                <Zap className="w-3 h-3 sm:w-4 sm:h-4 text-pink-600" />
                <span className="text-xs sm:text-sm font-medium text-pink-700">Smart Scheduling</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveView('calendar')}
                className={`px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 touch-manipulation min-h-[44px] ${
                  activeView === 'calendar' 
                    ? 'bg-purple-500 text-white shadow-medium' 
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Calendar className="w-4 h-4 mr-2 inline" />
                Schedule
              </button>
              <button
                onClick={() => setActiveView('baristas')}
                className={`px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 touch-manipulation min-h-[44px] ${
                  activeView === 'baristas' 
                    ? 'bg-purple-500 text-white shadow-medium' 
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Users className="w-4 h-4 mr-2 inline" />
                Baristas
              </button>
              <button
                onClick={() => setActiveView('settings')}
                className={`px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 touch-manipulation min-h-[44px] ${
                  activeView === 'settings' 
                    ? 'bg-purple-500 text-white shadow-medium' 
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Settings className="w-4 h-4 mr-2 inline" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-medium">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-blue-600">
                <Coffee className="w-4 h-4" />
                <span className="text-sm font-medium">Active</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Total Baristas</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">{baristas.length}</p>
            <p className="text-xs text-gray-500">Ready to schedule</p>
          </div>
        </div>

        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-medium">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Covered</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Weekly Hours</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">315</p>
            <p className="text-xs text-gray-500">Total coverage</p>
          </div>
        </div>

        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-medium">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-orange-600">
                <Brain className="w-4 h-4" />
                <span className="text-sm font-medium">AI</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Schedules</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">4</p>
            <p className="text-xs text-gray-500">This month</p>
          </div>
        </div>

        <div className="card-elevated group hover:scale-105 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-medium">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 text-purple-600">
                <Zap className="w-4 h-4" />
                <span className="text-sm font-medium">Optimized</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Efficiency</p>
            <p className="text-3xl font-bold text-gray-900 mb-2">94%</p>
            <p className="text-xs text-gray-500">AI optimized</p>
          </div>
        </div>
      </div>

      {/* Preferences Modal */}
      {showPreferences && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Barista Preferences</h3>
                  <p className="text-gray-600 mt-1">Set each barista's preferences for the week</p>
                </div>
                <button
                  onClick={() => setShowPreferences(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-6">
                {baristas.map((barista) => (
                  <div key={barista.id} className="bg-gray-50 rounded-xl p-4">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{barista.name}</h4>
                        <p className="text-sm text-gray-500">{barista.type}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Day Off Selection */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Day Off
                        </label>
                        <select
                          value={baristaPreferences[barista.id]?.dayOff || ''}
                          onChange={(e) => updateBaristaPreference(barista.id, 'dayOff', e.target.value ? parseInt(e.target.value) : -1)}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        >
                          <option value="">Select day off</option>
                          {['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'].map((day, index) => (
                            <option key={index} value={index}>{day}</option>
                          ))}
                        </select>
                      </div>
                      
                      {/* Preferred Opening Days */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Preferred Opening Days
                        </label>
                        <div className="space-y-1">
                          {['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'].map((day, index) => (
                            <label key={index} className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={baristaPreferences[barista.id]?.preferredOpening?.includes(index) || false}
                                onChange={() => toggleDayPreference(barista.id, 'preferredOpening', index)}
                                className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                              />
                              <span className="text-sm text-gray-700">{day}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                      
                      {/* Preferred Closing Days */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Preferred Closing Days
                        </label>
                        <div className="space-y-1">
                          {['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'].map((day, index) => (
                            <label key={index} className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={baristaPreferences[barista.id]?.preferredClosing?.includes(index) || false}
                                onChange={() => toggleDayPreference(barista.id, 'preferredClosing', index)}
                                className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                              />
                              <span className="text-sm text-gray-700">{day}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setShowPreferences(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={generateAISchedule}
                  disabled={isLoading}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? 'Generating...' : 'Generate Schedule'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {activeView === 'calendar' && (
        <div className="card-elevated">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Weekly Schedule</h3>
                <p className="text-sm text-gray-600">AI-powered barista scheduling</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={generateAISchedule}
                disabled={isLoading}
                className="flex items-center space-x-2 px-4 py-3 bg-purple-500 text-white rounded-xl text-sm font-medium shadow-soft hover:bg-purple-600 focus:ring-2 focus:ring-purple-500 transition-all duration-200 touch-manipulation min-h-[44px] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Brain className="w-4 h-4" />
                )}
                <span>{isLoading ? 'Generating...' : 'Generate AI Schedule'}</span>
              </button>
              <button onClick={exportScheduleCSV} className="flex items-center space-x-2 px-4 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl text-sm font-medium shadow-soft hover:bg-gray-50 focus:ring-2 focus:ring-purple-500 transition-all duration-200 touch-manipulation min-h-[44px]">
                <Download className="w-4 h-4" />
                <span>Export CSV</span>
              </button>
            </div>
          </div>

          {/* Weekly Schedule - Days as Columns */}
          <div className="overflow-x-auto">
            <div className="min-w-full">
              {/* Days as columns */}
              <div className="grid grid-cols-7 gap-4">
                {weekDates.map((date, dayIndex) => {
                  const dayName = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'][dayIndex];
                  const shifts = getShiftsForDay(dayIndex);
                  const openingShifts = shifts.filter((s: any) => s.shift_type === 'morning');
                  const closingShifts = shifts.filter((s: any) => s.shift_type === 'evening');
                  const offList = getOffBaristasForDay(dayIndex);
                  
                  return (
                    <div key={dayIndex} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                      {/* Day Header */}
                      <div className="text-center mb-4 pb-3 border-b border-gray-100">
                        <div className="text-lg font-bold text-gray-900">{dayName}</div>
                        <div className="text-sm text-gray-500">{date.getDate()}/{date.getMonth() + 1}</div>
                      </div>
                      
                      {/* Opening Shifts (1 shown + 1 empty slot) */}
                      <div className="mb-4">
                        <div className="text-xs font-semibold text-blue-600 mb-2 uppercase tracking-wide">
                          Açılış (2 kişi)
                        </div>
                        <div className="space-y-2">
                          {openingShifts.slice(0, 1).map((shift: any, idx: number) => {
                            const barista = getBaristaById(shift.barista_id);
                            return (
                              <div key={idx} className="bg-blue-50 rounded-lg p-2 text-sm">
                                <div className="font-medium text-blue-900">{barista?.name || 'Unknown'}</div>
                                <div className="text-blue-700">07:30-16:30</div>
                              </div>
                            );
                          })}
                          {/* Always render second empty slot */}
                          <div className="bg-gray-100 rounded-lg p-2 text-sm text-gray-400 italic">
                            Boş
                          </div>
                        </div>
                      </div>
                      
                      {/* Closing Shifts (3 people) */}
                      <div>
                        <div className="text-xs font-semibold text-green-600 mb-2 uppercase tracking-wide">
                          Kapanış (3 kişi)
                        </div>
                        <div className="space-y-2">
                          {closingShifts.slice(0, 3).map((shift: any, idx: number) => {
                            const barista = getBaristaById(shift.barista_id);
                            return (
                              <div key={idx} className="bg-green-50 rounded-lg p-2 text-sm">
                                <div className="font-medium text-green-900">{barista?.name || 'Unknown'}</div>
                                <div className="text-green-700">15:30-00:30</div>
                              </div>
                            );
                          })}
                          {closingShifts.length < 3 && (
                            <div className="bg-gray-100 rounded-lg p-2 text-sm text-gray-500 italic">
                              {3 - closingShifts.length} kişi daha gerekli
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Off Baristas */}
                      <div className="mt-4 pt-3 border-t border-gray-100">
                        <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                          İzinli
                        </div>
                        {offList.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {offList.map((b) => (
                              <span key={b.id} className="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-700">
                                {b.name}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <div className="text-xs text-gray-400">Yok</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === 'baristas' && (
        <div className="card-elevated">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Barista Management</h3>
                <p className="text-sm text-gray-600">Manage your barista team</p>
              </div>
            </div>
            <button className="flex items-center space-x-2 px-4 py-3 bg-blue-500 text-white rounded-xl text-sm font-medium shadow-soft hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 transition-all duration-200 touch-manipulation min-h-[44px]">
              <Plus className="w-4 h-4" />
              <span>Add Barista</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {baristas.map((barista) => (
              <div key={barista.id} className="p-4 border border-gray-200 rounded-xl hover:shadow-soft transition-all duration-200">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{barista.name}</h4>
                    <p className="text-sm text-gray-500">{barista.type}</p>
                  </div>
                  <div className="flex space-x-1">
                    <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-red-600 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>Max {barista.max_hours}h/week</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Coffee className="w-4 h-4" />
                    <span>{barista.skills.join(', ')}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Target className="w-4 h-4" />
                    <span>Prefers: {barista.preferred_shifts.join(', ')}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeView === 'settings' && (
        <div className="card-elevated">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl flex items-center justify-center">
              <Settings className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Scheduler Settings</h3>
              <p className="text-sm text-gray-600">Configure AI scheduling preferences</p>
            </div>
          </div>

          <div className="space-y-6">
            <div className="p-4 border border-gray-200 rounded-xl">
              <h4 className="font-semibold text-gray-900 mb-3">Operating Hours</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Monday - Saturday</label>
                  <div className="flex items-center space-x-2">
                    <input type="time" defaultValue="07:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                    <span className="text-gray-500">to</span>
                    <input type="time" defaultValue="00:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sunday</label>
                  <div className="flex items-center space-x-2">
                    <input type="time" defaultValue="09:00" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                    <span className="text-gray-500">to</span>
                    <input type="time" defaultValue="00:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border border-gray-200 rounded-xl">
              <h4 className="font-semibold text-gray-900 mb-3">Shift Configuration</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Morning Shift</label>
                  <div className="flex items-center space-x-2">
                    <input type="time" defaultValue="07:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                    <span className="text-gray-500">to</span>
                    <input type="time" defaultValue="16:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Evening Shift</label>
                  <div className="flex items-center space-x-2">
                    <input type="time" defaultValue="15:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                    <span className="text-gray-500">to</span>
                    <input type="time" defaultValue="00:30" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500" />
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border border-gray-200 rounded-xl">
              <h4 className="font-semibold text-gray-900 mb-3">AI Preferences</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Morning before day off rule</span>
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Consider sales data for staffing</span>
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Auto-balance workload</span>
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
}
