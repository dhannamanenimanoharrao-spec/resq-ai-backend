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
    version="0.5.0",
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
        "version": "0.5.0",
        "message": "Backend connected to Supabase with real Telangana GIS data.",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    try:
        supabase.table("ambulances_real").select("id").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return {"status": "degraded", "database": "error", "detail": str(exc)}


# =========================================================
# AMBULANCES — real Telangana GIS data
# =========================================================

@app.get("/ambulances")
def get_ambulances():
    try:
        response = (
            supabase.table("ambulances_real")
            .select("*")
            .order("id")
            .limit(100)
            .execute()
        )
        return response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ambulances: {str(exc)}")


@app.get("/ambulances/{ambulance_id}")
def get_ambulance(ambulance_id: str):
    try:
        response = (
            supabase.table("ambulances_real")
            .select("*")
            .eq("id", ambulance_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Ambulance not found.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ambulance: {str(exc)}")


# =========================================================
# HOSPITALS — real Telangana GIS health facilities
# =========================================================

@app.get("/hospitals")
def get_hospitals():
    try:
        response = (
            supabase.table("health_facilities_real")
            .select("*")
            .order("id")
            .limit(100)
            .execute()
        )
        return response.data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hospitals: {str(exc)}")


@app.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    try:
        response = (
            supabase.table("health_facilities_real")
            .select("*")
            .eq("id", hospital_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Facility not found.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch facility: {str(exc)}")


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
# DISPATCH
# =========================================================

class DispatchRequest(BaseModel):
    emergency_id: str
    ambulance_id: str
    hospital_id: str


@app.post("/dispatch")
def dispatch(req: DispatchRequest):
    try:
        emg = supabase.table("emergencies").select("*").eq("id", req.emergency_id).limit(1).execute()
        if not emg.data:
            raise HTTPException(status_code=404, detail="Emergency not found.")

        amb = supabase.table("ambulances_real").select("*").eq("id", req.ambulance_id).limit(1).execute()
        if not amb.data:
            raise HTTPException(status_code=404, detail="Ambulance not found.")
        if amb.data[0].get("current_status") == "busy":
            raise HTTPException(status_code=400, detail="Ambulance is not available.")

        supabase.table("ambulances_real").update({
            "current_status": "busy",
            "current_emergency_id": req.emergency_id
        }).eq("id", req.ambulance_id).execute()

        supabase.table("emergencies").update({
            "status": "dispatched",
            "assigned_ambulance_id": req.ambulance_id,
            "assigned_hospital_id": req.hospital_id,
        }).eq("id", req.emergency_id).execute()

        return {
            "success": True,
            "message": f"Dispatched {req.ambulance_id} to emergency {req.emergency_id}. Facility {req.hospital_id} assigned.",
            "emergency_id": req.emergency_id,
            "ambulance_id": req.ambulance_id,
            "hospital_id": req.hospital_id,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Dispatch failed: {str(exc)}")