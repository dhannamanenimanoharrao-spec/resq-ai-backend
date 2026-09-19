"""
RESQ-AI FastAPI Backend
Adaptive Emergency Resource Orchestration Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from models import Emergency
from supabase_client import supabase


app = FastAPI(
    title="RESQ-AI",
    description="Adaptive Emergency Resource Orchestration Engine",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "project": "RESQ-AI",
        "status": "online",
        "version": "0.4.0",
        "message": "Backend connected to Supabase.",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    try:
        supabase.table("ambulances").select("id").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return {"status": "degraded", "database": "error", "detail": str(exc)}


# =========================================================
# AMBULANCES
# =========================================================

@app.get("/ambulances")
def get_ambulances():
    try:
        response = supabase.table("ambulances").select("*").order("id").execute()
        return response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ambulances: {str(exc)}")


@app.get("/ambulances/{ambulance_id}")
def get_ambulance(ambulance_id: str):
    try:
        response = supabase.table("ambulances").select("*").eq("id", ambulance_id).limit(1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Ambulance not found.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ambulance: {str(exc)}")


# =========================================================
# HOSPITALS
# =========================================================

@app.get("/hospitals")
def get_hospitals():
    try:
        response = supabase.table("hospitals").select("*").order("id").execute()
        return response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hospitals: {str(exc)}")


@app.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    try:
        response = supabase.table("hospitals").select("*").eq("id", hospital_id).limit(1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Hospital not found.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hospital: {str(exc)}")


# =========================================================
# EMERGENCIES
# =========================================================

@app.get("/emergencies")
def get_emergencies():
    try:
        response = supabase.table("emergencies").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emergencies: {str(exc)}")


@app.post("/emergencies")
def create_emergency(emergency: Emergency):
    try:
        payload = emergency.model_dump(mode="json")
        response = supabase.table("emergencies").insert(payload).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Emergency could not be created.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create emergency: {str(exc)}")


# =========================================================
# DISPATCH ENDPOINT
# =========================================================

class DispatchRequest(BaseModel):
    emergency_id: str
    ambulance_id: str
    hospital_id: str


@app.post("/dispatch")
def dispatch(req: DispatchRequest):
    """
    Assign an ambulance and hospital to an emergency.
    - Sets ambulance status to 'busy'
    - Sets emergency status to 'dispatched'
    - Reduces hospital available_beds by 1
    """
    try:
        # 1. Check emergency exists
        emg = supabase.table("emergencies").select("*").eq("id", req.emergency_id).limit(1).execute()
        if not emg.data:
            raise HTTPException(status_code=404, detail="Emergency not found.")

        # 2. Check ambulance exists and is available
        amb = supabase.table("ambulances").select("*").eq("id", req.ambulance_id).limit(1).execute()
        if not amb.data:
            raise HTTPException(status_code=404, detail="Ambulance not found.")
        if amb.data[0]["status"] != "available":
            raise HTTPException(status_code=400, detail="Ambulance is not available.")

        # 3. Check hospital exists and has beds
        hos = supabase.table("hospitals").select("*").eq("id", req.hospital_id).limit(1).execute()
        if not hos.data:
            raise HTTPException(status_code=404, detail="Hospital not found.")
        if hos.data[0]["available_beds"] < 1:
            raise HTTPException(status_code=400, detail="Hospital has no available beds.")

        # 4. Update ambulance → busy
        supabase.table("ambulances").update({
            "status": "busy",
            "current_emergency_id": req.emergency_id
        }).eq("id", req.ambulance_id).execute()

        # 5. Update emergency → dispatched
        supabase.table("emergencies").update({
            "status": "dispatched",
            "assigned_ambulance_id": req.ambulance_id,
            "assigned_hospital_id": req.hospital_id,
        }).eq("id", req.emergency_id).execute()

        # 6. Reduce hospital beds by 1
        new_beds = hos.data[0]["available_beds"] - 1
        supabase.table("hospitals").update({
            "available_beds": new_beds
        }).eq("id", req.hospital_id).execute()

        return {
            "success": True,
            "message": f"Dispatched {req.ambulance_id} to emergency {req.emergency_id}. Hospital {req.hospital_id} bed reserved.",
            "emergency_id": req.emergency_id,
            "ambulance_id": req.ambulance_id,
            "hospital_id": req.hospital_id,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Dispatch failed: {str(exc)}")