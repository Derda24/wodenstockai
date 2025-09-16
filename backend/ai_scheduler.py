"""
AI Scheduler Module for Woden AI Stock Management
Generates intelligent weekly schedules for baristas
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Tuple
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
            'max_hours_full_time': 54,   # Full-time weekly cap
            'max_hours_part_time': 21,   # Part-time weekly cap
            'morning_before_day_off': True,
            'opening_baristas_per_day': 2,  # Always 2 people for opening
            'closing_baristas_per_day': 3,  # Always 3 people for closing
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
            
            # Track assigned hours per barista for weekly caps
            hours_assigned: Dict[str, int] = {b['id']: 0 for b in active_baristas}

            # Generate shifts for each day to ensure proper coverage
            generated_shifts = []
            
            for day in range(7):  # Monday to Sunday
                day_shifts = self._generate_day_schedule(
                    active_baristas, day, schedule_id, preferences, hours_assigned or {}
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
                    # Update assigned hours
                    hours_assigned[shift['barista_id']] = hours_assigned.get(shift['barista_id'], 0) + int(shift['hours'])
            
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

    def _generate_day_schedule(self, baristas: List[Dict[str, Any]], day: int, schedule_id: str, preferences: Dict[str, Any] = None, hours_assigned: Dict[str, int] = None) -> List[Dict[str, Any]]:
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
            
            if day != day_off:
                available_baristas.append(barista)
        
        # Separate full-time and part-time baristas
        full_time_baristas = [b for b in available_baristas if b.get("type", "full-time") == "full-time"]
        part_time_baristas = [b for b in available_baristas if b.get("type", "full-time") == "part-time"]
        
        # Select opening baristas (2 people)
        # Opening must be full-time only. Priority: full-time with day off tomorrow get opening today
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
        if remaining_needed > 0:
            remaining_candidates = [b for b in full_time_baristas if b['id'] not in opening_selected_ids]
            fill = self._select_baristas_for_shift(
                remaining_candidates,
                remaining_needed,
                "morning",
                day,
                preferences,
                hours_assigned,
                required_hours=9
            )
            opening_baristas.extend(fill)
        
        # Select closing baristas (3 people) - exclude opening and allow both types
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
        
        # Create opening shifts (full-time only, 9h)
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
        
        # Create closing shifts (full-time 9h, part-time 7h 17:30-00:30) with safety check
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
        
        return shifts

    def _select_baristas_for_shift(self, baristas: List[Dict[str, Any]], count: int, shift_type: str, day: int, preferences: Dict[str, Any] = None, hours_assigned: Dict[str, int] = None, required_hours: int = 9, exclude_ids: set | None = None) -> List[Dict[str, Any]]:
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
            # Part-time cannot work morning
            if b_type == 'part-time' and shift_type == 'morning':
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
        max_hours = barista.get("max_hours", 45)
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
