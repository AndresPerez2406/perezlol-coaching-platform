"""Script de diagnóstico para conexión a Supabase."""
import os
import sys
from dotenv import load_dotenv

# Forzar salida en utf-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

def test_supabase():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    print("\n--- Verificación de Configuración Supabase ---")
    print(f"URL: {url if url and 'tu-proyecto' not in url else '[NO CONFIGURADO]'}")
    
    if key.startswith("eyJ"):
        print("API KEY: [Detectada clave JWT válida (empieza por eyJ...)]")
    elif key:
        print(f"API KEY: [Detectado valor: '{key[:4]}...{key[-3:] if len(key)>6 else ''}']")
        print("\n[!] ATENCIÓN: La clave que pusiste parece ser la CONTRASEÑA de la base de datos, NO la API Key.")
        print("En Supabase necesitas la 'anon public' key:")
        print("  1. Entra a tu proyecto en https://app.supabase.com")
        print("  2. Ve a Project Settings (icono de engranaje) -> API")
        print("  3. En 'Project API keys', copia la que dice 'anon' / 'public' (empieza por eyJ...)")
        print("  4. Pégala en SUPABASE_KEY en tu archivo .env")
        return
    else:
        print("API KEY: [NO CONFIGURADA]")
        return

    try:
        from supabase import create_client
        supabase = create_client(url, key)
        # Probar autenticación / query básica
        res = supabase.table("profiles").select("*").limit(1).execute()
        print("\n[OK] ¡Conexión exitosa con Supabase!")
        print("La base de datos y la clave 'anon' están funcionando correctamente.")
    except Exception as e:
        error_msg = str(e)
        if "relation \"public.profiles\" does not exist" in error_msg:
            print("\n[OK] ¡Conexión con Supabase establecida!")
            print("[INFO] Aún no has ejecutado el script 'database/schema.sql' en el SQL Editor de Supabase.")
        elif "Invalid API key" in error_msg:
            print("\n[ERROR] Clave de API inválida.")
            print("Verifica que hayas copiado la anon/public key completa desde Project Settings -> API.")
        else:
            print(f"\n[INFO] Respuesta de Supabase: {error_msg}")

if __name__ == "__main__":
    test_supabase()
