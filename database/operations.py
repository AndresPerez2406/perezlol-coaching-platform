"""
Módulo de operaciones centralizadas para Supabase.
Permite interactuar con perfiles, paquetes, pagos P2P, sesiones y tareas.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

# ==============================================================================
# 1. PERFILES Y AUTENTICACIÓN
# ==============================================================================

def get_profile(supabase, user_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el perfil completo de un usuario por su UUID."""
    if not supabase or not user_id:
        return None
    try:
        res = supabase.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
        return res.data
    except Exception as e:
        print(f"Error al obtener perfil: {e}")
        return None

def get_profile_by_email(supabase, email: str) -> Optional[Dict[str, Any]]:
    """Obtiene el perfil de un usuario por su correo electrónico."""
    if not supabase or not email:
        return None
    try:
        res = supabase.table("profiles").select("*").eq("email", email.strip().lower()).maybe_single().execute()
        return res.data
    except Exception as e:
        print(f"Error al obtener perfil por email: {e}")
        return None

def upsert_profile(supabase, user_id: str, email: str, role: str = "student",
                   riot_id: str = "", discord_tag: str = "perez1473", full_name: str = "") -> bool:
    """Crea o actualiza el registro del perfil en public.profiles."""
    if not supabase or not user_id:
        return False
    try:
        data = {
            "id": user_id,
            "email": email,
            "role": role,
            "riot_id": riot_id,
            "discord_tag": discord_tag or "perez1473",
            "full_name": full_name or email.split("@")[0],
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("profiles").upsert(data).execute()
        return True
    except Exception as e:
        print(f"Error al guardar perfil: {e}")
        return False

def update_profile_details(supabase, user_id: str, full_name: str, riot_id: str,
                           discord_tag: str, avatar_url: str = "") -> bool:
    """Permite al usuario editar su propio perfil (nombre, riot ID, discord, avatar)."""
    if not supabase or not user_id:
        return False
    try:
        update_data = {
            "full_name": full_name,
            "riot_id": riot_id,
            "discord_tag": discord_tag,
            "updated_at": datetime.utcnow().isoformat()
        }
        if avatar_url:
            update_data["avatar_url"] = avatar_url
        supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar perfil: {e}")
        return False

def update_account_password(supabase, new_password: str) -> bool:
    """Actualiza la contraseña del usuario actual en Supabase Auth."""
    if not supabase or not new_password:
        return False
    try:
        supabase.auth.update_user({"password": new_password})
        return True
    except Exception as e:
        print(f"Error al actualizar contraseña: {e}")
        return False

def enroll_new_student(supabase, email: str, password: str, full_name: str, riot_id: str, discord_tag: str) -> Optional[str]:
    """Permite al coach o admin crear y matricular a un nuevo estudiante."""
    if not supabase or not email:
        return None
    clean_email = email.strip().lower()
    try:
        user_id = None
        # Intentar crear a través de Auth
        try:
            res = supabase.auth.sign_up({
                "email": clean_email,
                "password": password,
                "options": {
                    "data": {
                        "role": "student",
                        "full_name": full_name,
                        "riot_id": riot_id,
                        "discord_tag": discord_tag
                    }
                }
            })
            if res.user:
                user_id = res.user.id
        except Exception:
            pass

        if not user_id:
            import uuid
            user_id = str(uuid.uuid4())

        upsert_profile(
            supabase=supabase,
            user_id=user_id,
            email=clean_email,
            role="student",
            riot_id=riot_id,
            discord_tag=discord_tag or "perez1473",
            full_name=full_name
        )
        return user_id
    except Exception as e:
        print(f"Error al matricular estudiante: {e}")
        return None

# ==============================================================================
# 2. PAQUETES Y TARIFAS
# ==============================================================================

def get_packages(supabase) -> List[Dict[str, Any]]:
    """Obtiene la lista de paquetes activos ordenados por precio."""
    if not supabase:
        return []
    try:
        res = supabase.table("packages").select("*").eq("is_active", True).order("price").execute()
        return res.data or []
    except Exception as e:
        print(f"Error al consultar paquetes: {e}")
        return []

def get_student_package(supabase, student_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el paquete activo de un estudiante con créditos restantes."""
    if not supabase or not student_id:
        return None
    try:
        res = (supabase.table("student_packages")
               .select("*, packages(*)")
               .eq("student_id", student_id)
               .eq("status", "active")
               .order("created_at", desc=True)
               .limit(1)
               .execute())
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        print(f"Error al obtener paquete de estudiante: {e}")
        return None

# ==============================================================================
# 3. PAGOS Y FLUJO P2P
# ==============================================================================

def submit_payment(supabase, student_id: str, package_id: str, amount: float,
                   payment_method: str, receipt_url: str = "", reference_number: str = "") -> bool:
    """Registra una solicitud de pago P2P del estudiante con su imagen de comprobante."""
    if not supabase:
        return False
    try:
        data = {
            "student_id": student_id,
            "package_id": package_id,
            "amount": amount,
            "payment_method": payment_method,
            "reference_number": reference_number or f"{payment_method}",
            "receipt_url": receipt_url,
            "status": "pending"
        }
        supabase.table("payments").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error al registrar pago: {e}")
        return False

def get_pending_payments(supabase) -> List[Dict[str, Any]]:
    """Obtiene todos los pagos pendientes para revisión del coach/admin."""
    if not supabase:
        return []
    try:
        res = (supabase.table("payments")
               .select("*, profiles!student_id(email, full_name, riot_id, discord_tag), packages(*)")
               .eq("status", "pending")
               .order("created_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al consultar pagos pendientes: {e}")
        return []

def get_student_payments(supabase, student_id: str) -> List[Dict[str, Any]]:
    """Obtiene el historial de pagos de un estudiante."""
    if not supabase or not student_id:
        return []
    try:
        res = (supabase.table("payments")
               .select("*, packages(title, price)")
               .eq("student_id", student_id)
               .order("created_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al consultar pagos del estudiante: {e}")
        return []

def approve_payment(supabase, payment_id: str, coach_id: str) -> bool:
    """
    Aprueba un pago P2P y acredita las clases (VODs y LIVEs) correspondientes al alumno.
    """
    if not supabase:
        return False
    try:
        # 1. Obtener datos del pago
        pay_res = supabase.table("payments").select("*, packages(*)").eq("id", payment_id).single().execute()
        payment = pay_res.data
        if not payment:
            return False

        pkg = payment.get("packages")
        student_id = payment.get("student_id")
        vods = pkg.get("vod_classes", 0) if pkg else 0
        lives = pkg.get("live_classes", 0) if pkg else 0

        # 2. Actualizar estado del pago a 'approved'
        now = datetime.utcnow().isoformat()
        supabase.table("payments").update({
            "status": "approved",
            "reviewed_by": coach_id,
            "reviewed_at": now
        }).eq("id", payment_id).execute()

        # 3. Acreditar clases al student_package
        active_pkg = get_student_package(supabase, student_id)
        if active_pkg:
            # Acumular clases en el paquete activo
            new_vod_total = active_pkg.get("vod_classes_total", 0) + vods
            new_live_total = active_pkg.get("live_classes_total", 0) + lives
            supabase.table("student_packages").update({
                "vod_classes_total": new_vod_total,
                "live_classes_total": new_live_total,
                "status": "active"
            }).eq("id", active_pkg["id"]).execute()
        else:
            # Crear primer paquete activo
            supabase.table("student_packages").insert({
                "student_id": student_id,
                "package_id": payment["package_id"],
                "vod_classes_total": vods,
                "vod_classes_completed": 0,
                "live_classes_total": lives,
                "live_classes_completed": 0,
                "status": "active"
            }).execute()

        return True
    except Exception as e:
        print(f"Error al aprobar pago: {e}")
        return False

def reject_payment(supabase, payment_id: str, coach_id: str, reason: str = "") -> bool:
    """Rechaza un pago P2P."""
    if not supabase:
        return False
    try:
        now = datetime.utcnow().isoformat()
        supabase.table("payments").update({
            "status": "rejected",
            "reviewed_by": coach_id,
            "reviewed_at": now,
            "notes": reason
        }).eq("id", payment_id).execute()
        return True
    except Exception as e:
        print(f"Error al rechazar pago: {e}")
        return False

# ==============================================================================
# 4. SESIONES Y AGENDAMIENTO
# ==============================================================================

def book_session(supabase, student_id: str, service_type: str, scheduled_at: str,
                 coach_id: str = "", duration_minutes: int = 45, vod_url: str = "", discord_tag: str = "perez1473") -> bool:
    """Programa una sesión para el estudiante (agendada por el coach o admin)."""
    if not supabase:
        return False
    try:
        data = {
            "student_id": student_id,
            "coach_id": coach_id or None,
            "service_type": service_type,
            "role_lane": "JUNGLE",
            "scheduled_at": scheduled_at,
            "duration_minutes": duration_minutes,
            "vod_url": vod_url,
            "discord_tag": discord_tag or "perez1473",
            "status": "scheduled"
        }
        supabase.table("sessions").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error al agendar sesión: {e}")
        return False

def get_student_sessions(supabase, student_id: str) -> List[Dict[str, Any]]:
    """Obtiene el historial y próximas sesiones de un alumno."""
    if not supabase:
        return []
    try:
        res = (supabase.table("sessions")
               .select("*")
               .eq("student_id", student_id)
               .order("scheduled_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al consultar sesiones del alumno: {e}")
        return []

def get_coach_sessions(supabase) -> List[Dict[str, Any]]:
    """Obtiene todas las sesiones programadas para el coach."""
    if not supabase:
        return []
    try:
        res = (supabase.table("sessions")
               .select("*, profiles!student_id(email, full_name, riot_id, discord_tag)")
               .order("scheduled_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al consultar sesiones del coach: {e}")
        return []

def complete_session(supabase, session_id: str, coach_id: str) -> bool:
    """Marca una sesión como completada y descuenta el crédito al estudiante."""
    if not supabase:
        return False
    try:
        now = datetime.utcnow().isoformat()
        # 1. Obtener la sesión
        s_res = supabase.table("sessions").select("*").eq("id", session_id).single().execute()
        session = s_res.data
        if not session:
            return False

        # 2. Actualizar estado
        supabase.table("sessions").update({
            "status": "completed",
            "coach_id": coach_id,
            "updated_at": now
        }).eq("id", session_id).execute()

        # 3. Descontar crédito del student_package activo si existe
        student_id = session.get("student_id")
        service_type = session.get("service_type")
        active_pkg = get_student_package(supabase, student_id)

        if active_pkg:
            pkg_id = active_pkg["id"]
            if service_type == "vod":
                comp = active_pkg.get("vod_classes_completed", 0) + 1
                supabase.table("student_packages").update({"vod_classes_completed": comp}).eq("id", pkg_id).execute()
            elif service_type == "live":
                comp = active_pkg.get("live_classes_completed", 0) + 1
                supabase.table("student_packages").update({"live_classes_completed": comp}).eq("id", pkg_id).execute()

        return True
    except Exception as e:
        print(f"Error al completar sesión: {e}")
        return False

# ==============================================================================
# 5. TAREAS Y FEEDBACK POST-SESIÓN
# ==============================================================================

def get_student_tasks(supabase, student_id: str) -> List[Dict[str, Any]]:
    """Obtiene las tareas asignadas a un estudiante."""
    if not supabase:
        return []
    try:
        res = (supabase.table("tasks")
               .select("*")
               .eq("student_id", student_id)
               .order("created_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al obtener tareas: {e}")
        return []

def assign_task(supabase, student_id: str, coach_id: str, title: str,
                description: str = "", category: str = "pathing", due_date: str = None) -> bool:
    """Crea una nueva tarea asignada por el coach."""
    if not supabase:
        return False
    try:
        data = {
            "student_id": student_id,
            "coach_id": coach_id,
            "title": title,
            "description": description,
            "category": category,
            "due_date": due_date,
            "is_completed": False
        }
        supabase.table("tasks").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error al asignar tarea: {e}")
        return False

def toggle_task(supabase, task_id: str, is_completed: bool) -> bool:
    """Marca una tarea como completada o pendiente."""
    if not supabase:
        return False
    try:
        now = datetime.utcnow().isoformat() if is_completed else None
        supabase.table("tasks").update({
            "is_completed": is_completed,
            "completed_at": now
        }).eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar tarea: {e}")
        return False

def save_session_notes(supabase, session_id: str, coach_id: str, student_id: str,
                       strengths: str, areas_to_improve: str, pathing: str,
                       champion_pool: str, homework_summary: str) -> bool:
    """Guarda las notas técnicas post-sesión del coach."""
    if not supabase:
        return False
    try:
        data = {
            "session_id": session_id,
            "coach_id": coach_id,
            "student_id": student_id,
            "key_strengths": strengths,
            "areas_to_improve": areas_to_improve,
            "pathing_feedback": pathing,
            "champion_pool_notes": champion_pool,
            "homework_summary": homework_summary
        }
        supabase.table("session_notes").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error al guardar notas de sesión: {e}")
        return False

# ==============================================================================
# 6. ADMINISTRACIÓN
# ==============================================================================

def get_all_users(supabase) -> List[Dict[str, Any]]:
    """Obtiene todos los usuarios de la plataforma para el panel Admin."""
    if not supabase:
        return []
    try:
        res = supabase.table("profiles").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []

def update_user_role(supabase, user_id: str, new_role: str) -> bool:
    """Actualiza el rol de un usuario ('student', 'coach', 'admin')."""
    if not supabase:
        return False
    try:
        supabase.table("profiles").update({"role": new_role}).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error al cambiar rol: {e}")
        return False
