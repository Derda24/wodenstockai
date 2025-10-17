'use client';

import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import { Workbook } from 'exceljs';
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
  const [draggedBarista, setDraggedBarista] = useState<string | null>(null);
  const [draggedShift, setDraggedShift] = useState<string | null>(null);
  const [dragOverBarista, setDragOverBarista] = useState<string | null>(null);
  const [draggedEvent, setDraggedEvent] = useState<string | null>(null);
  const [dragOverDay, setDragOverDay] = useState<string | null>(null);
  const [manualSchedule, setManualSchedule] = useState<{[key: string]: {
    openings: string[];
    closings: string[];
    off: string[];
  }}>({});
  
  const [baristaShifts, setBaristaShifts] = useState<{[key: string]: {[shiftType: string]: string}}>({});
  const [dayEvents, setDayEvents] = useState<{[key: string]: string[]}>({});

  // Available shift times
  const shiftTimes = [
    '07:30-16:30',
    '07:30-15:30', 
    '15:30-00:30',
    '17:30-00:30',
    '18:30-00:30',
    '19:30-00:30'
  ];

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
        name: 'Derda',
        email: 'derda@woden.com',
        phone: '+90 555 123 4567',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'cashier', 'management'],
        is_active: true
      },
      {
        id: '2',
        name: 'Ahmet',
        email: 'ahmet@woden.com',
        phone: '+90 555 234 5678',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'management'],
        is_active: true
      },
      {
        id: '3',
        name: 'İlker',
        email: 'ilker@woden.com',
        phone: '+90 555 345 6789',
        type: 'full-time',
        max_hours: 45,
        preferred_shifts: ['morning', 'evening'],
        skills: ['coffee', 'cashier', 'cleaning'],
        is_active: true
      },
      {
        id: '4',
        name: 'Boran',
        email: 'boran@woden.com',
        phone: '+90 555 456 7890',
        type: 'part-time',
        max_hours: 25,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cashier'],
        is_active: true
      },
      {
        id: '5',
        name: 'Bedi',
        email: 'bedi@woden.com',
        phone: '+90 555 567 8901',
        type: 'part-time',
        max_hours: 25,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cashier'],
        is_active: true
      },
      {
        id: '6',
        name: 'Emin',
        email: 'emin@woden.com',
        phone: '+90 555 678 9012',
        type: 'part-time',
        max_hours: 25,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cleaning'],
        is_active: true
      },
      {
        id: '7',
        name: 'Özge',
        email: 'ozge@woden.com',
        phone: '+90 555 789 0123',
        type: 'part-time',
        max_hours: 20,
        preferred_shifts: ['morning'],
        skills: ['coffee', 'cashier'],
        is_active: true
      },
      {
        id: '8',
        name: 'Sultan',
        email: 'sultan@woden.com',
        phone: '+90 555 890 1234',
        type: 'part-time',
        max_hours: 20,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cleaning'],
        is_active: true
      },
      {
        id: '9',
        name: 'Can',
        email: 'can@woden.com',
        phone: '+90 555 901 2345',
        type: 'part-time',
        max_hours: 20,
        preferred_shifts: ['evening'],
        skills: ['coffee', 'cleaning'],
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

  // Removed AI schedule generation - now using drag and drop interface

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
      const sep = ';'; // Excel-friendly in many locales
      const quote = (v: any) => '"' + String(v ?? '').replace(/"/g, '""') + '"';
      const headers = ['Gün','Tarih','Vardiya','Saat','Barista','Tür'];
      const rows: string[] = [];
      rows.push(headers.map(quote).join(sep));
      for (let d = 0; d < 7; d++) {
        const date = getWeekDates(selectedWeek)[d];
        const dateStr = `${date.getDate().toString().padStart(2,'0')}.${(date.getMonth()+1).toString().padStart(2,'0')}.${date.getFullYear()}`;
        const shifts = getShiftsForDay(d) as any[];
        // Ensure deterministic order: opening first then closing
        const opening = shifts.filter(s => s.shift_type === 'morning');
        const closing = shifts.filter(s => s.shift_type === 'evening');
        const ordered = [
          ...opening.map(s => ({...s, label: 'Açılış'})),
          ...closing.map(s => ({...s, label: 'Kapanış'})),
        ];
        ordered.forEach(shift => {
          const barista = getBaristaById(shift.barista_id);
          const start = (shift.start_time || '').toString().slice(0,5);
          const end = (shift.end_time || '').toString().slice(0,5);
          rows.push([
            quote(dayNamesTr[d]),
            quote(dateStr),
            quote(shift.label),
            quote(`${start}-${end}`),
            quote(barista?.name || 'Bilinmiyor'),
            quote(barista?.type || '-')
          ].join(sep));
        });
        // Off list
        const offs = getOffBaristasForDay(d);
        if (offs.length > 0) {
          rows.push([
            quote(dayNamesTr[d]),
            quote(dateStr),
            quote('İzinli'),
            quote('-'),
            quote(offs.map(b=>b.name).join(' / ')),
            quote('-')
          ].join(sep));
        }
      }
      // Prepend UTF-8 BOM so Excel renders Turkish characters correctly
      const csvContent = '\ufeff' + rows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const weekStartStr = currentSchedule?.week_start || getWeekStart(selectedWeek).toISOString().split('T')[0];
      a.download = `haftalik_vardiya_${weekStartStr}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed:', e);
      alert('Export failed.');
    }
  };

  const exportScheduleXLSX = () => {
    try {
      const wb = XLSX.utils.book_new();
      // Pretty grouped layout, single column lines per your sample
      const wsData: any[] = [];
      const trDays = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar'];
      for (let d = 0; d < 7; d++) {
        const date = getWeekDates(selectedWeek)[d];
        const dateStr = `${date.getDate().toString().padStart(2,'0')}.${(date.getMonth()+1).toString().padStart(2,'0')}.${date.getFullYear()}`;
        const shifts = getShiftsForDay(d) as any[];
        const opening = shifts.filter(s => s.shift_type === 'morning');
        const closing = shifts.filter(s => s.shift_type === 'evening');
        wsData.push([`Tarih - ${dateStr}`]);
        wsData.push([`Gün - ${trDays[d]}`]);
        opening.forEach(s => {
          const b = getBaristaById(s.barista_id);
          wsData.push([`Açılış - ${b?.name || 'Bilinmiyor'}`]);
        });
        closing.forEach(s => {
          const b = getBaristaById(s.barista_id);
          wsData.push([`Kapanış - ${b?.name || 'Bilinmiyor'}`]);
        });
        const offs = getOffBaristasForDay(d);
        if (offs.length > 0) {
          wsData.push([`İzinli - ${offs.map(b=>b.name).join(' / ')}`]);
        }
        wsData.push(['']);
      }
      const ws = XLSX.utils.aoa_to_sheet(wsData);
      (ws as any)['!cols'] = [ { wch: 40 } ];
      XLSX.utils.book_append_sheet(wb, ws, 'Haftalık Vardiya');
      const weekStartStr = currentSchedule?.week_start || getWeekStart(selectedWeek).toISOString().split('T')[0];
      XLSX.writeFile(wb, `haftalik_vardiya_${weekStartStr}.xlsx`);
    } catch (e) {
      console.error('Export XLSX failed:', e);
      alert('Excel dışa aktarımı başarısız oldu.');
    }
  };

  const exportStyledExcel = async () => {
    try {
      const wb = new Workbook();
      const ws = wb.addWorksheet('Haftalık Vardiya');

      // Column widths: first label col + 7 days
      ws.columns = [{ width: 18 }, { width: 20 }, { width: 20 }, { width: 20 }, { width: 20 }, { width: 20 }, { width: 20 }, { width: 20 }];

      const weekDatesArr = getWeekDates(selectedWeek);
      const dateStrings = weekDatesArr.map(d => `${d.getDate().toString().padStart(2,'0')}.${(d.getMonth()+1).toString().padStart(2,'0')}.${d.getFullYear()}`);
      const trDays = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar'];

      // Header row: Tarih
      const headerRow = ws.addRow(['Tarih', ...dateStrings]);
      headerRow.eachCell((cell, col) => {
        cell.font = { bold: true };
        cell.alignment = { horizontal: col === 1 ? 'left' : 'center', vertical: 'middle' };
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE8EEF7' } };
        cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
      });

      // Row: Gün
      const dayRow = ws.addRow(['Gün', ...trDays]);
      dayRow.eachCell((cell) => {
        cell.font = { bold: true };
        cell.alignment = { horizontal: 'center', vertical: 'middle' };
        cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
      });

      // Prepare shift rows
      const openLabelRows = ['Açılış /Saat', 'Açılış /Saat'];
      const closeLabelRows = ['Kapanış/Saat', 'Kapanış/Saat', 'Kapanış/Saat', 'Kapanış/Saat'];

      const openingFill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE3F2FD' } } as const; // light blue
      const closingFill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE8F5E9' } } as const; // light green

      const addDataRow = (label: string, values: string[], fill?: any) => {
        const row = ws.addRow([label, ...values]);
        row.eachCell((cell, col) => {
          cell.alignment = { vertical: 'middle', horizontal: col === 1 ? 'left' : 'left', wrapText: true };
          cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
          if (col !== 1 && fill) cell.fill = fill;
        });
      };

      // Build opening rows
      for (let i = 0; i < openLabelRows.length; i++) {
        const vals: string[] = [];
        for (let d = 0; d < 7; d++) {
          const shifts = getShiftsForDay(d) as any[];
          const opening = shifts.filter(s => s.shift_type === 'morning');
          const s = opening[i];
          if (s) {
            const b = getBaristaById(s.barista_id);
            const start = (s.start_time || '07:30').toString().slice(0,5);
            const end = (s.end_time || '16:30').toString().slice(0,5);
            vals.push(`Açılış - ${b?.name || 'Bilinmiyor'}/${start}-${end}`);
          } else {
            vals.push('');
          }
        }
        addDataRow(openLabelRows[i], vals, openingFill);
      }

      // Build closing rows
      for (let i = 0; i < closeLabelRows.length; i++) {
        const vals: string[] = [];
        for (let d = 0; d < 7; d++) {
          const shifts = getShiftsForDay(d) as any[];
          const closing = shifts.filter(s => s.shift_type === 'evening');
          const s = closing[i];
          if (s) {
            const b = getBaristaById(s.barista_id);
            const start = (s.start_time || '15:30').toString().slice(0,5);
            const end = (s.end_time || '00:30').toString().slice(0,5);
            vals.push(`Kapanış - ${b?.name || 'Bilinmiyor'}/${start}-${end}`);
          } else {
            vals.push('');
          }
        }
        addDataRow(closeLabelRows[i], vals, closingFill);
      }

      // Off row
      const offVals: string[] = [];
      for (let d = 0; d < 7; d++) {
        const offs = getOffBaristasForDay(d);
        offVals.push(offs.map(b => b.name).join(' / '));
      }
      addDataRow('İzinli', offVals);

      // Freeze top two rows
      ws.views = [{ state: 'frozen', xSplit: 1, ySplit: 2 }];

      const weekStartStr = currentSchedule?.week_start || getWeekStart(selectedWeek).toISOString().split('T')[0];
      const buffer = await wb.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `haftalik_vardiya_${weekStartStr}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Styled export failed:', e);
      alert('Excel dışa aktarımı başarısız oldu.');
    }
  };

  const getBaristaById = (baristaId: string) => {
    // First try to find by ID, then by name (fallback)
    return baristas.find(b => b.id === baristaId) || baristas.find(b => b.name === baristaId);
  };

  // Removed preference functions - now using drag and drop interface

  // Drag and Drop Functions
  const handleDragStart = (e: React.DragEvent, baristaName: string) => {
    setDraggedBarista(baristaName);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleShiftDragStart = (e: React.DragEvent, shiftTime: string) => {
    setDraggedShift(shiftTime);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleEventDragStart = (e: React.DragEvent, eventName: string) => {
    setDraggedEvent(eventName);
    e.dataTransfer.effectAllowed = 'copy';
  };

  const handleEventDragEnd = (e: React.DragEvent) => {
    setDraggedEvent(null);
    setDragOverDay(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, dayIndex: number, shiftType: 'openings' | 'closings' | 'off') => {
    e.preventDefault();
    if (!draggedBarista) return;

    const dayKey = dayIndex.toString();
    setManualSchedule(prev => {
      const newSchedule = { ...prev };
      if (!newSchedule[dayKey]) {
        newSchedule[dayKey] = { openings: [], closings: [], off: [] };
      }

      // Check if this barista is already in this specific shift
      const isAlreadyInThisShift = newSchedule[dayKey][shiftType].includes(draggedBarista);
      
      if (!isAlreadyInThisShift) {
        // Add to new position (allow multiple assignments of same barista)
        newSchedule[dayKey][shiftType].push(draggedBarista);
      }

      return newSchedule;
    });

    setDraggedBarista(null);
  };

  const handleBaristaDragOver = (e: React.DragEvent, baristaName: string) => {
    e.preventDefault();
    if (draggedShift) {
      setDragOverBarista(baristaName);
      e.dataTransfer.dropEffect = 'copy';
    }
  };

  const handleBaristaDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOverBarista(null);
  };

  const handleDayDragOver = (e: React.DragEvent, dayKey: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (draggedEvent) {
      setDragOverDay(dayKey);
      e.dataTransfer.dropEffect = 'copy';
    }
  };

  const handleDayDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOverDay(null);
  };

  const handleBaristaDrop = (e: React.DragEvent, baristaName: string, shiftType?: string) => {
    e.preventDefault();
    if (!draggedShift) return;

    console.log(`Dropping shift ${draggedShift} on barista ${baristaName} for shift type ${shiftType}`); // Debug log

    setBaristaShifts(prev => ({
      ...prev,
      [baristaName]: {
        ...prev[baristaName],
        [shiftType || 'default']: draggedShift
      }
    }));

    setDraggedShift(null);
    setDragOverBarista(null);
  };

  const handleDayDrop = (e: React.DragEvent, dayKey: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (!draggedEvent) return;

    console.log(`Dropping event ${draggedEvent} on day ${dayKey}`); // Debug log

    setDayEvents(prev => {
      const currentEvents = prev[dayKey] || [];
      // Check if event already exists on this day
      if (currentEvents.includes(draggedEvent)) {
        console.log(`Event ${draggedEvent} already exists on day ${dayKey}`);
        return prev;
      }
      
      return {
        ...prev,
        [dayKey]: [...currentEvents, draggedEvent]
      };
    });

    setDraggedEvent(null);
    setDragOverDay(null);
  };

  const removeEventFromDay = (dayKey: string, eventName: string) => {
    setDayEvents(prev => ({
      ...prev,
      [dayKey]: (prev[dayKey] || []).filter(event => event !== eventName)
    }));
  };

  const removeShiftFromBarista = (baristaName: string, shiftType?: string) => {
    setBaristaShifts(prev => {
      const newShifts = { ...prev };
      if (shiftType) {
        if (newShifts[baristaName]) {
          delete newShifts[baristaName][shiftType];
          if (Object.keys(newShifts[baristaName]).length === 0) {
            delete newShifts[baristaName];
          }
        }
      } else {
        delete newShifts[baristaName];
      }
      return newShifts;
    });
  };

  const removeFromSchedule = (baristaName: string, dayIndex: number, shiftType: 'openings' | 'closings' | 'off') => {
    const dayKey = dayIndex.toString();
    setManualSchedule(prev => {
      const newSchedule = { ...prev };
      if (newSchedule[dayKey]) {
        if (shiftType === 'openings') {
          newSchedule[dayKey].openings = newSchedule[dayKey].openings.filter(name => name !== baristaName);
        } else if (shiftType === 'closings') {
          newSchedule[dayKey].closings = newSchedule[dayKey].closings.filter(name => name !== baristaName);
        } else if (shiftType === 'off') {
          newSchedule[dayKey].off = newSchedule[dayKey].off.filter(name => name !== baristaName);
        }
      }
      return newSchedule;
    });
  };

  const getAvailableBaristas = (dayIndex: number) => {
    const dayKey = dayIndex.toString();
    const scheduledBaristas = new Set<string>();
    
    if (manualSchedule[dayKey]) {
      manualSchedule[dayKey].openings.forEach(name => scheduledBaristas.add(name));
      manualSchedule[dayKey].closings.forEach(name => scheduledBaristas.add(name));
      manualSchedule[dayKey].off.forEach(name => scheduledBaristas.add(name));
    }

    return baristas.filter(barista => !scheduledBaristas.has(barista.name));
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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-all duration-200">
          <div className="flex items-center justify-between mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Users className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-center space-x-1 text-blue-600">
              <Coffee className="w-3 h-3" />
              <span className="text-xs font-medium">Active</span>
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Total Baristas</p>
            <p className="text-xl font-bold text-gray-900">{baristas.length}</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-all duration-200">
          <div className="flex items-center justify-between mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <Clock className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-center space-x-1 text-green-600">
              <CheckCircle className="w-3 h-3" />
              <span className="text-xs font-medium">Covered</span>
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Weekly Hours</p>
            <p className="text-xl font-bold text-gray-900">315</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-all duration-200">
          <div className="flex items-center justify-between mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <Target className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-center space-x-1 text-orange-600">
              <Brain className="w-3 h-3" />
              <span className="text-xs font-medium">AI</span>
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Schedules</p>
            <p className="text-xl font-bold text-gray-900">4</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-all duration-200">
          <div className="flex items-center justify-between mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-center space-x-1 text-purple-600">
              <Zap className="w-3 h-3" />
              <span className="text-xs font-medium">Optimized</span>
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Efficiency</p>
            <p className="text-xl font-bold text-gray-900">94%</p>
          </div>
        </div>
      </div>

      {/* Drag and Drop Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">!</span>
          </div>
          <div>
            <h4 className="font-medium text-blue-900 text-sm">Quick Guide:</h4>
            <p className="text-blue-800 text-xs">
              Drag baristas to shifts • Drag shift times to baristas • Drag Cam/Bar events to days • Same barista can work multiple days
            </p>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {activeView === 'calendar' && (
        <div className="card-elevated">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Drag & Drop Schedule</h3>
                <p className="text-sm text-gray-600">Drag barista names to arrange your weekly schedule</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setManualSchedule({});
                  setBaristaShifts({});
                  setDayEvents({});
                }}
                className="flex items-center space-x-2 px-4 py-3 bg-gray-500 text-white rounded-xl text-sm font-medium shadow-soft hover:bg-gray-600 focus:ring-2 focus:ring-gray-500 transition-all duration-200 touch-manipulation min-h-[44px]"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Clear All</span>
              </button>
              <button onClick={exportStyledExcel} className="flex items-center space-x-2 px-4 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl text-sm font-medium shadow-soft hover:bg-gray-50 focus:ring-2 focus:ring-purple-500 transition-all duration-200 touch-manipulation min-h-[44px]">
                <Download className="w-4 h-4" />
                <span>Export Excel</span>
              </button>
            </div>
          </div>

          {/* Drag and Drop Schedule */}
          <div className="space-y-6">
            {/* Available Baristas */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Available Baristas</h4>
              <div className="flex flex-wrap gap-2">
                {baristas.map((barista) => (
                  <div
                    key={barista.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, barista.name)}
                    onDragOver={(e) => handleBaristaDragOver(e, barista.name)}
                    onDragLeave={handleBaristaDragLeave}
                    onDrop={(e) => handleBaristaDrop(e, barista.name, 'default')}
                    className={`px-3 py-2 border rounded-lg text-sm font-medium cursor-move transition-colors relative ${
                      dragOverBarista === barista.name && draggedShift
                        ? 'bg-orange-100 border-orange-400 text-orange-800'
                        : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300'
                    }`}
                  >
                    {barista.name}
                    {baristaShifts[barista.name] && (
                      <div className="absolute -top-1 -right-1 flex flex-col gap-1">
                        {Object.entries(baristaShifts[barista.name]).map(([shiftType, time]) => (
                          <div 
                            key={shiftType}
                            className="bg-blue-500 text-white text-xs px-1 py-0.5 rounded-full cursor-pointer hover:bg-blue-600"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeShiftFromBarista(barista.name, shiftType);
                            }}
                            title={`Click to remove ${shiftType} shift time`}
                          >
                            {time}
                          </div>
                        ))}
                      </div>
                    )}
                    {dragOverBarista === barista.name && draggedShift && (
                      <div className="absolute -bottom-1 -right-1 bg-orange-500 text-white text-xs px-1 py-0.5 rounded-full">
                        {draggedShift}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Available Shift Times */}
            <div className="bg-orange-50 rounded-xl p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Available Shift Times</h4>
              <div className="flex flex-wrap gap-2">
                {shiftTimes.map((shiftTime) => (
                  <div
                    key={shiftTime}
                    draggable
                    onDragStart={(e) => handleShiftDragStart(e, shiftTime)}
                    className="px-3 py-2 bg-orange-100 border border-orange-200 rounded-lg text-sm font-medium text-orange-800 cursor-move hover:bg-orange-200 hover:border-orange-300 transition-colors"
                  >
                    <Clock className="w-3 h-3 inline mr-1" />
                    {shiftTime}
                  </div>
                ))}
              </div>
            </div>

            {/* Available Events */}
            <div className="bg-purple-50 rounded-xl p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Available Events</h4>
              <div className="flex flex-wrap gap-2">
                <div
                  draggable
                  onDragStart={(e) => handleEventDragStart(e, 'Cam')}
                  onDragEnd={handleEventDragEnd}
                  className="px-3 py-2 bg-purple-100 border border-purple-200 rounded-lg text-sm font-medium text-purple-800 cursor-move hover:bg-purple-200 hover:border-purple-300 transition-colors"
                >
                  Cam
                </div>
                <div
                  draggable
                  onDragStart={(e) => handleEventDragStart(e, 'Bar')}
                  onDragEnd={handleEventDragEnd}
                  className="px-3 py-2 bg-purple-100 border border-purple-200 rounded-lg text-sm font-medium text-purple-800 cursor-move hover:bg-purple-200 hover:border-purple-300 transition-colors"
                >
                  Bar
                </div>
              </div>
            </div>

            {/* Weekly Schedule Grid */}
            <div className="grid grid-cols-7 gap-4">
              {weekDates.map((date, dayIndex) => {
                const dayName = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'][dayIndex];
                const dayKey = dayIndex.toString();
                const daySchedule = manualSchedule[dayKey] || { openings: [], closings: [], off: [] };
                
                console.log(`Day ${dayIndex}: ${dayName}, key: ${dayKey}`); // Debug log
                
                return (
                  <div key={dayIndex} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                    {/* Day Header */}
                    <div 
                      className={`text-center mb-4 pb-3 border-b border-gray-100 transition-colors ${
                        dragOverDay === dayKey && draggedEvent
                          ? 'bg-purple-50 border-purple-200'
                          : ''
                      }`}
                      onDragOver={(e) => handleDayDragOver(e, dayKey)}
                      onDragLeave={handleDayDragLeave}
                      onDrop={(e) => handleDayDrop(e, dayKey)}
                    >
                      <div className="text-lg font-bold text-gray-900">{dayName}</div>
                      <div className="text-sm text-gray-500">{date.getDate()}/{date.getMonth() + 1}</div>
                      {dayEvents[dayKey] && dayEvents[dayKey].length > 0 && (
                        <div className="flex flex-wrap justify-center gap-1 mt-2">
                          {dayEvents[dayKey].map((event, idx) => (
                            <div 
                              key={idx}
                              className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full flex items-center gap-1"
                            >
                              {event}
                              <button
                                onClick={() => removeEventFromDay(dayKey, event)}
                                className="text-purple-600 hover:text-purple-800"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      {dragOverDay === dayKey && draggedEvent && (
                        <div className="text-xs text-purple-600 font-medium mt-1">
                          → {draggedEvent}
                        </div>
                      )}
                    </div>
                    
                    {/* Opening Shifts Drop Zone */}
                    <div className="mb-4">
                      <div className="text-xs font-semibold text-blue-600 mb-2 uppercase tracking-wide">
                        Açılış
                      </div>
                      <div
                        className="min-h-[80px] bg-blue-50 rounded-lg p-2 border-2 border-dashed border-blue-200"
                        onDragOver={handleDragOver}
                        onDrop={(e) => handleDrop(e, dayIndex, 'openings')}
                      >
                        <div className="space-y-1">
                          {daySchedule.openings.map((baristaName, idx) => (
                            <div 
                              key={idx} 
                              draggable
                              onDragStart={(e) => handleDragStart(e, baristaName)}
                              onDragOver={(e) => handleBaristaDragOver(e, baristaName)}
                              onDragLeave={handleBaristaDragLeave}
                              onDrop={(e) => handleBaristaDrop(e, baristaName, 'opening')}
                              className={`bg-blue-100 rounded p-2 text-sm flex items-center justify-between cursor-move transition-colors ${
                                dragOverBarista === baristaName && draggedShift
                                  ? 'bg-orange-100 border-2 border-orange-400'
                                  : 'hover:bg-blue-200'
                              }`}
                            >
                              <div className="flex flex-col">
                                <span className="font-medium text-blue-900">{baristaName}</span>
                                {baristaShifts[baristaName]?.opening && (
                                  <span className="text-xs text-blue-700">{baristaShifts[baristaName].opening}</span>
                                )}
                                {dragOverBarista === baristaName && draggedShift && (
                                  <span className="text-xs text-orange-600 font-medium">→ {draggedShift}</span>
                                )}
                              </div>
                              <button
                                onClick={() => removeFromSchedule(baristaName, dayIndex, 'openings')}
                                className="text-blue-600 hover:text-blue-800"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                          {daySchedule.openings.length === 0 && (
                            <div className="text-xs text-blue-500 italic">
                              Drop baristas here for opening shift
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Closing Shifts Drop Zone */}
                    <div className="mb-4">
                      <div className="text-xs font-semibold text-green-600 mb-2 uppercase tracking-wide">
                        Kapanış
                      </div>
                      <div
                        className="min-h-[120px] bg-green-50 rounded-lg p-2 border-2 border-dashed border-green-200"
                        onDragOver={handleDragOver}
                        onDrop={(e) => handleDrop(e, dayIndex, 'closings')}
                      >
                        <div className="space-y-1">
                          {daySchedule.closings.map((baristaName, idx) => (
                            <div 
                              key={idx} 
                              draggable
                              onDragStart={(e) => handleDragStart(e, baristaName)}
                              onDragOver={(e) => handleBaristaDragOver(e, baristaName)}
                              onDragLeave={handleBaristaDragLeave}
                              onDrop={(e) => handleBaristaDrop(e, baristaName, 'closing')}
                              className={`bg-green-100 rounded p-2 text-sm flex items-center justify-between cursor-move transition-colors ${
                                dragOverBarista === baristaName && draggedShift
                                  ? 'bg-orange-100 border-2 border-orange-400'
                                  : 'hover:bg-green-200'
                              }`}
                            >
                              <div className="flex flex-col">
                                <span className="font-medium text-green-900">{baristaName}</span>
                                {baristaShifts[baristaName]?.closing && (
                                  <span className="text-xs text-green-700">{baristaShifts[baristaName].closing}</span>
                                )}
                                {dragOverBarista === baristaName && draggedShift && (
                                  <span className="text-xs text-orange-600 font-medium">→ {draggedShift}</span>
                                )}
                              </div>
                              <button
                                onClick={() => removeFromSchedule(baristaName, dayIndex, 'closings')}
                                className="text-green-600 hover:text-green-800"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                          {daySchedule.closings.length === 0 && (
                            <div className="text-xs text-green-500 italic">
                              Drop baristas here for closing shift
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Off Baristas Drop Zone */}
                    <div>
                      <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                        İzinli
                      </div>
                      <div
                        className="min-h-[60px] bg-gray-50 rounded-lg p-2 border-2 border-dashed border-gray-200"
                        onDragOver={handleDragOver}
                        onDrop={(e) => handleDrop(e, dayIndex, 'off')}
                      >
                        <div className="space-y-1">
                          {daySchedule.off.map((baristaName, idx) => (
                            <div 
                              key={idx} 
                              draggable
                              onDragStart={(e) => handleDragStart(e, baristaName)}
                              onDragOver={(e) => handleBaristaDragOver(e, baristaName)}
                              onDragLeave={handleBaristaDragLeave}
                              onDrop={(e) => handleBaristaDrop(e, baristaName, 'off')}
                              className={`bg-gray-100 rounded p-2 text-sm flex items-center justify-between cursor-move transition-colors ${
                                dragOverBarista === baristaName && draggedShift
                                  ? 'bg-orange-100 border-2 border-orange-400'
                                  : 'hover:bg-gray-200'
                              }`}
                            >
                              <div className="flex flex-col">
                                <span className="font-medium text-gray-700">{baristaName}</span>
                                {baristaShifts[baristaName]?.off && (
                                  <span className="text-xs text-gray-600">{baristaShifts[baristaName].off}</span>
                                )}
                                {dragOverBarista === baristaName && draggedShift && (
                                  <span className="text-xs text-orange-600 font-medium">→ {draggedShift}</span>
                                )}
                              </div>
                              <button
                                onClick={() => removeFromSchedule(baristaName, dayIndex, 'off')}
                                className="text-gray-600 hover:text-gray-800"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                          {daySchedule.off.length === 0 && (
                            <div className="text-xs text-gray-400 italic">Drop here for day off</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
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
