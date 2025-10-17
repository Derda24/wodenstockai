from typing import List, Dict, Any
from app.services.supabase_service import SupabaseService


STAFF: List[Dict[str, Any]] = [
    {"name": "Derda", "type": "full-time", "max_hours": 54, "preferred_shifts": ["morning", "evening"], "skills": ["cashier", "barback", "support"]},
    {"name": "İlker", "type": "full-time", "max_hours": 54, "preferred_shifts": ["morning", "evening"], "skills": ["cashier", "barback", "support"]},
    {"name": "Ahmet C.", "type": "full-time", "max_hours": 54, "preferred_shifts": ["morning", "evening"], "skills": ["cashier", "barback", "support"]},
    {"name": "Boran", "type": "part-time", "max_hours": 40, "preferred_shifts": ["evening"], "skills": ["barback", "support"]},
    {"name": "Can", "type": "part-time", "max_hours": 25, "preferred_shifts": ["evening"], "skills": ["barback", "support"]},
    {"name": "Özge", "type": "part-time", "max_hours": 25, "preferred_shifts": ["morning", "cashier"], "skills": ["cashier"]},
    {"name": "Bedi", "type": "part-time", "max_hours": 40, "preferred_shifts": ["evening"], "skills": ["barback", "support"]},
    {"name": "Emin", "type": "part-time", "max_hours": 40, "preferred_shifts": ["evening"], "skills": ["barback", "support"]},
]


def seed():
    service = SupabaseService()
    # Ensure AI scheduler tables exist (user should have run ai_scheduler_schema.sql already)
    created = 0
    for s in STAFF:
        # Check if barista exists by name
        try:
            resp = service.client.table("baristas").select("id").eq("name", s["name"]).limit(1).execute()
            if resp.data:
                # Update existing with latest attributes
                service.client.table("baristas").update({
                    "type": s["type"],
                    "max_hours": s["max_hours"],
                    "preferred_shifts": s.get("preferred_shifts", []),
                    "skills": s.get("skills", []),
                    "is_active": True,
                }).eq("id", resp.data[0]["id"]).execute()
            else:
                out = service.create_barista(
                    name=s["name"],
                    type=s["type"],
                    max_hours=s["max_hours"],
                    preferred_shifts=s.get("preferred_shifts", []),
                    skills=s.get("skills", []),
                )
                if out.get("success"):
                    created += 1
        except Exception as e:
            print(f"Seed error for {s['name']}: {e}")

    print({"seeded": True, "created": created, "total": len(STAFF)})


if __name__ == "__main__":
    seed()


