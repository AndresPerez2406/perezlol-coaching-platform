import streamlit as st
from database.operations import get_all_users, update_user_role, get_packages

def render_admin_view(supabase, user, active_module=None):
    st.title("⚡ Panel de Administración Central")
    st.caption(f"Administrador: **{user.get('email', 'Admin')}**")
    mod = active_module or "👥 Gestión de Usuarios y Roles"

    # Obtener usuarios desde la base de datos
    users = get_all_users(supabase)
    total_users = len(users)
    students_count = len([u for u in users if u.get("role") == "student"])
    coaches_count = len([u for u in users if u.get("role") == "coach"])
    admins_count = len([u for u in users if u.get("role") == "admin"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Usuarios", total_users)
    with col2:
        st.metric("Estudiantes", students_count)
    with col3:
        st.metric("Coaches Activos", coaches_count)
    with col4:
        st.metric("Administradores", admins_count)

    st.divider()

    # ==============================================================================
    # MÓDULO 1: USUARIOS Y ROLES
    # ==============================================================================
    if "Usuarios" in mod:
        st.subheader("👥 Gestión de Usuarios y Permisos")
        st.caption("Gestiona los permisos y roles de los usuarios registrados en Supabase:")

        if users:
            display_data = [{
                "Email": u.get("email"),
                "Nombre": u.get("full_name") or "Sin nombre",
                "Rol Actual": u.get("role"),
                "Riot ID": u.get("riot_id") or "No vinculado",
                "Discord": u.get("discord_tag") or "perez1473",
                "ID": u.get("id")
            } for u in users]
            st.dataframe(display_data, use_container_width=True)

            st.divider()
            st.subheader("Modificar Rol de Usuario")
            c_sel, c_role, c_btn = st.columns([2, 1, 1])
            with c_sel:
                user_options = {f"{u.get('email')} ({u.get('role')})": u.get("id") for u in users}
                selected_label = st.selectbox("Selecciona un usuario", list(user_options.keys()))
                target_user_id = user_options.get(selected_label)
            with c_role:
                new_role = st.selectbox("Nuevo Rol", ["student", "coach", "admin"])
            with c_btn:
                st.write("")
                st.write("")
                if st.button("Actualizar Rol", type="primary"):
                    if target_user_id:
                        ok = update_user_role(supabase, target_user_id, new_role)
                        if ok:
                            st.success(f"Rol actualizado a '{new_role}'.")
                            st.rerun()
                        else:
                            st.error("Error al actualizar rol en Supabase.")

        st.divider()
        st.subheader("➕ Crear / Matricular Usuario Directamente")
        with st.container(border=True):
            col_au1, col_au2 = st.columns(2)
            with col_au1:
                adm_u_name = st.text_input("Nombre Completo", key="adm_u_name")
                adm_u_email = st.text_input("Correo Electrónico", key="adm_u_email")
                adm_u_pass = st.text_input("Contraseña (mín. 6 caracteres)", value="Perez2026!", type="password", key="adm_u_pass")
            with col_au2:
                adm_u_role = st.selectbox("Rol Asignado", ["student", "coach", "admin"], key="adm_u_role")
                adm_u_riot = st.text_input("Riot ID (ej: Invocador#LAN)", key="adm_u_riot")
                adm_u_disc = st.text_input("Discord Tag", placeholder="ej: usuario_disc", key="adm_u_disc")

            if st.button("Registrar Usuario en la Plataforma", type="primary", use_container_width=True):
                if not adm_u_email or not adm_u_pass or not adm_u_name:
                    st.warning("Completa los datos requeridos.")
                else:
                    from database.operations import upsert_profile
                    import uuid
                    u_id = str(uuid.uuid4())
                    ok = upsert_profile(
                        supabase=supabase,
                        user_id=u_id,
                        email=adm_u_email.strip().lower(),
                        role=adm_u_role,
                        riot_id=adm_u_riot,
                        discord_tag=adm_u_disc or "perez1473",
                        full_name=adm_u_name
                    )
                    if ok:
                        st.success(f"Usuario {adm_u_name} ({adm_u_role}) registrado con éxito.")
                        st.rerun()
                    else:
                        st.error("Error al registrar usuario.")

    # ==============================================================================
    # MÓDULO 2: CATÁLOGO DE PAQUETES
    # ==============================================================================
    elif "Paquetes" in mod:
        st.subheader("📦 Catálogo de Paquetes Only JG")
        packages = get_packages(supabase)
        if packages:
            st.dataframe(packages, use_container_width=True)
        else:
            st.write("Mostrando paquetes por defecto de PerezLoL Coaching:")
            st.markdown("""
            * **Sesión VOD Review:** $3.50 USD (1 VOD)
            * **Pack 4 VODs:** $12.00 USD (4 VODs)
            * **LIVE GAME:** $5.00 USD (1 Live)
            * **Pack Primer Coaching (Recomendado):** $14.00 USD (1 Live + 3 VODs)
            """)

    # ==============================================================================
    # MÓDULO 3: AUDITORÍA DE PAGOS
    # ==============================================================================
    elif "Auditoría" in mod:
        st.subheader("📑 Auditoría Global de Pagos y Transacciones P2P")
        try:
            res = (supabase.table("payments")
                   .select("*, profiles!student_id(email), packages(title, price)")
                   .order("created_at", desc=True)
                   .execute())
            payments = res.data or []
            if payments:
                audit_rows = [{
                    "Fecha": p.get("created_at")[:10],
                    "Alumno": p.get("profiles", {}).get("email") if p.get("profiles") else "N/A",
                    "Paquete": p.get("packages", {}).get("title") if p.get("packages") else "N/A",
                    "Monto ($ USD)": f"${p.get('amount')}",
                    "Método": p.get("payment_method"),
                    "Comprobante": "🖼️ Adjunto" if p.get("receipt_url") else "Sin imagen",
                    "Estado": p.get("status").capitalize()
                } for p in payments]
                st.dataframe(audit_rows, use_container_width=True)
            else:
                st.info("No hay pagos registrados aún en el sistema.")
        except Exception:
            st.info("Sin registros de pagos disponibles todavía.")
