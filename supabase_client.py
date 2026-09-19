"""
RESQ-AI Supabase database connection.

The .env file is loaded using an explicit path so the backend
works reliably when started by Uvicorn/reload processes.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client


# ---------------------------------------------------------
# Load backend/.env explicitly
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


# ---------------------------------------------------------
# Read environment variables
# ---------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")


# ---------------------------------------------------------
# Validate configuration
# ---------------------------------------------------------

if not SUPABASE_URL:
    raise RuntimeError(
        f"SUPABASE_URL is missing. Expected .env at: {ENV_FILE}"
    )

if not SUPABASE_SECRET_KEY:
    raise RuntimeError(
        f"SUPABASE_SECRET_KEY is missing. Expected .env at: {ENV_FILE}"
    )


# ---------------------------------------------------------
# Create Supabase client
# ---------------------------------------------------------

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)