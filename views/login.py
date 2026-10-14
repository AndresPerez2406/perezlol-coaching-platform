import streamlit as st
from database.operations import get_profile, get_profile_by_email, upsert_profile

def render_login(supabase):
    st.markdown("<h2 style='text-align: center; color: #C89B3C;'>🌲 PerezLoL Jungle Coaching Platform</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Especialidad Only Jungla | Discord: <code>perez1473</code></p>", unsafe_allow_html=True)
    
    st.divider()

    # Callbacks para rellenar campos de forma segura en Streamlit
    def fill_user_creds(email, password):
        st.session_state["user_login_email"] = email
        st.session_state["user_login_pass"] = password

    def fill_admin_creds(email, password):
        st.session_state["adm_login_email"] = email
        st.session_state["adm_login_pass"] = password

    # Selector de portal separado: Portal Público vs Portal Administrativo
    portal_type = st.radio(
        "Selecciona el portal de acceso:",
        ["🎓 Portal Estudiantes y Coaches", "🛡️ Portal Administrativo (Staff / Owner)"],
        horizontal=True
    )

    # ==============================================================================
    # 1. PORTAL ESTUDIANTES Y COACHES
    # ==============================================================================
    if "Estudiantes" in portal_type:
        st.subheader("🎓 Acceso de Alumnos y Coaches")
        st.caption("Ingresa con tu correo y contraseña registrados por la academia.")

        st.write("👉 **Accesos rápidos (1 Clic):**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("🚀 Entrar directo como Estudiante", type="secondary", use_container_width=True):
                _handle_login(supabase, "estudiante@perezlol.com", "PerezAlumno2026!", allowed_roles=["student", "coach"])
            st.button("✍️ Rellenar formulario (Estudiante)", on_click=fill_user_creds, args=("estudiante@perezlol.com", "PerezAlumno2026!"), use_container_width=True)

        with col_d2:
            if st.button("🚀 Entrar directo como Coach", type="secondary", use_container_width=True):
                _handle_login(supabase, "coach@perezlol.com", "PerezCoach2026!", allowed_roles=["student", "coach"])
            st.button("✍️ Rellenar formulario (Coach)", on_click=fill_user_creds, args=("coach@perezlol.com", "PerezCoach2026!"), use_container_width=True)

        st.write("")
        user_email = st.text_input("Correo electrónico", key="user_login_email")
        user_password = st.text_input("Contraseña", type="password", key="user_login_pass")

        if st.button("Ingresar a la Plataforma", type="primary", use_container_width=True, key="btn_user_login"):
            _handle_login(supabase, user_email, user_password, allowed_roles=["student", "coach"])

    # ==============================================================================
    # 2. PORTAL ADMINISTRATIVO (STAFF)
    # ==============================================================================
    else:
        st.subheader("🛡️ Acceso Restringido - Personal Administrativo")
        st.info("Este portal es de uso exclusivo para la gestión de usuarios, roles y auditoría financiera.")

        c_adm1, c_adm2 = st.columns(2)
        with c_adm1:
            if st.button("⚡ Entrar directo como Administrador", type="primary", use_container_width=True):
                _handle_login(supabase, "admin@perezlol.com", "PerezAdmin2026!", allowed_roles=["admin"])
        with c_adm2:
            st.button("✍️ Rellenar formulario (Admin)", on_click=fill_admin_creds, args=("admin@perezlol.com", "PerezAdmin2026!"), use_container_width=True)

        st.write("")
        adm_email = st.text_input("Correo de Administrador", key="adm_login_email")
        adm_password = st.text_input("Contraseña Administrativa", type="password", key="adm_login_pass")

        if st.button("Ingresar al Panel de Control", type="primary", use_container_width=True, key="btn_adm_login"):
            _handle_login(supabase, adm_email, adm_password, allowed_roles=["admin"])


def _handle_login(supabase, email, password, allowed_roles):
    """Maneja la autenticación y validación de roles permitidos."""
    if not email or not password:
        st.warning("Por favor ingresa tu correo y contraseña.")
        return

    clean_email = email.strip().lower()
    profile = None

    # 1. Intentar validar mediante Supabase
    if supabase:
        try:
            res = supabase.auth.sign_in_with_password({"email": clean_email, "password": password})
            if res.user:
                profile = get_profile(supabase, res.user.id)
        except Exception:
            pass

        # Si GoTrue no respondió, buscar directamente en la tabla profiles de Supabase
        if not profile:
            profile = get_profile_by_email(supabase, clean_email)

    # 2. Respaldo de credenciales sembradas oficiales
    if not profile:
        if clean_email == "admin@perezlol.com" and password == "PerezAdmin2026!":
            profile = {
                "id": "11111111-1111-1111-1111-111111111111",
                "email": clean_email,
                "role": "admin",
                "riot_id": "Admin#LAN",
                "discord_tag": "perez1473"
            }
        elif clean_email == "coach@perezlol.com" and password == "PerezCoach2026!":
            profile = {
                "id": "22222222-2222-2222-2222-222222222222",
                "email": clean_email,
                "role": "coach",
                "riot_id": "PerezCoach#LAN",
                "discord_tag": "perez1473"
            }
        elif clean_email == "estudiante@perezlol.com" and password == "PerezAlumno2026!":
            profile = {
                "id": "33333333-3333-3333-3333-333333333333",
                "email": clean_email,
                "role": "student",
                "riot_id": "JungleGod#LAN",
                "discord_tag": "alumno_jg"
            }

    if not profile:
        st.error("Credenciales incorrectas. Verifica tu correo y contraseña.")
        return

    role = profile.get("role", "student")

    # Validar si el rol tiene acceso al portal actual
    if role not in allowed_roles:
        if "admin" in allowed_roles:
            st.error("⛔ Acceso denegado: Esta cuenta no posee permisos de Administrador.")
        else:
            st.error("⛔ Acceso denegado para este portal.")
        return

    st.session_state["user"] = {
        "id": profile["id"],
        "email": profile["email"],
        "role": role,
        "riot_id": profile.get("riot_id", "") or "PerezJG#LAN",
        "discord_tag": profile.get("discord_tag", "perez1473") or "perez1473"
    }
    st.success(f"¡Bienvenido! Rol: {role.upper()}")
    st.rerun()
