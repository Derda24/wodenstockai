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
        """Haftalık vardiya planı oluştur - Sadece kullanıcı tercihlerini uygula"""
        print(f"Haftalık vardiya planı oluşturuluyor: {start_date}")
        
        # Sadece manuel atamaları uygula
        self._apply_manual_assignments(start_date)
        
        # Sadece kullanıcı tercihlerini uygula
        self._apply_user_preferences(start_date)
        
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
    
    def _apply_user_preferences(self, start_date: date):
        """Sadece kullanıcının belirttiği tercihleri uygula"""
        print("Kullanıcı tercihleri uygulanıyor...")
        
        for day_offset in range(7):
            current_day = start_date + timedelta(days=day_offset)
            day_name = current_day.strftime('%A')
            day_weekday = current_day.weekday()
            
            # Her çalışan için tercihlerini kontrol et
            for employee_name, employee in self.employees.items():
                preferences = employee.preferences
                
                # Tercih edilen açılış günleri
                if "preferred_opening_days" in preferences and day_weekday in preferences["preferred_opening_days"]:
                    if not self._is_assigned(current_day, employee_name):
                        self._assign_to_schedule(employee_name, current_day, ShiftType.OPENING)
                        employee.add_working_day(current_day, ShiftType.OPENING)
                        print(f"✅ Açılış tercihi uygulandı: {employee_name} - {day_name}")
                
                # Tercih edilen kapanış günleri
                if "preferred_closing_days" in preferences and day_weekday in preferences["preferred_closing_days"]:
                    if not self._is_assigned(current_day, employee_name):
                        self._assign_to_schedule(employee_name, current_day, ShiftType.CLOSING)
                        employee.add_working_day(current_day, ShiftType.CLOSING)
                        print(f"✅ Kapanış tercihi uygulandı: {employee_name} - {day_name}")
                
                # Tercih edilen izin günü
                if "preferred_day_off" in preferences and preferences["preferred_day_off"] == day_weekday:
                    employee.take_day_off(current_day)
                    print(f"✅ İzin tercihi uygulandı: {employee_name} - {day_name}")
    
    # Removed complex scheduling rules - now only applies user preferences
    
    # Removed complex full barista planning - now only applies user preferences
    
    # Removed complex day-off planning - now only applies user preferences
    
    # Removed complex opening assignment - now only applies user preferences
    
    
    # Removed complex closing scheduling - now only applies user preferences
    
    
    # Removed complex closing assignment - now only applies user preferences
    
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
    
    # Removed full barista off day check - no longer needed with simplified approach
    
    # Removed validation and minimum coverage enforcement - now only applies user preferences
    
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
