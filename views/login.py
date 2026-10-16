import streamlit as st
from database.operations import get_profile, get_profile_by_email, upsert_profile, register_student

def render_login(supabase):
    st.markdown("<h2 class='main-title' style='text-align: center;'>🌲 PerezLoL Coaching Academy</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.8;'>Campus Virtual Profesional de League of Legends | Discord Head Coach: <code>perez1473</code></p>", unsafe_allow_html=True)
    
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
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse como Nuevo Estudiante"])

        with tab_login:
            st.subheader("🎓 Acceso de Alumnos y Coaches")
            st.caption("Ingresa con tu correo y contraseña registrados:")

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

        with tab_register:
            st.subheader("📝 Crear Cuenta de Invocador")
            st.caption("Regístrate en la academia. Al crear tu perfil, pasarás directo a seleccionar tu paquete de coaching:")

            with st.container(border=True):
                reg_name = st.text_input("Nombre Completo / Apodo", placeholder="Ej: Andrés Pérez", key="reg_name_input")
                reg_email = st.text_input("Correo Electrónico", placeholder="tu_correo@gmail.com", key="reg_email_input")

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    reg_pass = st.text_input("Contraseña (mínimo 6 caracteres)", type="password", key="reg_pass_input")
                with col_p2:
                    reg_pass_conf = st.text_input("Confirmar Contraseña", type="password", key="reg_pass_conf_input")

                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    reg_riot = st.text_input("Riot ID Oficial (Invocador#TAG)", placeholder="Perez#LAN", key="reg_riot_input")
                with col_r2:
                    reg_disc = st.text_input("Usuario de Discord", placeholder="perez1473", key="reg_disc_input")

                col_l1, col_l2, col_l3 = st.columns(3)
                with col_l1:
                    reg_lane = st.selectbox("Rol Principal en LoL", ["JUNGLE (Jungla)", "TOP (Carril Superior)", "MID (Carril Central)", "ADC (Tirador)", "SUPPORT (Soporte)"], index=0, key="reg_lane_sel")
                    lane_clean = reg_lane.split(" ")[0]
                with col_l2:
                    reg_tier = st.selectbox("Rango / Liga Actual", ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"], index=3, key="reg_tier_sel")
                with col_l3:
                    reg_rank = st.selectbox("División", ["I", "II", "III", "IV"], index=3, key="reg_rank_sel")

                st.write("")
                if st.button("🚀 Crear Mi Perfil y Escoger Paquete de Coaching", type="primary", use_container_width=True, key="btn_register_submit"):
                    if not reg_name or not reg_email or not reg_pass:
                        st.warning("Por favor completa al menos tu nombre, correo y contraseña.")
                    elif len(reg_pass) < 6:
                        st.error("La contraseña debe tener un mínimo de 6 caracteres.")
                    elif reg_pass != reg_pass_conf:
                        st.error("Las contraseñas no coinciden. Verifícalas.")
                    else:
                        new_profile = register_student(
                            supabase=supabase,
                            email=reg_email,
                            password=reg_pass,
                            full_name=reg_name,
                            riot_id=reg_riot or "Invocador#LAN",
                            discord_tag=reg_disc or "discord_user",
                            main_lane=lane_clean,
                            current_tier=reg_tier,
                            current_rank=reg_rank,
                            current_lp=0
                        )
                        if new_profile:
                            st.session_state["user"] = {
                                "id": new_profile["id"],
                                "email": new_profile["email"],
                                "role": "student",
                                "full_name": new_profile.get("full_name", reg_name),
                                "riot_id": new_profile.get("riot_id", reg_riot),
                                "discord_tag": new_profile.get("discord_tag", reg_disc)
                            }
                            st.session_state["just_registered"] = True
                            st.session_state["student_target_module"] = "🛒 Comprar Clases / Recargar (P2P)"
                            st.success(f"¡Bienvenido a la academia, {reg_name}! Redirigiendo a la tienda de paquetes...")
                            st.rerun()
                        else:
                            st.error("Hubo un error al registrar el estudiante en la base de datos.")

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
