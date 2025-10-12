"""
AI Scheduler - Woden Coffee Vardiya Sistemi
Akıllı vardiya planlama sistemi
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
import json
import random
from enum import Enum

class ShiftType(Enum):
    OPENING = "açılış"  # 07:30-15:30 (Pazar 09:00-15:30)
    CLOSING = "kapanış"  # 17:30-00:30

class EmployeeType(Enum):
    FULL = "full"
    PART_TIME = "part_time"

class Employee:
    def __init__(self, name: str, employee_type: EmployeeType, 
                 max_working_days: int = 6, max_openings: int = 3):
        self.name = name
        self.employee_type = employee_type
        self.max_working_days = max_working_days
        self.max_openings = max_openings
        self.working_days = []
        self.off_days = []
        self.openings_count = 0
        self.preferences = {}  # Manuel tercihler
        
    def can_work_day(self, day: date) -> bool:
        """Bu gün çalışabilir mi?"""
        if day in self.off_days:
            return False
        if len(self.working_days) >= self.max_working_days:
            return False
        return True
    
    def can_do_opening(self) -> bool:
        """Açılış yapabilir mi?"""
        return self.openings_count < self.max_openings
    
    def add_working_day(self, day: date, shift_type: ShiftType):
        """Çalışma günü ekle"""
        if day not in self.working_days:
            self.working_days.append(day)
        if shift_type == ShiftType.OPENING:
            self.openings_count += 1
    
    def take_day_off(self, day: date):
        """İzin günü al"""
        if day not in self.off_days:
            self.off_days.append(day)

class AIScheduler:
    def __init__(self):
        self.employees = self._initialize_employees()
        self.weekly_schedule = {}
        self.manual_assignments = {}  # Manuel atamalar
        self.barista_preferences = {}  # Barista tercihleri (UI'dan gelecek)
        
    def _initialize_employees(self) -> Dict[str, Employee]:
        """Çalışanları başlat"""
        employees = {}
        
        # Full Baristalar (6 gün çalışır, 1 gün izin, max 3 açılış)
        full_baristas = ["Derda", "Ahmet", "İlker"]
        for name in full_baristas:
            employees[name] = Employee(name, EmployeeType.FULL, 6, 3)
        
        # Part-time Baristalar
        # Boran, Bedi, Emin (5 gün çalışır, 2 gün izin, max 1 açılış)
        part_time_limited = ["Boran", "Bedi", "Emin"]
        for name in part_time_limited:
            employees[name] = Employee(name, EmployeeType.PART_TIME, 5, 1)
        
        # Özge (sadece açılış, genelde Çarşamba, Perşembe, Cumartesi)
        employees["Özge"] = Employee("Özge", EmployeeType.PART_TIME, 3, 3)
        employees["Özge"].preferences = {
            "preferred_days": [2, 3, 5],  # Çarşamba, Perşembe, Cumartesi
            "shift_preference": ShiftType.OPENING
        }
        
        # Sultan (sadece kapanış, haftada 3 gün, 19:30 giriş)
        employees["Sultan"] = Employee("Sultan", EmployeeType.PART_TIME, 3, 0)
        employees["Sultan"].preferences = {
            "shift_preference": ShiftType.CLOSING,
            "entry_time": "19:30"
        }
        
        # Can (full baristaların tatil günlerinde çalışır, genelde 3 kapanış)
        employees["Can"] = Employee("Can", EmployeeType.PART_TIME, 3, 0)
        employees["Can"].preferences = {
            "shift_preference": ShiftType.CLOSING,
            "fills_full_off_days": True
        }
        
        return employees
    
    def add_manual_assignment(self, employee_name: str, day: date, shift_type: ShiftType):
        """Manuel atama ekle"""
        if employee_name not in self.manual_assignments:
            self.manual_assignments[employee_name] = {}
        
        self.manual_assignments[employee_name][day] = shift_type
        print(f"Manuel atama eklendi: {employee_name} - {day.strftime('%Y-%m-%d')} - {shift_type.value}")
    
    def set_barista_preferences(self, preferences: Dict[str, Dict[str, Any]]):
        """
        Barista tercihlerini ayarla
        
        preferences format:
        {
            "Ahmet": {
                "preferred_day_off": 4,  # 0=Pazartesi, 6=Pazar (None = tercih yok)
                "preferred_opening_days": [0, 1, 2],  # Pazartesi, Salı, Çarşamba
                "preferred_closing_days": [3, 4, 5]   # Perşembe, Cuma, Cumartesi
            },
            ...
        }
        """
        self.barista_preferences = preferences
        
        # Tercihleri employee nesnelerine aktar
        for barista_name, prefs in preferences.items():
            if barista_name in self.employees:
                employee = self.employees[barista_name]
                
                # Tercih edilen açılış günlerini kaydet
                if "preferred_opening_days" in prefs and prefs["preferred_opening_days"]:
                    employee.preferences["preferred_opening_days"] = prefs["preferred_opening_days"]
                
                # Tercih edilen kapanış günlerini kaydet
                if "preferred_closing_days" in prefs and prefs["preferred_closing_days"]:
                    employee.preferences["preferred_closing_days"] = prefs["preferred_closing_days"]
                
                # Tercih edilen izin gününü kaydet
                if "preferred_day_off" in prefs and prefs["preferred_day_off"] is not None:
                    employee.preferences["preferred_day_off"] = prefs["preferred_day_off"]
        
        print(f"✅ {len(preferences)} barista için tercihler yüklendi")
    
    def generate_weekly_schedule(self, start_date: date) -> Dict[str, Any]:
        """Haftalık vardiya planı oluştur"""
        print(f"Haftalık vardiya planı oluşturuluyor: {start_date}")
        
        # Manuel atamaları önce uygula
        self._apply_manual_assignments(start_date)
        
        # Açılış vardiyalarını planla (2 kişi gerekli)
        self._schedule_openings(start_date)
        
        # Kapanış vardiyalarını planla (4 kişi gerekli)
        self._schedule_closings(start_date)
        
        # Çalışma günlerini kontrol et ve düzenle
        self._validate_and_adjust_schedule(start_date)
        
        return self._format_schedule(start_date)
    
    def _apply_manual_assignments(self, start_date: date):
        """Manuel atamaları uygula"""
        for employee_name, assignments in self.manual_assignments.items():
            if employee_name in self.employees:
                employee = self.employees[employee_name]
                for day, shift_type in assignments.items():
                    # Hafta içinde mi kontrol et
                    week_end = start_date + timedelta(days=6)
                    if start_date <= day <= week_end:
                        employee.add_working_day(day, shift_type)
                        self._assign_to_schedule(employee_name, day, shift_type)
    
    def _schedule_openings(self, start_date: date):
        """Açılış vardiyalarını planla (2 kişi) - Dengeli full barista dağılımı"""
        print("Açılış vardiyaları planlanıyor...")
        
        # Önce full baristalar için haftalık açılış planlaması yap
        self._plan_full_barista_openings(start_date)
        
        for day_offset in range(7):
            current_day = start_date + timedelta(days=day_offset)
            day_name = current_day.strftime('%A')
            
            # Bu gün için açılış atanmış mı kontrol et
            opening_assigned = self._count_shift_type_for_day(current_day, ShiftType.OPENING)
            
            if opening_assigned < 2:  # 2 kişi gerekli
                needed = 2 - opening_assigned
                self._assign_remaining_openings(current_day, needed)
    
    def _plan_full_barista_openings(self, start_date: date):
        """Full baristalar için haftalık açılış planlaması"""
        full_baristas = ["Derda", "Ahmet", "İlker"]
        
        # Önce izin günlerini planla
        self._plan_full_barista_days_off(start_date)
        
        # Sonra açılışları planla
        week_days = [start_date + timedelta(days=i) for i in range(7)]
        
        # Her gün için sadece 1 full barista açılışta olacak şekilde planla
        # Toplam 6 açılış (her full barista 2 açılış)
        
        # Her gün için 1 full barista ata
        # Toplam 7 gün var, her full barista 2 açılış yapacak (toplam 6 açılış)
        # 1 gün part-time çalışanlar açılış yapacak
        
        assigned_openings = {name: 0 for name in full_baristas}
        target_openings_per_barista = {
            "Derda": 2,
            "Ahmet": 2,
            "İlker": 2
        }
        
        # Her gün için 1 full barista ata
        for day in week_days:
            # Bu gün için full barista ata
            assigned_this_day = False
            
            # Full baristaları açılış sayısına göre sırala (az açılış yapan önce)
            sorted_baristas = sorted(full_baristas, key=lambda x: assigned_openings[x])
            
            for barista_name in sorted_baristas:
                employee = self.employees[barista_name]
                
                # Bu barista izin gününde değilse ve henüz hedef açılış sayısına ulaşmadıysa ata
                if (day not in employee.off_days and 
                    assigned_openings[barista_name] < target_openings_per_barista[barista_name] and
                    not self._is_assigned(day, barista_name)):
                    
                    self._assign_to_schedule(barista_name, day, ShiftType.OPENING)
                    employee.add_working_day(day, ShiftType.OPENING)
                    assigned_openings[barista_name] += 1
                    assigned_this_day = True
                    print(f"✅ Full barista açılış planlandı: {barista_name} - {day.strftime('%Y-%m-%d')}")
                    break  # Bu gün için sadece 1 full barista
            
            # Eğer bu gün için full barista atanamadıysa, part-time çalışanlar açılış yapacak
            if not assigned_this_day:
                print(f"ℹ️ {day.strftime('%Y-%m-%d')}: Full barista yok, part-time çalışanlar açılış yapacak")
    
    def _plan_full_barista_days_off(self, start_date: date):
        """Full baristaların izin günlerini planla - tercihleri kullan"""
        full_baristas = ["Derda", "Ahmet", "İlker"]
        week_days = [start_date + timedelta(days=i) for i in range(7)]
        
        used_off_days = []  # Kullanılan izin günleri
        
        # Her full barista için 1 izin günü ata
        for barista_name in full_baristas:
            # İzin günü: açılış yapmadığı günlerden birini seç
            available_off_days = []
            
            for day in week_days:
                if not self._is_assigned(day, barista_name):
                    available_off_days.append(day)
            
            # İzin günü ata - önce tercihleri kontrol et
            if available_off_days:
                off_day = None
                employee = self.employees[barista_name]
                
                # Kullanıcı tercihi var mı?
                preferred_day_off = employee.preferences.get("preferred_day_off")
                
                if preferred_day_off is not None:
                    # Tercih edilen günü bul
                    for day in available_off_days:
                        if day.weekday() == preferred_day_off and day not in used_off_days:
                            off_day = day
                            print(f"✅ Tercih kullanıldı: {barista_name} - {off_day.strftime('%A')}")
                            break
                
                # Tercih yoksa veya kullanılamıyorsa, otomatik ata
                if not off_day:
                    # Varsayılan tercihler
                    default_preferences = {
                        "Derda": [6, 0],      # Pazar, Pazartesi
                        "Ahmet": [4, 5],      # Cuma, Cumartesi  
                        "İlker": [6, 1]       # Pazar, Salı
                    }
                    
                    for preferred_day in default_preferences.get(barista_name, [6]):
                        for day in available_off_days:
                            if day.weekday() == preferred_day and day not in used_off_days:
                                off_day = day
                                break
                        if off_day:
                            break
                
                # Eğer hala bulunamadıysa, başka bir gün seç
                if not off_day:
                    for day in available_off_days:
                        if day not in used_off_days:
                            off_day = day
                            break
                
                # Hala bulunamadıysa, ilk müsait günü al
                if not off_day:
                    off_day = available_off_days[0]
                
                used_off_days.append(off_day)
                self.employees[barista_name].take_day_off(off_day)
                
                # İzin günü için schedule'a özel işaretleme yap
                day_str = off_day.strftime('%Y-%m-%d')
                if day_str not in self.weekly_schedule:
                    self.weekly_schedule[day_str] = {
                        "day_name": off_day.strftime('%A'),
                        "openings": [],
                        "closings": []
                    }
                # İzin günü bilgisini kaydet
                if "off_days" not in self.weekly_schedule[day_str]:
                    self.weekly_schedule[day_str]["off_days"] = []
                self.weekly_schedule[day_str]["off_days"].append(barista_name)
                print(f"✅ Full barista izin planlandı: {barista_name} - {off_day.strftime('%Y-%m-%d')}")
    
    def _assign_remaining_openings(self, day: date, needed: int):
        """Kalan açılışları ata - Part-time çalışanları öncelikli"""
        available_employees = []
        
        # Açılış yapabilen çalışanları bul
        for name, employee in self.employees.items():
            if (employee.can_work_day(day) and 
                employee.can_do_opening() and 
                not self._is_assigned(day, name)):
                
                available_employees.append(employee)
        
        # Part-time ve full-time çalışanları ayır
        part_time_employees = [emp for emp in available_employees if emp.employee_type == EmployeeType.PART_TIME]
        full_time_employees = [emp for emp in available_employees if emp.employee_type == EmployeeType.FULL]
        
        # Tercihlere göre sırala
        high_priority = []  # Tercih eden çalışanlar
        medium_priority = []  # Tercih etmeyen ama uygun olanlar
        low_priority = []  # Tercih etmeyen
        
        for emp in part_time_employees:
            preferred_opening_days = emp.preferences.get("preferred_opening_days", [])
            
            # Özge için özel kontrol (eski sistem uyumluluğu)
            if emp.name == "Özge" and "preferred_days" in emp.preferences:
                preferred_opening_days = emp.preferences.get("preferred_days", [])
            
            if preferred_opening_days and day.weekday() in preferred_opening_days:
                high_priority.append(emp)
                print(f"✅ Açılış tercihi kullanıldı: {emp.name} - {day.strftime('%A')}")
            else:
                medium_priority.append(emp)
        
        # Full-time çalışanları da tercihlere göre sırala
        for emp in full_time_employees:
            if emp.openings_count < 2:  # Henüz 2 açılış yapmamışsa
                preferred_opening_days = emp.preferences.get("preferred_opening_days", [])
                
                if preferred_opening_days and day.weekday() in preferred_opening_days:
                    high_priority.append(emp)
                    print(f"✅ Açılış tercihi kullanıldı: {emp.name} - {day.strftime('%A')}")
                else:
                    low_priority.append(emp)
        
        # Öncelik sırası: Tercih edenler -> Tercih etmeyenler
        prioritized_employees = high_priority + medium_priority + low_priority
        
        # Gerekli sayıda atama yap
        assigned_count = 0
        for employee in prioritized_employees:
            if assigned_count >= needed:
                break
                
            self._assign_to_schedule(employee.name, day, ShiftType.OPENING)
            employee.add_working_day(day, ShiftType.OPENING)
            assigned_count += 1
        
        # Eğer hala yeterli değilse, zorla atama yap (SADECE PART-TIME)
        if assigned_count < needed:
            print(f"⚠️ {day}: Açılış için yeterli part-time çalışan yok, zorla atama yapılıyor")
            remaining_needed = needed - assigned_count
            
            # Önce part-time çalışanları dene (çifte vardiya yapabilirler)
            for name, employee in self.employees.items():
                if (remaining_needed > 0 and 
                    employee.employee_type == EmployeeType.PART_TIME and
                    employee.can_work_day(day)):
                    
                    self._assign_to_schedule(employee.name, day, ShiftType.OPENING)
                    employee.add_working_day(day, ShiftType.OPENING)
                    remaining_needed -= 1
            
            # Hala yeterli değilse, full baristaları da ekle (son çare)
            if remaining_needed > 0:
                print(f"⚠️ {day}: Part-time yetmedi, full baristaları da ekliyorum")
                for name, employee in self.employees.items():
                    if (remaining_needed > 0 and 
                        employee.employee_type == EmployeeType.FULL and
                        not self._is_assigned(day, name) and
                        employee.can_work_day(day)):
                        
                        self._assign_to_schedule(employee.name, day, ShiftType.OPENING)
                        employee.add_working_day(day, ShiftType.OPENING)
                        remaining_needed -= 1
    
    
    def _schedule_closings(self, start_date: date):
        """Kapanış vardiyalarını planla (4 kişi)"""
        print("Kapanış vardiyaları planlanıyor...")
        
        for day_offset in range(7):
            current_day = start_date + timedelta(days=day_offset)
            
            # Bu gün için kapanış atanmış mı kontrol et
            closing_assigned = self._count_shift_type_for_day(current_day, ShiftType.CLOSING)
            
            if closing_assigned < 4:  # 4 kişi gerekli
                needed = 4 - closing_assigned
                self._assign_closing_shift(current_day, needed)
    
    
    def _assign_closing_shift(self, day: date, needed: int):
        """Kapanış vardiyası ata"""
        available_employees = []
        
        # Kapanış yapabilen çalışanları bul
        for name, employee in self.employees.items():
            if (employee.can_work_day(day) and 
                not self._is_assigned(day, name)):
                
                # Sultan için özel kontrol (sadece kapanış)
                if name == "Sultan":
                    available_employees.insert(0, employee)  # Öncelik
                # Can için özel kontrol (full baristaların tatil günlerinde)
                elif name == "Can" and self._is_full_barista_off_day(day):
                    available_employees.insert(0, employee)  # Öncelik
                else:
                    available_employees.append(employee)
        
        # Eğer yeterli çalışan yoksa, zorla atama yap
        if len(available_employees) < needed:
            print(f"⚠️ {day}: Yeterli çalışan yok, zorla atama yapılıyor")
            # Zaten çalışan çalışanları da dahil et (çifte vardiya)
            for name, employee in self.employees.items():
                if (not self._is_assigned(day, name) or 
                    (self._is_assigned(day, name) and len(self._get_assigned_employees_for_day(day, ShiftType.CLOSING)) < 4)):
                    
                    if employee not in available_employees:
                        available_employees.append(employee)
        
        # Gerekli sayıda atama yap
        assigned_count = 0
        for employee in available_employees:
            if assigned_count >= needed:
                break
                
            self._assign_to_schedule(employee.name, day, ShiftType.CLOSING)
            employee.add_working_day(day, ShiftType.CLOSING)
            assigned_count += 1
    
    def _assign_to_schedule(self, employee_name: str, day: date, shift_type: ShiftType):
        """Vardiyayı programa ata"""
        day_str = day.strftime('%Y-%m-%d')
        
        if day_str not in self.weekly_schedule:
            self.weekly_schedule[day_str] = {
                "date": day_str,
                "day_name": day.strftime('%A'),
                "openings": [],
                "closings": []
            }
        
        shift_info = {
            "employee": employee_name,
            "employee_type": self.employees[employee_name].employee_type.value,
            "shift_start": self._get_shift_start_time(day, shift_type),
            "shift_end": self._get_shift_end_time(shift_type)
        }
        
        if shift_type == ShiftType.OPENING:
            self.weekly_schedule[day_str]["openings"].append(shift_info)
        else:
            self.weekly_schedule[day_str]["closings"].append(shift_info)
    
    def _get_shift_start_time(self, day: date, shift_type: ShiftType) -> str:
        """Vardiya başlangıç saati"""
        if shift_type == ShiftType.OPENING:
            if day.weekday() == 6:  # Pazar
                return "09:00"
            else:
                return "07:30"
        else:  # CLOSING
            return "17:30"
    
    def _get_shift_end_time(self, shift_type: ShiftType) -> str:
        """Vardiya bitiş saati"""
        if shift_type == ShiftType.OPENING:
            return "15:30"
        else:  # CLOSING
            return "00:30"
    
    def _is_assigned(self, day: date, employee_name: str) -> bool:
        """Çalışan bu gün atanmış mı?"""
        day_str = day.strftime('%Y-%m-%d')
        if day_str in self.weekly_schedule:
            schedule = self.weekly_schedule[day_str]
            all_shifts = schedule["openings"] + schedule["closings"]
            return any(shift["employee"] == employee_name for shift in all_shifts)
        return False
    
    def _count_shift_type_for_day(self, day: date, shift_type: ShiftType) -> int:
        """Gün için vardiya tipi sayısı"""
        day_str = day.strftime('%Y-%m-%d')
        if day_str in self.weekly_schedule:
            if shift_type == ShiftType.OPENING:
                return len(self.weekly_schedule[day_str]["openings"])
            else:
                return len(self.weekly_schedule[day_str]["closings"])
        return 0
    
    def _get_assigned_employees_for_day(self, day: date, shift_type: ShiftType) -> List[str]:
        """Gün için atanmış çalışanlar"""
        day_str = day.strftime('%Y-%m-%d')
        if day_str in self.weekly_schedule:
            if shift_type == ShiftType.OPENING:
                shifts = self.weekly_schedule[day_str]["openings"]
            else:
                shifts = self.weekly_schedule[day_str]["closings"]
            return [shift["employee"] for shift in shifts]
        return []
    
    def _is_full_barista_off_day(self, day: date) -> bool:
        """Bu gün full baristaların tatil günü mü?"""
        full_baristas = ["Derda", "Ahmet", "İlker"]
        for name in full_baristas:
            if name in self.employees and day in self.employees[name].working_days:
                return False  # En az biri çalışıyor
        return True  # Hepsi tatilde
    
    def _validate_and_adjust_schedule(self, start_date: date):
        """Programı kontrol et ve düzenle"""
        print("Program kontrol ediliyor...")
        
        for day_offset in range(7):
            current_day = start_date + timedelta(days=day_offset)
            self._ensure_minimum_coverage(current_day)
    
    def _ensure_minimum_coverage(self, day: date):
        """Minimum kapsama alanını garanti et"""
        day_str = day.strftime('%Y-%m-%d')
        
        if day_str in self.weekly_schedule:
            openings = len(self.weekly_schedule[day_str]["openings"])
            closings = len(self.weekly_schedule[day_str]["closings"])
            
            # Açılış için minimum 2 kişi
            if openings < 2:
                needed = 2 - openings
                print(f"⚠️ {day_str}: Açılış yetersiz ({openings}/2), {needed} kişi daha atanıyor")
                self._assign_opening_shift(day, needed)
            
            # Kapanış için minimum 4 kişi
            if closings < 4:
                needed = 4 - closings
                print(f"⚠️ {day_str}: Kapanış yetersiz ({closings}/4), {needed} kişi daha atanıyor")
                self._assign_closing_shift(day, needed)
    
    def _format_schedule(self, start_date: date) -> Dict[str, Any]:
        """Programı formatla"""
        week_end = start_date + timedelta(days=6)
        
        # Çalışan özeti
        employee_summary = {}
        for name, employee in self.employees.items():
            employee_summary[name] = {
                "type": employee.employee_type.value,
                "working_days": len(employee.working_days),
                "off_days": len(employee.off_days),
                "openings_count": employee.openings_count,
                "max_working_days": employee.max_working_days,
                "max_openings": employee.max_openings
            }
        
        return {
            "week_start": start_date.strftime('%Y-%m-%d'),
            "week_end": week_end.strftime('%Y-%m-%d'),
            "schedule": self.weekly_schedule,
            "employee_summary": employee_summary,
            "total_assignments": self._count_total_assignments(),
            "coverage_analysis": self._analyze_coverage()
        }
    
    def _count_total_assignments(self) -> Dict[str, int]:
        """Toplam atamaları say"""
        total_openings = 0
        total_closings = 0
        
        for day_schedule in self.weekly_schedule.values():
            total_openings += len(day_schedule["openings"])
            total_closings += len(day_schedule["closings"])
        
        return {
            "total_openings": total_openings,
            "total_closings": total_closings,
            "total_shifts": total_openings + total_closings
        }
    
    def _analyze_coverage(self) -> Dict[str, Any]:
        """Kapsama analizi"""
        coverage = {
            "daily_coverage": {},
            "employee_utilization": {},
            "issues": []
        }
        
        for day_str, day_schedule in self.weekly_schedule.items():
            openings = len(day_schedule["openings"])
            closings = len(day_schedule["closings"])
            
            coverage["daily_coverage"][day_str] = {
                "openings": openings,
                "closings": closings,
                "total": openings + closings,
                "opening_adequate": openings >= 2,
                "closing_adequate": closings >= 4
            }
            
            # Sorunları tespit et
            if openings < 2:
                coverage["issues"].append(f"{day_str}: Açılış yetersiz ({openings}/2)")
            if closings < 4:
                coverage["issues"].append(f"{day_str}: Kapanış yetersiz ({closings}/4)")
        
        return coverage
    
    def export_schedule_data(self, start_date: date) -> str:
        """Program verilerini export et - düzenli format"""
        
        # Haftalık program oluştur
        schedule_data = self.generate_weekly_schedule(start_date)
        
        export_data = {
            "export_info": {
                "generated_at": datetime.now().isoformat(),
                "scheduler_version": "2.0.0",
                "week_start": start_date.strftime('%Y-%m-%d'),
                "week_end": (start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
                "export_type": "weekly_schedule"
            },
            
            "schedule_summary": {
                "total_openings": schedule_data["total_assignments"]["total_openings"],
                "total_closings": schedule_data["total_assignments"]["total_closings"],
                "total_shifts": schedule_data["total_assignments"]["total_shifts"],
                "coverage_status": "✅ Tam Kapsama" if not schedule_data["coverage_analysis"]["issues"] else "⚠️ Eksik Kapsama"
            },
            
            "weekly_schedule": self._format_export_schedule(),
            
            "employee_summary": schedule_data["employee_summary"],
            
            "coverage_analysis": schedule_data["coverage_analysis"],
            
            "manual_assignments": self._format_manual_assignments(),
            
            "shift_rules": {
                "opening_shift": {
                    "required_staff": 2,
                    "hours": "07:30-15:30 (Pazar: 09:00-15:30)",
                    "rules": [
                        "Minimum 2 kişi gerekli",
                        "Full baristalar yan yana gelmemeli",
                        "Özge tercih ettiği günlerde öncelikli"
                    ]
                },
                "closing_shift": {
                    "required_staff": 4,
                    "hours": "17:30-00:30",
                    "rules": [
                        "Minimum 4 kişi gerekli",
                        "Sultan sadece kapanış yapar",
                        "Can full baristaların tatil günlerinde öncelikli"
                    ]
                }
            }
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _format_export_schedule(self) -> Dict[str, Any]:
        """Export için programı formatla"""
        formatted_schedule = {}
        
        for day_str, day_schedule in self.weekly_schedule.items():
            formatted_schedule[day_str] = {
                "date": day_str,
                "day_name": day_schedule["day_name"],
                "shifts": {
                    "opening": {
                        "count": len(day_schedule["openings"]),
                        "staff": [
                            {
                                "name": shift["employee"],
                                "type": shift["employee_type"],
                                "hours": f"{shift['shift_start']}-{shift['shift_end']}"
                            }
                            for shift in day_schedule["openings"]
                        ]
                    },
                    "closing": {
                        "count": len(day_schedule["closings"]),
                        "staff": [
                            {
                                "name": shift["employee"],
                                "type": shift["employee_type"],
                                "hours": f"{shift['shift_start']}-{shift['shift_end']}"
                            }
                            for shift in day_schedule["closings"]
                        ]
                    }
                },
                "coverage_status": {
                    "opening_adequate": len(day_schedule["openings"]) >= 2,
                    "closing_adequate": len(day_schedule["closings"]) >= 4,
                    "total_staff": len(day_schedule["openings"]) + len(day_schedule["closings"])
                }
            }
        
        return formatted_schedule
    
    def _format_manual_assignments(self) -> Dict[str, Any]:
        """Manuel atamaları formatla"""
        if not self.manual_assignments:
            return {"message": "Manuel atama yok", "assignments": {}}
        
        formatted = {}
        for employee_name, assignments in self.manual_assignments.items():
            formatted[employee_name] = {
                "total_manual_assignments": len(assignments),
                "assignments": {
                    day.strftime('%Y-%m-%d'): shift_type.value
                    for day, shift_type in assignments.items()
                }
            }
        
        return formatted
    
    def load_schedule_data(self, json_data: str):
        """Program verilerini yükle"""
        try:
            data = json.loads(json_data)
            
            # Manuel atamaları yükle
            if "manual_assignments" in data:
                self.manual_assignments = {}
                for employee_name, assignments in data["manual_assignments"].items():
                    self.manual_assignments[employee_name] = {}
                    for day_str, shift_type_str in assignments.items():
                        day = datetime.strptime(day_str, '%Y-%m-%d').date()
                        shift_type = ShiftType.OPENING if shift_type_str == "açılış" else ShiftType.CLOSING
                        self.manual_assignments[employee_name][day] = shift_type
            
            print("Program verileri başarıyla yüklendi")
            return True
            
        except Exception as e:
            print(f"Program verileri yüklenirken hata: {str(e)}")
            return False

# Test fonksiyonu
def test_scheduler():
    """Scheduler'ı test et"""
    scheduler = AIScheduler()
    
    # Başlangıç tarihi (Pazartesi)
    start_date = date(2025, 10, 13)
    
    # Örnek tercihler (UI'dan gelecek)
    preferences = {
        "Ahmet": {
            "preferred_day_off": 4,  # Cuma
            "preferred_opening_days": [0, 1],  # Pazartesi, Salı
            "preferred_closing_days": [5, 6]   # Cumartesi, Pazar
        },
        "Özge": {
            "preferred_opening_days": [2, 3, 5],  # Çarşamba, Perşembe, Cumartesi
            "preferred_closing_days": []
        },
        "Derda": {
            "preferred_day_off": 6,  # Pazar
            "preferred_opening_days": [0, 3],  # Pazartesi, Perşembe
            "preferred_closing_days": [1, 2, 4, 5]  # Salı, Çarşamba, Cuma, Cumartesi
        }
    }
    
    # Tercihleri yükle
    scheduler.set_barista_preferences(preferences)
    
    # Haftalık program oluştur
    schedule = scheduler.generate_weekly_schedule(start_date)
    
    print("\n=== HAFTALIK VARDİYA PROGRAMI ===")
    for day_str, day_schedule in schedule["schedule"].items():
        print(f"\n{day_schedule['day_name']} - {day_str}")
        print(f"Açılış ({len(day_schedule['openings'])} kişi):")
        for shift in day_schedule['openings']:
            print(f"  - {shift['employee']} ({shift['shift_start']}-{shift['shift_end']})")
        
        print(f"Kapanış ({len(day_schedule['closings'])} kişi):")
        for shift in day_schedule['closings']:
            print(f"  - {shift['employee']} ({shift['shift_start']}-{shift['shift_end']})")
    
    print(f"\n=== ÇALIŞAN ÖZETİ ===")
    for name, summary in schedule["employee_summary"].items():
        print(f"{name}: {summary['working_days']} gün çalışma, {summary['openings_count']} açılış")
    
    print(f"\n=== KAPSAMA ANALİZİ ===")
    for day_str, coverage in schedule["coverage_analysis"]["daily_coverage"].items():
        print(f"{day_str}: Açılış {coverage['openings']}/2, Kapanış {coverage['closings']}/4")
    
    if schedule["coverage_analysis"]["issues"]:
        print(f"\n⚠️ SORUNLAR:")
        for issue in schedule["coverage_analysis"]["issues"]:
            print(f"  - {issue}")
    
    # Export test
    print(f"\n=== EXPORT DATA TEST ===")
    export_data = scheduler.export_schedule_data(start_date)
    print(f"Export verisi oluşturuldu ({len(export_data)} karakter)")
    
    # Export verisini dosyaya kaydet
    with open("schedule_export.json", "w", encoding="utf-8") as f:
        f.write(export_data)
    print("Export verisi 'schedule_export.json' dosyasına kaydedildi")

if __name__ == "__main__":
    test_scheduler()
