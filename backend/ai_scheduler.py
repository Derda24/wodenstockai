"""
AI Scheduler Module for Woden AI Stock Management
Generates intelligent weekly schedules for baristas
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Tuple, Optional, Set
import random
import math
import traceback

class AIScheduler:
    def __init__(self, supabase_service):
        self.supabase_service = supabase_service
        
        # Operating hours configuration
        self.operating_hours = {
            'monday_saturday': {'start': '07:30', 'end': '00:30'},
            'sunday': {'start': '09:00', 'end': '00:30'}
        }
        
        # Shift configurations
        self.shift_types = {
            'morning': {'start': '07:30', 'end': '16:30', 'hours': 9},
            'evening_full': {'start': '15:30', 'end': '00:30', 'hours': 9},
            'evening_part': {'start': '17:30', 'end': '00:30', 'hours': 7},
        }
        
        # AI Rules
        self.rules = {
            'max_hours_full_time': 54,   # Full-time weekly cap per request
            'max_hours_part_time': 30,   # Part-time weekly cap (no strict restriction given)
            'morning_before_day_off': True,
            'opening_baristas_per_day': 2,  # strictly 2 people for opening
            'closing_baristas_per_day': 4,  # 4 people for closing per request
            'max_consecutive_days': 6
        }

    def generate_weekly_schedule(self, week_start: date, baristas: List[Dict[str, Any]], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate AI-powered weekly schedule for baristas
        
        Args:
            week_start: Start date of the week (Monday)
            baristas: List of barista data from database
            preferences: Optional barista preferences for the week
            
        Returns:
            Dict with success status and generated schedule data
        """
        try:
            print(f"AI Scheduler: Generating schedule for week starting {week_start}")
            print(f"AI Scheduler: Processing {len(baristas)} baristas")
            
            # Filter active baristas
            active_baristas = [b for b in baristas if b.get('is_active', True)]
            
            if len(active_baristas) < 2:
                return {
                    "success": False,
                    "message": "Need at least 2 active baristas to generate schedule"
                }
            
            # Create weekly schedule record
            week_end = week_start + timedelta(days=6)
            schedule_result = self.supabase_service.create_weekly_schedule(
                week_start=week_start.isoformat(),
                week_end=week_end.isoformat(),
                created_by="AI Scheduler",
                notes="AI-generated weekly schedule"
            )
            
            if not schedule_result["success"]:
                return schedule_result
            
            schedule_id = schedule_result["schedule"]["id"]
            print(f"AI Scheduler: Created schedule with ID {schedule_id}")
            
            # Track assigned hours and working days per barista for weekly caps and day-off rule
            hours_assigned: Dict[str, int] = {b['id']: 0 for b in active_baristas}
            days_assigned: Dict[str, int] = {b['id']: 0 for b in active_baristas}

            # Generate shifts for each day to ensure proper coverage
            generated_shifts = []
            
            for day in range(7):  # Monday to Sunday
                day_shifts = self._generate_day_schedule(
                    active_baristas, day, schedule_id, preferences, hours_assigned or {}, days_assigned or {}
                )
                generated_shifts.extend(day_shifts)
            
            # Save all shifts to database
            for shift in generated_shifts:
                shift_result = self.supabase_service.create_shift(
                    schedule_id=schedule_id,
                    barista_id=shift["barista_id"],
                    day_of_week=shift["day_of_week"],
                    shift_type=shift["shift_type"],
                    start_time=shift["start_time"],
                    end_time=shift["end_time"],
                    hours=shift["hours"],
                    notes=shift.get("notes", "")
                )
                
                if not shift_result["success"]:
                    print(f"Warning: Failed to create shift for barista {shift['barista_id']}")
                else:
                    # Update assigned hours and days
                    hours_assigned[shift['barista_id']] = hours_assigned.get(shift['barista_id'], 0) + int(shift['hours'])
                    if int(shift['hours']) > 0:
                        days_assigned[shift['barista_id']] = days_assigned.get(shift['barista_id'], 0) + 1
            
            # Get the complete schedule with barista details
            shifts_result = self.supabase_service.get_schedule_shifts(schedule_id)
            
            return {
                "success": True,
                "message": f"AI schedule generated successfully for {len(active_baristas)} baristas",
                "schedule_id": schedule_id,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "baristas_count": len(active_baristas),
                "shifts_count": len(generated_shifts),
                "shifts": shifts_result.get("shifts", [])
            }
            
        except Exception as e:
            print(f"AI Scheduler Error: {repr(e)}")
            print(traceback.format_exc())
            return {
                "success": False,
                "message": f"Error generating schedule: {repr(e)}"
            }

    def _generate_day_schedule(self, baristas: List[Dict[str, Any]], day: int, schedule_id: str, preferences: Dict[str, Any] = None, hours_assigned: Dict[str, int] = None, days_assigned: Dict[str, int] = None) -> List[Dict[str, Any]]:
        """
        Generate schedule for a specific day ensuring proper coverage
        
        Args:
            baristas: List of active baristas
            day: Day of week (0-6)
            schedule_id: ID of the weekly schedule
            preferences: Optional barista preferences
            
        Returns:
            List of shift dictionaries for the day
        """
        shifts = []
        
        # Filter baristas who are available (not on day off) and map day_off per barista
        available_baristas = []
        barista_day_off: Dict[str, int] = {}
        for barista in baristas:
            barista_id = barista["id"]
            day_off = None
            
            # Use preferences if available
            if preferences and barista_id in preferences:
                day_off = preferences[barista_id].get("dayOff")
                # -1 means no day off specified, use random assignment
                if day_off == -1:
                    day_off = hash(barista_id) % 7
            else:
                # Fallback: assign day off randomly for consistency
                day_off = hash(barista_id) % 7
            barista_day_off[barista_id] = day_off
            
            # Enforce one day off for full-time: if already 6 working days assigned, force day off
            if barista.get('type','full-time') == 'full-time' and (days_assigned or {}).get(barista_id, 0) >= 6:
                # Consider as day off today
                barista_day_off[barista_id] = day
                continue

            if day != day_off:
                available_baristas.append(barista)
        
        # Separate full-time and part-time baristas (available today)
        full_time_baristas = [b for b in available_baristas if b.get("type", "full-time") == "full-time"]
        part_time_baristas = [b for b in available_baristas if b.get("type", "full-time") == "part-time"]
        # Also keep global (ignoring day-off) for guaranteed fill
        all_full_time = [b for b in baristas if b.get("type", "full-time") == "full-time"]
        all_part_time = [b for b in baristas if b.get("type", "full-time") == "part-time"]
        
        # Helper: strict constraint checks
        def is_allowed_open(b: Dict[str, Any]) -> bool:
            # Özge can do morning; Boran/Can should not do morning
            name = (b.get('name') or '').lower()
            if name in {'boran', 'can'} and True:
                return False
            # Only allow part-time if they prefer morning
            if b.get('type') == 'part-time':
                prefs = [s.lower() for s in (b.get('preferred_shifts') or [])]
                return 'morning' in prefs
            return True

        def is_allowed_close(b: Dict[str, Any]) -> bool:
            name = (b.get('name') or '').lower()
            if name.startswith('özge'):
                return False
            return True

        # Select opening baristas (strictly 2 people)
        # Priority order:
        # 1) Full-time whose day off is tomorrow (must_open)
        # 2) Baristas with explicit opening preference for this day (from preferences), including part-time (e.g., Özge)
        # 3) Remaining full-time
        # 4) Morning-capable part-time
        opening_needed = self.rules["opening_baristas_per_day"]
        must_open: List[Dict[str, Any]] = []
        if self.rules.get("morning_before_day_off", True):
            for b in full_time_baristas:
                b_id = b["id"]
                b_type = b.get("type", "full-time")
                assigned = (hours_assigned or {}).get(b_id, 0)
                cap = self.rules['max_hours_full_time']
                if ((day + 1) % 7) == barista_day_off.get(b_id, -2) and assigned + 9 <= cap:
                    must_open.append(b)
        # Ensure uniqueness and cap the list
        must_open = list({b['id']: b for b in must_open}.values())[:opening_needed]
        opening_selected_ids = set(b['id'] for b in must_open)
        remaining_needed = max(0, opening_needed - len(must_open))
        opening_baristas = must_open.copy()

        # 1.5) Hard overrides provided as names for that day (preferences.fixed_opening_by_day)
        if remaining_needed > 0 and preferences and isinstance(preferences, dict):
            fixed_map = preferences.get("fixed_opening_by_day") or {}
            wanted_names = [n.lower().strip() for n in (fixed_map.get(day) or [])]
            if wanted_names:
                fixed_candidates = []
                for b in available_baristas + [x for x in baristas if x not in available_baristas]:
                    if b['id'] in opening_selected_ids:
                        continue
                    name = (b.get('name') or '').lower().strip()
                    if name in wanted_names and is_allowed_open(b):
                        # Check weekly cap feasibility
                        assigned = (hours_assigned or {}).get(b['id'], 0)
                        cap = self.rules['max_hours_part_time'] if b.get('type') == 'part-time' else self.rules['max_hours_full_time']
                        if assigned + 9 <= cap:
                            fixed_candidates.append(b)
                # Preserve wanted order
                ordered_fixed = []
                used = set()
                for wn in wanted_names:
                    for c in fixed_candidates:
                        if c['id'] in used:
                            continue
                        if (c.get('name') or '').lower().strip() == wn:
                            ordered_fixed.append(c)
                            used.add(c['id'])
                            break
                take = ordered_fixed[:remaining_needed]
                if take:
                    opening_baristas.extend(take)
                    opening_selected_ids.update(b['id'] for b in take)
                    remaining_needed = max(0, opening_needed - len(opening_baristas))

        # 2) Strong preferences for opening on this day
        if remaining_needed > 0:
            preferred_openers: List[Dict[str, Any]] = []
            for b in available_baristas:
                b_id = b['id']
                if b_id in opening_selected_ids:
                    continue
                # Only allow morning if policy allows it
                if b.get('type') == 'part-time':
                    prefs_shifts = [s.lower() for s in (b.get('preferred_shifts') or [])]
                    if 'morning' not in prefs_shifts:
                        continue
                # Check explicit daily preferences
                if preferences and b_id in preferences:
                    if day in (preferences[b_id].get('preferredOpening') or []):
                        preferred_openers.append(b)
                else:
                    # If no explicit preferences, prefer Özge for morning
                    name = (b.get('name') or '').lower()
                    if name.startswith('özge'):
                        preferred_openers.append(b)
            # De-dup and cap
            dedup_pref = []
            seen = set()
            for b in preferred_openers:
                if b['id'] in seen:
                    continue
                seen.add(b['id'])
                dedup_pref.append(b)
            # Sort to prefer full-time first among preferred, but keep Özge at top if present
            def pref_key(b):
                name = (b.get('name') or '').lower()
                is_ozge = 0 if name.startswith('özge') else 1
                is_ft = 0 if b.get('type') == 'full-time' else 1
                return (is_ozge, is_ft, (hours_assigned or {}).get(b['id'], 0))
            dedup_pref.sort(key=pref_key)
            take = dedup_pref[:remaining_needed]
            opening_baristas.extend(take)
            opening_selected_ids.update(b['id'] for b in take)
            remaining_needed = max(0, opening_needed - len(opening_baristas))
        if remaining_needed > 0:
            # First, try remaining full-time
            remaining_candidates_full = [b for b in full_time_baristas if b['id'] not in opening_selected_ids]
            fill_full = self._select_baristas_for_shift(
                remaining_candidates_full,
                remaining_needed,
                "morning",
                day,
                preferences,
                hours_assigned,
                required_hours=9
            )
            opening_baristas.extend(fill_full)
            remaining_needed = max(0, opening_needed - len(opening_baristas))
        if remaining_needed > 0:
            # Then allow part-time who are permitted mornings (strict prefs) and prioritize Özge
            def pt_morning_ok(b: Dict[str, Any]) -> bool:
                if b.get('type') != 'part-time':
                    return False
                name = (b.get('name') or '').lower()
                if name in {'boran', 'can'}:
                    return False
                prefs = [s.lower() for s in (b.get('preferred_shifts') or [])]
                return 'morning' in prefs
            remaining_candidates_pt = [b for b in part_time_baristas if pt_morning_ok(b) and b['id'] not in opening_selected_ids]
            # Prefer Özge first if present
            remaining_candidates_pt.sort(key=lambda b: 0 if (b.get('name') or '').lower().startswith('özge') else 1)
            fill_pt = self._select_baristas_for_shift(
                remaining_candidates_pt,
                remaining_needed,
                "morning",
                day,
                preferences,
                hours_assigned,
                required_hours=9
            )
            opening_baristas.extend(fill_pt)

        # Final fallback: allow pulling from day-off (global lists) to reach exactly opening_needed
        if len(opening_baristas) < opening_needed:
            need = opening_needed - len(opening_baristas)
            # Consider all baristas, not just available, with priority full-time then part-time
            all_full = [b for b in all_full_time if b not in opening_baristas]
            all_part = [b for b in all_part_time if b not in opening_baristas]
            # Filter by open-allowed
            all_full = [b for b in all_full if is_allowed_open(b)]
            all_part = [b for b in all_part if is_allowed_open(b)]
            # Sort by hours asc
            all_full.sort(key=lambda b: (hours_assigned or {}).get(b['id'], 0))
            all_part.sort(key=lambda b: (hours_assigned or {}).get(b['id'], 0))
            # Prefer Özgë if exists among part-time
            all_part.sort(key=lambda b: 0 if (b.get('name') or '').lower().startswith('özge') else 1)
            for pool in (all_full, all_part):
                for b in pool:
                    if len(opening_baristas) >= opening_needed:
                        break
                    opening_baristas.append(b)

        # Fallback top-up to guarantee exactly opening_needed (ignore weekly caps as last resort)
        # Do NOT force-fill beyond eligibility; if fewer than opening_needed remain after FT+PT, leave empty
        
        # Select closing baristas (4 people) - exclude opening and allow both types
        candidates_for_closing = [b for b in (full_time_baristas + part_time_baristas) if b not in opening_baristas]
        closing_baristas = self._select_baristas_for_shift(
            candidates_for_closing,
            self.rules["closing_baristas_per_day"], 
            "evening",
            day,
            preferences,
            hours_assigned,
            # hours depend on type; handled inside creator, but for selection use min 7
            required_hours=7,
            exclude_ids=set(b['id'] for b in opening_baristas)
        )

        # Re-select closers: prioritize full-time first, then part-time
        if len(closing_baristas) < self.rules["closing_baristas_per_day"]:
            # First pass already mixed; rebuild according to priority
            closing_needed = self.rules["closing_baristas_per_day"]
            closing_baristas = []
            # Full-time candidates first (prefer globally to guarantee fill)
            ft_candidates = [b for b in all_full_time if b not in opening_baristas]
            ft_candidates = [b for b in ft_candidates if is_allowed_close(b)]
            ft_fill = self._select_baristas_for_shift(
                ft_candidates,
                closing_needed,
                "evening",
                day,
                preferences,
                hours_assigned,
                required_hours=9,
                exclude_ids=set(b['id'] for b in opening_baristas)
            )
            closing_baristas.extend(ft_fill)
            rem = closing_needed - len(closing_baristas)
            if rem > 0:
                # Then part-time (prefer globally to guarantee fill)
                pt_candidates = [b for b in all_part_time if b not in opening_baristas]
                pt_candidates = [b for b in pt_candidates if is_allowed_close(b)]
                pt_fill = self._select_baristas_for_shift(
                    pt_candidates,
                    rem,
                    "evening",
                    day,
                    preferences,
                    hours_assigned,
                    required_hours=7,
                    exclude_ids=set(b['id'] for b in opening_baristas)
                )
                closing_baristas.extend(pt_fill)

        # Final fallback for closers: include day-off baristas if still short, respecting strict constraints
        if len(closing_baristas) < self.rules["closing_baristas_per_day"]:
            need = self.rules["closing_baristas_per_day"] - len(closing_baristas)
            all_full = [b for b in all_full_time if b not in opening_baristas and b not in closing_baristas]
            all_part = [b for b in all_part_time if b not in opening_baristas and b not in closing_baristas]
            all_full = [b for b in all_full if is_allowed_close(b)]
            all_part = [b for b in all_part if is_allowed_close(b)]
            all_full.sort(key=lambda b: (hours_assigned or {}).get(b['id'], 0))
            all_part.sort(key=lambda b: (hours_assigned or {}).get(b['id'], 0))
            for pool in (all_full, all_part):
                for b in pool:
                    if len(closing_baristas) >= self.rules["closing_baristas_per_day"]:
                        break
                    closing_baristas.append(b)
        
        # Create opening shifts (9h). Track day assignment once per barista per day
        counted_today: Set[str] = set()
        for barista in opening_baristas:
            shifts.append({
                "barista_id": barista["id"],
                "day_of_week": day,
                "shift_type": "morning",
                "start_time": "07:30:00",
                "end_time": "16:30:00",
                "hours": 9,
                "notes": "Opening shift"
            })
            # update assignment tracker early for fair distribution
            if hours_assigned is not None:
                hours_assigned[barista['id']] = hours_assigned.get(barista['id'], 0) + 9
            if days_assigned is not None and barista['id'] not in counted_today:
                days_assigned[barista['id']] = days_assigned.get(barista['id'], 0) + 1
                counted_today.add(barista['id'])
        
        # Create closing shifts (full-time 9h 15:30-00:30, part-time 7h 17:30-00:30) with safety check
        for barista in closing_baristas:
            if any(ob['id'] == barista['id'] for ob in opening_baristas):
                continue
            is_part_time = barista.get("type", "full-time") == "part-time"
            start_time = self.shift_types['evening_part']['start'] if is_part_time else self.shift_types['evening_full']['start']
            end_time = self.shift_types['evening_part']['end'] if is_part_time else self.shift_types['evening_full']['end']
            hours = self.shift_types['evening_part']['hours'] if is_part_time else self.shift_types['evening_full']['hours']
            shifts.append({
                "barista_id": barista["id"],
                "day_of_week": day,
                "shift_type": "evening",
                "start_time": f"{start_time}:00" if len(start_time) == 5 else start_time,
                "end_time": f"{end_time}:00" if len(end_time) == 5 else end_time,
                "hours": hours,
                "notes": "Closing shift"
            })
            if hours_assigned is not None:
                hours_assigned[barista['id']] = hours_assigned.get(barista['id'], 0) + int(hours)
            if days_assigned is not None and barista['id'] not in counted_today:
                days_assigned[barista['id']] = days_assigned.get(barista['id'], 0) + 1
                counted_today.add(barista['id'])
        
        return shifts

    def _select_baristas_for_shift(self, baristas: List[Dict[str, Any]], count: int, shift_type: str, day: int, preferences: Dict[str, Any] = None, hours_assigned: Dict[str, int] = None, required_hours: int = 9, exclude_ids: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """
        Select baristas for a specific shift type
        
        Args:
            baristas: Available baristas
            count: Number of baristas needed
            shift_type: Type of shift (morning/evening)
            day: Day of week (0-6)
            preferences: Optional barista preferences
            
        Returns:
            List of selected baristas
        """
        # Enforce weekly hour caps and eligibility
        eligible: List[Dict[str, Any]] = []
        for b in baristas:
            b_type = b.get("type", "full-time")
            assigned = (hours_assigned or {}).get(b["id"], 0)
            cap = self.rules['max_hours_part_time'] if b_type == 'part-time' else self.rules['max_hours_full_time']
            # Compute required hours by type if evening
            eff_required = required_hours
            if shift_type == 'evening':
                eff_required = 7 if b_type == 'part-time' else 9
            # Hard constraints from business rules
            # - Özge morning-only (block evening)
            if (b.get('name') or b.get('email') or '').lower().startswith('özge') and shift_type == 'evening':
                continue
            # - Boran and Can evenings only (block morning)
            if (b.get('name') or '').lower() in {'boran', 'can'} and shift_type == 'morning':
                continue
            # Part-time morning policy: generally avoid but allow if they prefer morning
            if b_type == 'part-time' and shift_type == 'morning':
                preferred = set([s.lower() for s in (b.get('preferred_shifts') or [])])
                if 'morning' not in preferred:
                    continue
            # Hard preference enforcement: if barista has preferences, only schedule within them
            prefs = [s.lower() for s in (b.get('preferred_shifts') or [])]
            if prefs and shift_type not in prefs:
                # allow full-time with both, block those without this shift in prefs
                pass_allowed = False
                if 'morning' in prefs and 'evening' in prefs:
                    pass_allowed = True
                if not pass_allowed:
                    # Do not allow e.g., Özge to be assigned evening
                    continue
            # Exclusion by ID
            if exclude_ids and b['id'] in exclude_ids:
                continue
            if assigned + eff_required <= cap:
                eligible.append(b)
        if len(eligible) < count:
            # Return whatever is eligible (may be less than needed)
            return eligible
        
        # Filter by preferences if available
        preferred_baristas = []
        for barista in eligible:
            barista_id = barista["id"]
            is_preferred = False
            
            # Check user preferences first
            if preferences and barista_id in preferences:
                pref = preferences[barista_id]
                if shift_type == "morning" and day in pref.get("preferredOpening", []):
                    is_preferred = True
                elif shift_type == "evening" and day in pref.get("preferredClosing", []):
                    is_preferred = True
            else:
                # Fallback to barista's general preferences
                preferred_shifts = barista.get("preferred_shifts", [])
                if shift_type in preferred_shifts or not preferred_shifts:
                    is_preferred = True
            
            if is_preferred:
                preferred_baristas.append(barista)
        
        # If we have enough preferred baristas, use them
        if len(preferred_baristas) >= count:
            return random.sample(preferred_baristas, count)
        
        # Otherwise, mix preferred and others
        selected = preferred_baristas.copy()
        remaining_needed = count - len(selected)
        remaining_baristas = [b for b in eligible if b not in selected]
        
        if remaining_needed > 0 and remaining_baristas:
            additional = random.sample(remaining_baristas, min(remaining_needed, len(remaining_baristas)))
            selected.extend(additional)
        
        return selected

    def _generate_barista_schedule(self, barista: Dict[str, Any], week_start: date, schedule_id: str) -> List[Dict[str, Any]]:
        """
        Generate schedule for a single barista
        
        Args:
            barista: Barista data
            week_start: Start date of the week
            schedule_id: ID of the weekly schedule
            
        Returns:
            List of shift dictionaries
        """
        shifts = []
        barista_id = barista["id"]
        barista_type = barista.get("type", "full-time")
        max_hours = barista.get("max_hours", 54)
        preferred_shifts = barista.get("preferred_shifts", [])
        
        # Determine day off (random for now, but could be based on preferences)
        day_off = random.randint(0, 6)  # 0=Monday, 6=Sunday
        
        # Calculate target hours based on barista type
        if barista_type == "part-time":
            target_hours = min(max_hours, 30)  # Cap part-time at 30 hours
            working_days = 4  # Part-time works 4 days
        else:
            target_hours = min(max_hours, 45)  # Full-time up to 45 hours
            working_days = 6  # Full-time works 6 days
        
        # Generate shifts for each day
        for day in range(7):  # Monday to Sunday
            if day == day_off:
                # Day off
                shifts.append({
                    "barista_id": barista_id,
                    "day_of_week": day,
                    "shift_type": "off",
                    "start_time": None,
                    "end_time": None,
                    "hours": 0,
                    "notes": "Day off"
                })
            else:
                # Determine shift type based on AI rules and preferences
                shift_type = self._determine_shift_type(barista, day, day_off, preferred_shifts)
                shift_config = self.shift_types[shift_type]
                
                # Apply morning shift rule: work morning the day before day off
                if day == (day_off - 1) % 7 and self.rules["morning_before_day_off"]:
                    shift_type = "morning"
                    shift_config = self.shift_types["morning"]
                
                shifts.append({
                    "barista_id": barista_id,
                    "day_of_week": day,
                    "shift_type": shift_type,
                    "start_time": shift_config["start"],
                    "end_time": shift_config["end"],
                    "hours": shift_config["hours"],
                    "notes": f"{shift_type.title()} shift"
                })
        
        return shifts

    def _determine_shift_type(self, barista: Dict[str, Any], day: int, day_off: int, preferred_shifts: List[str]) -> str:
        """
        Determine the best shift type for a barista on a given day
        
        Args:
            barista: Barista data
            day: Day of week (0-6)
            day_off: Barista's day off
            preferred_shifts: Barista's preferred shift types
            
        Returns:
            Shift type string
        """
        barista_type = barista.get("type", "full-time")
        
        # Part-time baristas get part-time shifts
        if barista_type == "part-time":
            return "part-time"
        
        # Check if barista has preferences
        if preferred_shifts:
            # Use preferred shifts with some randomness
            if "morning" in preferred_shifts and "evening" in preferred_shifts:
                return random.choice(["morning", "evening"])
            elif "morning" in preferred_shifts:
                return "morning"
            elif "evening" in preferred_shifts:
                return "evening"
        
        # Default logic: alternate between morning and evening
        # with some consideration for day of week
        if day in [0, 1, 2]:  # Monday, Tuesday, Wednesday
            return "morning" if random.random() > 0.3 else "evening"
        elif day in [3, 4]:  # Thursday, Friday
            return "evening" if random.random() > 0.3 else "morning"
        else:  # Saturday, Sunday
            return "morning" if random.random() > 0.5 else "evening"

    def optimize_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Optimize an existing schedule using AI algorithms
        
        Args:
            schedule_id: ID of the schedule to optimize
            
        Returns:
            Dict with optimization results
        """
        try:
            # Get current schedule
            shifts_result = self.supabase_service.get_schedule_shifts(schedule_id)
            
            if not shifts_result["success"]:
                return shifts_result
            
            shifts = shifts_result["shifts"]
            
            # Apply optimization algorithms
            optimized_shifts = self._apply_optimization_rules(shifts)
            
            # Update shifts in database
            for shift in optimized_shifts:
                # Update shift in database
                pass  # Implementation would update each shift
            
            return {
                "success": True,
                "message": "Schedule optimized successfully",
                "optimizations_applied": len(optimized_shifts)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error optimizing schedule: {str(e)}"
            }

    def _apply_optimization_rules(self, shifts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply AI optimization rules to improve schedule quality
        
        Args:
            shifts: List of current shifts
            
        Returns:
            List of optimized shifts
        """
        # This is where advanced AI optimization would happen
        # For now, we'll implement basic rules
        
        optimized = []
        
        for shift in shifts:
            # Basic optimization: ensure proper coverage
            if shift["shift_type"] != "off":
                # Add optimization logic here
                optimized.append(shift)
            else:
                optimized.append(shift)
        
        return optimized

    def analyze_schedule_quality(self, schedule_id: str) -> Dict[str, Any]:
        """
        Analyze the quality of a generated schedule
        
        Args:
            schedule_id: ID of the schedule to analyze
            
        Returns:
            Dict with quality metrics and recommendations
        """
        try:
            shifts_result = self.supabase_service.get_schedule_shifts(schedule_id)
            
            if not shifts_result["success"]:
                return shifts_result
            
            shifts = shifts_result["shifts"]
            
            # Calculate quality metrics
            metrics = {
                "total_shifts": len([s for s in shifts if s["shift_type"] != "off"]),
                "coverage_score": self._calculate_coverage_score(shifts),
                "fairness_score": self._calculate_fairness_score(shifts),
                "preference_score": self._calculate_preference_score(shifts),
                "overall_score": 0
            }
            
            # Calculate overall score
            metrics["overall_score"] = (
                metrics["coverage_score"] * 0.4 +
                metrics["fairness_score"] * 0.3 +
                metrics["preference_score"] * 0.3
            )
            
            return {
                "success": True,
                "metrics": metrics,
                "recommendations": self._generate_quality_recommendations(metrics)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing schedule quality: {str(e)}"
            }

    def _calculate_coverage_score(self, shifts: List[Dict[str, Any]]) -> float:
        """Calculate how well the schedule covers all required hours"""
        # Implementation would analyze coverage gaps
        return 0.85  # Placeholder

    def _calculate_fairness_score(self, shifts: List[Dict[str, Any]]) -> float:
        """Calculate how fairly hours are distributed among baristas"""
        # Implementation would analyze hour distribution
        return 0.90  # Placeholder

    def _calculate_preference_score(self, shifts: List[Dict[str, Any]]) -> float:
        """Calculate how well the schedule matches barista preferences"""
        # Implementation would analyze preference matching
        return 0.80  # Placeholder

    def _generate_quality_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on quality metrics"""
        recommendations = []
        
        if metrics["coverage_score"] < 0.8:
            recommendations.append("Consider adding more coverage during peak hours")
        
        if metrics["fairness_score"] < 0.8:
            recommendations.append("Balance hours more evenly among baristas")
        
        if metrics["preference_score"] < 0.8:
            recommendations.append("Better match barista shift preferences")
        
        return recommendations
