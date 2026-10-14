import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_supabase_client() -> Client | None:
    """
    Inicializa y devuelve el cliente singleton de Supabase.
    Prioriza SUPABASE_SERVICE_ROLE_KEY si está disponible para bypass de RLS en servidor,
    de lo contrario utiliza SUPABASE_KEY (anon).
    """
    env_url = os.getenv("SUPABASE_URL", "")
    env_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    env_anon_key = os.getenv("SUPABASE_KEY", "")

    # Determinar mejor clave en .env
    env_key = ""
    if env_service_key and "tu-service-role" not in env_service_key:
        env_key = env_service_key
    elif env_anon_key and "tu-anon" not in env_anon_key:
        env_key = env_anon_key

    sec_url = ""
    sec_key = ""
    try:
        if hasattr(st, "secrets"):
            sec_url = st.secrets.get("SUPABASE_URL", "")
            sec_service = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")
            sec_anon = st.secrets.get("SUPABASE_KEY", "")
            if sec_service and "tu-service-role" not in sec_service:
                sec_key = sec_service
            elif sec_anon and "tu-anon" not in sec_anon:
                sec_key = sec_anon
    except Exception:
        pass

    url = env_url if (env_url and "tu-proyecto" not in env_url) else sec_url
    key = env_key if env_key else sec_key

    if not url or not key or "tu-proyecto" in url or "tu-anon" in key or "tu-service-role" in key:
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Error al conectar con Supabase: {e}")
        return None

