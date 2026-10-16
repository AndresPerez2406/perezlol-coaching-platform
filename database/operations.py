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
        # 1. Intentar crear usuario confirmado mediante admin api
        if hasattr(supabase.auth, "admin"):
            try:
                res = supabase.auth.admin.create_user({
                    "email": clean_email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {
                        "role": "student",
                        "full_name": full_name,
                        "riot_id": riot_id,
                        "discord_tag": discord_tag
                    }
                })
                if res.user:
                    user_id = res.user.id
            except Exception as e_adm:
                print(f"Aviso admin create_user: {e_adm}")

        # 2. Fallback a sign_up
        if not user_id:
            try:
                res = supabase.auth.sign_up({
                    "email": clean_email,
                    "password": password
                })
                if res.user:
                    user_id = res.user.id
            except Exception as e_sign:
                print(f"Aviso auth sign_up: {e_sign}")

        if not user_id:
            return None

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

def register_student(supabase, email: str, password: str, full_name: str,
                     riot_id: str, discord_tag: str, main_lane: str = "JUNGLE",
                     current_tier: str = "EMERALD", current_rank: str = "IV",
                     current_lp: int = 0) -> Optional[Dict[str, Any]]:
    """Auto-registro de estudiante desde la pantalla de bienvenida."""
    if not supabase or not email or not password:
        return None
    clean_email = email.strip().lower()
    try:
        user_id = None
        # 1. Crear usuario confirmado en Supabase Auth
        if hasattr(supabase.auth, "admin"):
            try:
                res = supabase.auth.admin.create_user({
                    "email": clean_email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {
                        "role": "student",
                        "full_name": full_name,
                        "riot_id": riot_id,
                        "discord_tag": discord_tag,
                        "main_lane": main_lane
                    }
                })
                if res.user:
                    user_id = res.user.id
            except Exception as e_adm:
                print(f"Aviso admin create_user: {e_adm}")

        # 2. Fallback sign_up
        if not user_id:
            try:
                res = supabase.auth.sign_up({
                    "email": clean_email,
                    "password": password
                })
                if res.user:
                    user_id = res.user.id
            except Exception as e_auth:
                print(f"Aviso auth sign_up: {e_auth}")

        if not user_id:
            return None

        # 3. Guardar ficha de perfil en tabla profiles
        profile_data = {
            "id": user_id,
            "email": clean_email,
            "full_name": full_name,
            "role": "student",
            "riot_id": riot_id or "Invocador#LAN",
            "discord_tag": discord_tag or "discord_user",
            "main_lane": main_lane or "JUNGLE",
            "current_tier": current_tier or "GOLD",
            "current_rank": current_rank or "IV",
            "current_lp": current_lp or 0,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("profiles").upsert(profile_data).execute()
        return profile_data
    except Exception as e:
        print(f"Error al auto-registrar estudiante: {e}")
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

def get_coach_tasks(supabase, coach_id: str = None) -> List[Dict[str, Any]]:
    """Obtiene todas las tareas asignadas por el coach (con datos del alumno)."""
    if not supabase:
        return []
    try:
        # Intentar traer datos del perfil del alumno
        q = supabase.table("tasks").select("*, profiles!student_id(full_name, email, riot_id, discord_tag)")
        if coach_id:
            q = q.eq("coach_id", coach_id)
        res = q.order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        # Fallback sin join
        try:
            q = supabase.table("tasks").select("*")
            if coach_id:
                q = q.eq("coach_id", coach_id)
            res = q.order("created_at", desc=True).execute()
            return res.data or []
        except Exception:
            return []

def update_task_feedback(supabase, task_id: str, feedback: str) -> bool:
    """Permite al coach dejar notas/feedback técnico sobre una tarea entregada."""
    if not supabase or not task_id:
        return False
    try:
        supabase.table("tasks").update({
            "coach_feedback": feedback
        }).eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar feedback de tarea: {e}")
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

# ==============================================================================
# 7. CRUD AVANZADO DE ADMINISTRADOR
# ==============================================================================

# --- A. CRUD PAQUETES Y MODOS DE COACHING ---

def get_all_packages_admin(supabase) -> List[Dict[str, Any]]:
    """Obtiene todos los paquetes (activos e inactivos) para gestión de admin."""
    if not supabase:
        return []
    try:
        res = supabase.table("packages").select("*").order("created_at", desc=False).execute()
        return res.data or []
    except Exception as e:
        print(f"Error al consultar paquetes admin: {e}")
        return []

def create_package(supabase, title: str, description: str, price: float,
                   vod_classes: int, live_classes: int, service_type: str = "combo",
                   is_recommended: bool = False, is_active: bool = True) -> bool:
    """Crea un nuevo paquete o modo de coaching en el catálogo."""
    if not supabase:
        return False
    try:
        data = {
            "title": title,
            "description": description,
            "price": price,
            "vod_classes": vod_classes,
            "live_classes": live_classes,
            "service_type": service_type,
            "is_recommended": is_recommended,
            "is_active": is_active,
            "currency": "USD"
        }
        supabase.table("packages").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error al crear paquete: {e}")
        return False

def update_package(supabase, package_id: str, title: str, description: str,
                   price: float, vod_classes: int, live_classes: int,
                   service_type: str = "combo", is_recommended: bool = False,
                   is_active: bool = True) -> bool:
    """Edita un paquete o modo de coaching existente."""
    if not supabase or not package_id:
        return False
    try:
        data = {
            "title": title,
            "description": description,
            "price": price,
            "vod_classes": vod_classes,
            "live_classes": live_classes,
            "service_type": service_type,
            "is_recommended": is_recommended,
            "is_active": is_active
        }
        supabase.table("packages").update(data).eq("id", package_id).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar paquete: {e}")
        return False

def delete_package(supabase, package_id: str) -> bool:
    """Elimina un paquete del catálogo (o lo desactiva si tiene referencias)."""
    if not supabase or not package_id:
        return False
    try:
        try:
            supabase.table("packages").delete().eq("id", package_id).execute()
            return True
        except Exception:
            # Si tiene pagos o paquetes asociados, desactivar en lugar de romper integridad
            supabase.table("packages").update({"is_active": False}).eq("id", package_id).execute()
            return True
    except Exception as e:
        print(f"Error al eliminar paquete: {e}")
        return False

# --- B. CRUD ESTUDIANTES Y GESTIÓN DE CRÉDITOS ---

def get_students_detailed(supabase) -> List[Dict[str, Any]]:
    """Obtiene todos los estudiantes con sus paquetes de clases asociados."""
    if not supabase:
        return []
    try:
        res = (supabase.table("profiles")
               .select("*, student_packages(*, packages(*))")
               .eq("role", "student")
               .order("created_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al obtener estudiantes detallados: {e}")
        try:
            r = supabase.table("profiles").select("*").eq("role", "student").order("created_at", desc=True).execute()
            return r.data or []
        except Exception:
            return []

def update_student_profile(supabase, user_id: str, full_name: str, riot_id: str,
                           discord_tag: str, current_tier: str, current_rank: str,
                           current_lp: int, main_lane: str = "JUNGLE") -> bool:
    """Actualiza los datos competitivos y de perfil de un estudiante."""
    if not supabase or not user_id:
        return False
    try:
        data = {
            "full_name": full_name,
            "riot_id": riot_id,
            "discord_tag": discord_tag,
            "current_tier": current_tier,
            "current_rank": current_rank,
            "current_lp": current_lp,
            "main_lane": main_lane,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("profiles").update(data).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar estudiante: {e}")
        return False

def adjust_student_credits(supabase, student_id: str, vod_remaining: int,
                           live_remaining: int, vod_total: int = None,
                           live_total: int = None) -> bool:
    """Ajusta o añade manualmente créditos a un estudiante."""
    if not supabase or not student_id:
        return False
    try:
        active_pkg = get_student_package(supabase, student_id)
        if active_pkg:
            update_data = {
                "vod_classes_remaining": max(0, vod_remaining),
                "live_classes_remaining": max(0, live_remaining)
            }
            if vod_total is not None:
                update_data["vod_classes_total"] = vod_total
            if live_total is not None:
                update_data["live_classes_total"] = live_total
            supabase.table("student_packages").update(update_data).eq("id", active_pkg["id"]).execute()
            return True
        else:
            # Crear paquete activo directo para el alumno
            pkgs = get_packages(supabase)
            pkg_id = pkgs[0]["id"] if pkgs else None
            data = {
                "student_id": student_id,
                "package_id": pkg_id,
                "vod_classes_total": vod_total or vod_remaining,
                "vod_classes_completed": 0,
                "vod_classes_remaining": vod_remaining,
                "live_classes_total": live_total or live_remaining,
                "live_classes_completed": 0,
                "live_classes_remaining": live_remaining,
                "status": "active"
            }
            supabase.table("student_packages").insert(data).execute()
            return True
    except Exception as e:
        print(f"Error al ajustar créditos del estudiante: {e}")
        return False

def delete_user(supabase, user_id: str) -> bool:
    """Elimina el perfil de un usuario."""
    if not supabase or not user_id:
        return False
    try:
        supabase.table("profiles").delete().eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False

# --- C. CRUD SESIONES DE COACHING ---

def get_all_sessions_admin(supabase) -> List[Dict[str, Any]]:
    """Obtiene todas las sesiones registradas con datos de alumno y coach."""
    if not supabase:
        return []
    try:
        res = (supabase.table("sessions")
               .select("*, student:profiles!student_id(email, full_name, riot_id, discord_tag), coach:profiles!coach_id(email, full_name, discord_tag)")
               .order("scheduled_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al consultar sesiones admin: {e}")
        return []

def admin_create_session(supabase, student_id: str, coach_id: str, service_type: str,
                         role_lane: str, scheduled_at: str, duration_minutes: int = 45,
                         discord_tag: str = "perez1473") -> bool:
    """Crea una sesión de coaching directamente desde administración."""
    return book_session(
        supabase=supabase,
        student_id=student_id,
        service_type=service_type,
        scheduled_at=scheduled_at,
        coach_id=coach_id,
        duration_minutes=duration_minutes,
        vod_url="",
        discord_tag=discord_tag,
        role_lane=role_lane
    )

def admin_update_session(supabase, session_id: str, service_type: str,
                         role_lane: str, scheduled_at: str, duration_minutes: int,
                         status: str, coach_id: str = None) -> bool:
    """Modifica fecha, hora, estado o coach de una sesión."""
    if not supabase or not session_id:
        return False
    try:
        data = {
            "service_type": service_type,
            "role_lane": role_lane,
            "scheduled_at": scheduled_at,
            "duration_minutes": duration_minutes,
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        if coach_id:
            data["coach_id"] = coach_id
        supabase.table("sessions").update(data).eq("id", session_id).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar sesión: {e}")
        return False

def admin_delete_session(supabase, session_id: str) -> bool:
    """Elimina una sesión agendada."""
    if not supabase or not session_id:
        return False
    try:
        supabase.table("sessions").delete().eq("id", session_id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar sesión: {e}")
        return False

# --- D. CRUD PAGOS P2P ---

def get_all_payments_admin(supabase) -> List[Dict[str, Any]]:
    """Obtiene el historial completo de pagos con datos de alumnos y paquetes."""
    if not supabase:
        return []
    try:
        res = (supabase.table("payments")
               .select("*, profiles!student_id(email, full_name, riot_id, discord_tag), packages(title, price)")
               .order("created_at", desc=True)
               .execute())
        return res.data or []
    except Exception as e:
        print(f"Error al consultar pagos admin: {e}")
        return []

def admin_create_payment(supabase, student_id: str, package_id: str, amount: float,
                         payment_method: str, status: str = "approved",
                         auto_credit: bool = True) -> bool:
    """Registra un pago manual y opcionalmente acredita las clases al alumno."""
    if not supabase or not student_id:
        return False
    try:
        data = {
            "student_id": student_id,
            "package_id": package_id or None,
            "amount": amount,
            "payment_method": payment_method,
            "reference_number": "MANUAL-ADMIN",
            "receipt_url": "",
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        }
        res = supabase.table("payments").insert(data).execute()
        
        # Si se marca aprobado y se desea auto-acreditar
        if auto_credit and status == "approved" and package_id:
            pkg_res = supabase.table("packages").select("*").eq("id", package_id).maybe_single().execute()
            if pkg_res.data:
                pkg = pkg_res.data
                vods = pkg.get("vod_classes", 0)
                lives = pkg.get("live_classes", 0)
                
                # Acreditar al student_package activo o crear uno
                active_sp = get_student_package(supabase, student_id)
                if active_sp:
                    supabase.table("student_packages").update({
                        "vod_classes_total": active_sp.get("vod_classes_total", 0) + vods,
                        "vod_classes_remaining": active_sp.get("vod_classes_remaining", 0) + vods,
                        "live_classes_total": active_sp.get("live_classes_total", 0) + lives,
                        "live_classes_remaining": active_sp.get("live_classes_remaining", 0) + lives
                    }).eq("id", active_sp["id"]).execute()
                else:
                    supabase.table("student_packages").insert({
                        "student_id": student_id,
                        "package_id": package_id,
                        "vod_classes_total": vods,
                        "vod_classes_completed": 0,
                        "vod_classes_remaining": vods,
                        "live_classes_total": lives,
                        "live_classes_completed": 0,
                        "live_classes_remaining": lives,
                        "status": "active"
                    }).execute()
        return True
    except Exception as e:
        print(f"Error al registrar pago manual: {e}")
        return False

def admin_update_payment(supabase, payment_id: str, status: str,
                         amount: float = None, payment_method: str = None,
                         notes: str = "") -> bool:
    """Actualiza el estado, monto o método de un pago."""
    if not supabase or not payment_id:
        return False
    try:
        update_data = {
            "status": status,
            "reviewed_at": datetime.utcnow().isoformat()
        }
        if amount is not None:
            update_data["amount"] = amount
        if payment_method:
            update_data["payment_method"] = payment_method
        if notes:
            update_data["notes"] = notes
            
        supabase.table("payments").update(update_data).eq("id", payment_id).execute()
        
        # Si se aprobó el pago, acreditar las clases
        if status == "approved":
            p_res = supabase.table("payments").select("*, packages(*)").eq("id", payment_id).maybe_single().execute()
            if p_res.data and p_res.data.get("packages"):
                pkg = p_res.data["packages"]
                st_id = p_res.data.get("student_id")
                vods = pkg.get("vod_classes", 0)
                lives = pkg.get("live_classes", 0)
                
                active_sp = get_student_package(supabase, st_id)
                if active_sp:
                    supabase.table("student_packages").update({
                        "vod_classes_total": active_sp.get("vod_classes_total", 0) + vods,
                        "vod_classes_remaining": active_sp.get("vod_classes_remaining", 0) + vods,
                        "live_classes_total": active_sp.get("live_classes_total", 0) + lives,
                        "live_classes_remaining": active_sp.get("live_classes_remaining", 0) + lives
                    }).eq("id", active_sp["id"]).execute()
                else:
                    supabase.table("student_packages").insert({
                        "student_id": st_id,
                        "package_id": pkg.get("id"),
                        "vod_classes_total": vods,
                        "vod_classes_completed": 0,
                        "vod_classes_remaining": vods,
                        "live_classes_total": lives,
                        "live_classes_completed": 0,
                        "live_classes_remaining": lives,
                        "status": "active"
                    }).execute()
        return True
    except Exception as e:
        print(f"Error al actualizar pago admin: {e}")
        return False

def admin_delete_payment(supabase, payment_id: str) -> bool:
    """Elimina un registro de pago."""
    if not supabase or not payment_id:
        return False
    try:
        supabase.table("payments").delete().eq("id", payment_id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar pago: {e}")
        return False

