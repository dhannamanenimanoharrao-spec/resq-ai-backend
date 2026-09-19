"""
RESQ-AI FastAPI Backend
Adaptive Emergency Resource Orchestration Engine

Current responsibilities:
- Health check
- Read ambulances from Supabase
- Read hospitals from Supabase
- Read emergencies from Supabase
- Create emergencies in Supabase
- CORS support for the RESQ-AI frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import Emergency
from supabase_client import supabase


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="RESQ-AI",
    description="Adaptive Emergency Resource Orchestration Engine",
    version="0.3.0",
)


# =========================================================
# CORS CONFIGURATION
# =========================================================
# The frontend may run on either port 5173 or 5174.
# This allows the browser to communicate with FastAPI.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():
    """Basic project information."""

    return {
        "project": "RESQ-AI",
        "status": "online",
        "version": "0.3.0",
        "message": "Backend connected to Supabase.",
    }


# =========================================================
# HEALTH ENDPOINT
# =========================================================

@app.get("/health")
def health():
    """
    Check whether FastAPI can communicate
    successfully with Supabase.
    """

    try:
        supabase.table("ambulances").select("id").limit(1).execute()

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as exc:
        return {
            "status": "degraded",
            "database": "error",
            "detail": str(exc),
        }


# =========================================================
# AMBULANCE ENDPOINTS
# =========================================================

@app.get("/ambulances")
def get_ambulances():
    """Return all ambulances from Supabase."""

    try:
        response = (
            supabase
            .table("ambulances")
            .select("*")
            .order("id")
            .execute()
        )

        return response.data

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch ambulances: {str(exc)}",
        )


@app.get("/ambulances/{ambulance_id}")
def get_ambulance(ambulance_id: str):
    """Return one ambulance by ID."""

    try:
        response = (
            supabase
            .table("ambulances")
            .select("*")
            .eq("id", ambulance_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Ambulance not found.",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch ambulance: {str(exc)}",
        )


# =========================================================
# HOSPITAL ENDPOINTS
# =========================================================

@app.get("/hospitals")
def get_hospitals():
    """Return all hospitals from Supabase."""

    try:
        response = (
            supabase
            .table("hospitals")
            .select("*")
            .order("id")
            .execute()
        )

        return response.data

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch hospitals: {str(exc)}",
        )


@app.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    """Return one hospital by ID."""

    try:
        response = (
            supabase
            .table("hospitals")
            .select("*")
            .eq("id", hospital_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Hospital not found.",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch hospital: {str(exc)}",
        )


# =========================================================
# EMERGENCY ENDPOINTS
# =========================================================

@app.get("/emergencies")
def get_emergencies():
    """Return emergencies, newest first."""

    try:
        response = (
            supabase
            .table("emergencies")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch emergencies: {str(exc)}",
        )


@app.post("/emergencies")
def create_emergency(emergency: Emergency):
    """
    Create a new emergency.

    Flow:

    Frontend
        ↓
    FastAPI
        ↓
    Pydantic validation
        ↓
    Supabase
        ↓
    PostgreSQL
    """

    try:
        payload = emergency.model_dump(mode="json")

        response = (
            supabase
            .table("emergencies")
            .insert(payload)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Emergency could not be created.",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create emergency: {str(exc)}",
        )