"""
Módulo de Administración Central - PerezLoL Coaching Academy
Permite el control y CRUD completo de:
1. Paquetes y Modos de Coaching
2. Estudiantes y Créditos de Clases
3. Agenda y Sesiones de Coaching
4. Pagos P2P (Aprobación, Creación manual, Edición)
5. Coaches y Roles de Usuario
"""
import streamlit as st
from datetime import datetime, date
import uuid

from database.operations import (
    get_all_users, update_user_role, upsert_profile, delete_user,
    get_all_packages_admin, create_package, update_package, delete_package,
    get_students_detailed, update_student_profile, adjust_student_credits, get_student_package,
    get_all_sessions_admin, admin_create_session, admin_update_session, admin_delete_session,
    get_all_payments_admin, admin_create_payment, admin_update_payment, admin_delete_payment,
    get_packages
)

def render_admin_view(supabase, user, active_module=None):
    st.title("⚡ Panel de Control Administrativo")
    st.caption(f"Administrador en sesión: **{user.get('email', 'Admin')}**")
    mod = active_module or "📦 Paquetes & Modos de Coaching"

    all_users = get_all_users(supabase)
    students = [u for u in all_users if u.get("role") == "student"]
    coaches = [u for u in all_users if u.get("role") == "coach"]
    packages = get_all_packages_admin(supabase)
    payments = get_all_payments_admin(supabase)
    sessions = get_all_sessions_admin(supabase)

    # Métricas Globales Rápidas en Cabecera
    c_g1, c_g2, c_g3, c_g4 = st.columns(4)
    with c_g1:
        st.metric("Alumnos Registrados", len(students))
    with c_g2:
        st.metric("Coaches Activos", len(coaches))
    with c_g3:
        st.metric("Paquetes / Modos", len(packages))
    with c_g4:
        st.metric("Sesiones en Agenda", len(sessions))

    st.divider()

    # ==============================================================================
    # 1. CRUD DE PAQUETES Y NUEVOS MODOS DE COACHING
    # ==============================================================================
    if "Paquetes" in mod:
        st.subheader("📦 Gestión y Creación de Paquetes / Modos de Coaching")
        st.caption("Crea nuevos planes, ajusta tarifas, añade modos (VOD, LIVE, Dúo, 5v5) o desactiva paquetes obsoletos:")

        # Tabla Resumen de Paquetes
        if packages:
            pkg_rows = [{
                "ID": p.get("id")[:8] + "...",
                "Título": p.get("title"),
                "Tipo / Modo": (p.get("service_type") or "combo").upper(),
                "Precio ($ USD)": f"${p.get('price'):.2f}",
                "VODs": p.get("vod_classes", 0),
                "LIVEs": p.get("live_classes", 0),
                "Total Clases": p.get("total_classes", 0),
                "Recomendado": "⭐ Sí" if p.get("is_recommended") else "No",
                "Estado": "🟢 Activo" if p.get("is_active", True) else "🔴 Inactivo"
            } for p in packages]
            st.dataframe(pkg_rows, use_container_width=True)
        else:
            st.info("No hay paquetes registrados en la base de datos.")

        st.write("")
        tab_p1, tab_p2, tab_p3 = st.tabs(["➕ Crear Nuevo Paquete / Modo", "✏️ Editar Paquete", "🗑️ Eliminar o Desactivar"])

        # TAB 1: CREAR PAQUETE
        with tab_p1:
            st.markdown("#### ➕ Crear Nuevo Paquete o Modo de Coaching")
            with st.container(border=True):
                col_cp1, col_cp2 = st.columns(2)
                with col_cp1:
                    new_pkg_title = st.text_input("Título del Paquete / Modo *", placeholder="ej. Pack 4 VODs Reviews, Dúo Coaching LIVE, Team 5v5")
                    new_pkg_type = st.selectbox("Modo de Servicio *", ["combo", "vod", "live", "team", "custom"], help="Define si es VOD, LIVE, Combo o especial")
                    new_pkg_price = st.number_input("Precio ($ USD) *", min_value=0.0, value=12.0, step=0.5)
                with col_cp2:
                    new_pkg_vods = st.number_input("Clases VOD Review incluidas", min_value=0, value=4, step=1)
                    new_pkg_lives = st.number_input("Clases LIVE Game incluidas", min_value=0, value=0, step=1)
                    col_chk1, col_chk2 = st.columns(2)
                    with col_chk1:
                        new_pkg_recom = st.checkbox("⭐ Destacar como Recomendado", value=False)
                    with col_chk2:
                        new_pkg_act = st.checkbox("🟢 Activo en Tienda", value=True)

                new_pkg_desc = st.text_area("Descripción detallada del paquete / modo", placeholder="Explica en qué consiste el coaching, duración de las clases y puntos a trabajar...")

                if st.button("💾 Guardar y Publicar Nuevo Paquete", type="primary", use_container_width=True):
                    if not new_pkg_title:
                        st.warning("⚠️ Debes asignar un título al paquete.")
                    else:
                        ok = create_package(
                            supabase=supabase,
                            title=new_pkg_title,
                            description=new_pkg_desc,
                            price=float(new_pkg_price),
                            vod_classes=int(new_pkg_vods),
                            live_classes=int(new_pkg_lives),
                            service_type=new_pkg_type,
                            is_recommended=new_pkg_recom,
                            is_active=new_pkg_act
                        )
                        if ok:
                            st.success(f"¡Paquete '{new_pkg_title}' creado y publicado con éxito!")
                            st.rerun()
                        else:
                            st.error("Error al registrar paquete en la base de datos.")

        # TAB 2: EDITAR PAQUETE
        with tab_p2:
            st.markdown("#### ✏️ Modificar Tarifas y Contenido de Paquetes")
            if packages:
                pkg_map = {f"{p.get('title')} (${p.get('price')} USD)": p for p in packages}
                sel_edit_label = st.selectbox("Selecciona el paquete a modificar", list(pkg_map.keys()), key="sel_pkg_edit")
                curr_p = pkg_map[sel_edit_label]

                with st.container(border=True):
                    col_ep1, col_ep2 = st.columns(2)
                    with col_ep1:
                        edit_title = st.text_input("Título", value=curr_p.get("title", ""), key="ep_title")
                        edit_type = st.selectbox("Modo de Servicio", ["combo", "vod", "live", "team", "custom"], 
                                                index=["combo", "vod", "live", "team", "custom"].index(curr_p.get("service_type") if curr_p.get("service_type") in ["combo", "vod", "live", "team", "custom"] else "combo"), key="ep_type")
                        edit_price = st.number_input("Precio ($ USD)", min_value=0.0, value=float(curr_p.get("price", 0.0)), step=0.5, key="ep_price")
                    with col_ep2:
                        edit_vods = st.number_input("VODs Reviews", min_value=0, value=int(curr_p.get("vod_classes", 0)), step=1, key="ep_vods")
                        edit_lives = st.number_input("LIVEs Games", min_value=0, value=int(curr_p.get("live_classes", 0)), step=1, key="ep_lives")
                        c_echk1, c_echk2 = st.columns(2)
                        with c_echk1:
                            edit_recom = st.checkbox("⭐ Recomendado", value=bool(curr_p.get("is_recommended", False)), key="ep_recom")
                        with c_echk2:
                            edit_act = st.checkbox("🟢 Activo", value=bool(curr_p.get("is_active", True)), key="ep_act")

                    edit_desc = st.text_area("Descripción", value=curr_p.get("description", "") or "", key="ep_desc")

                    if st.button("💾 Guardar Cambios del Paquete", type="primary", use_container_width=True):
                        ok = update_package(
                            supabase=supabase,
                            package_id=curr_p.get("id"),
                            title=edit_title,
                            description=edit_desc,
                            price=float(edit_price),
                            vod_classes=int(edit_vods),
                            live_classes=int(edit_lives),
                            service_type=edit_type,
                            is_recommended=edit_recom,
                            is_active=edit_act
                        )
                        if ok:
                            st.success(f"¡Paquete '{edit_title}' actualizado correctamente!")
                            st.rerun()
                        else:
                            st.error("Error al actualizar el paquete.")
            else:
                st.info("No hay paquetes disponibles para editar.")

        # TAB 3: ELIMINAR O DESACTIVAR
        with tab_p3:
            st.markdown("#### 🗑️ Eliminar o Desactivar Paquetes")
            if packages:
                pkg_del_map = {f"{p.get('title')} (${p.get('price')} USD)": p for p in packages}
                sel_del_label = st.selectbox("Selecciona el paquete", list(pkg_del_map.keys()), key="sel_pkg_del")
                del_target = pkg_del_map[sel_del_label]

                st.warning(f"¿Estás seguro de que deseas eliminar o retirar el paquete **'{del_target.get('title')}'**?")
                col_dbtn1, col_dbtn2 = st.columns(2)
                with col_dbtn1:
                    if st.button("🚫 Desactivar Paquete (Ocultar de la Tienda)", use_container_width=True):
                        update_package(supabase, del_target.get("id"), del_target.get("title"), del_target.get("description"),
                                       float(del_target.get("price")), int(del_target.get("vod_classes")), int(del_target.get("live_classes")),
                                       del_target.get("service_type"), False, False)
                        st.success("Paquete desactivado.")
                        st.rerun()
                with col_dbtn2:
                    if st.button("🗑️ Eliminar Definitivamente", type="primary", use_container_width=True):
                        ok = delete_package(supabase, del_target.get("id"))
                        if ok:
                            st.success("Paquete eliminado del sistema.")
                            st.rerun()
                        else:
                            st.error("No se pudo eliminar el paquete.")

    # ==============================================================================
    # 2. CRUD DE ESTUDIANTES Y GESTIÓN DE CRÉDITOS
    # ==============================================================================
    elif "Estudiantes" in mod:
        st.subheader("🎓 Gestión, Modificación y CRUD de Estudiantes")
        st.caption("Administra la información de los alumnos, ajusta créditos de clases y asigna elos competitivos:")

        detailed_students = get_students_detailed(supabase)

        if detailed_students:
            st_rows = []
            for s in detailed_students:
                sp_list = s.get("student_packages") or []
                active_sp = next((p for p in sp_list if p.get("status") == "active"), sp_list[0] if sp_list else {})
                pkg_info = active_sp.get("packages") or {}

                st_rows.append({
                    "Alumno": s.get("full_name") or s.get("email"),
                    "Email": s.get("email"),
                    "Riot ID": s.get("riot_id") or "Sin Riot ID",
                    "Discord": s.get("discord_tag") or "perez1473",
                    "Rango / Elo": f"{s.get('current_tier', 'EMERALD')} {s.get('current_rank', 'II')} ({s.get('current_lp', 0)} LP)",
                    "Línea": s.get("main_lane", "JUNGLE"),
                    "Paquete Activo": pkg_info.get("title", "Sin Paquete"),
                    "VODs Restantes": active_sp.get("vod_classes_remaining", 0),
                    "LIVEs Restantes": active_sp.get("live_classes_remaining", 0)
                })
            st.dataframe(st_rows, use_container_width=True)
        else:
            st.info("No hay estudiantes matriculados en la plataforma.")

        st.write("")
        tab_st1, tab_st2, tab_st3 = st.tabs(["✏️ Editar Alumno y Ajustar Créditos", "➕ Matricular Nuevo Alumno", "🗑️ Dar de Baja"])

        # TAB 1: EDITAR ALUMNO Y AJUSTAR CRÉDITOS
        with tab_st1:
            st.markdown("#### ✏️ Modificar Perfil Competitivo y Ajuste de Clases")
            if detailed_students:
                st_map = {f"{s.get('full_name') or s.get('email')} ({s.get('riot_id') or s.get('email')})": s for s in detailed_students}
                sel_st_label = st.selectbox("Selecciona al Estudiante a Modificar", list(st_map.keys()), key="sel_st_mod")
                target_st = st_map[sel_st_label]
                target_st_id = target_st.get("id")

                # Obtener créditos actuales
                curr_sp = get_student_package(supabase, target_st_id)
                curr_vod_rem = curr_sp.get("vod_classes_remaining", 0) if curr_sp else 0
                curr_live_rem = curr_sp.get("live_classes_remaining", 0) if curr_sp else 0
                curr_vod_tot = curr_sp.get("vod_classes_total", 0) if curr_sp else 0
                curr_live_tot = curr_sp.get("live_classes_total", 0) if curr_sp else 0

                with st.container(border=True):
                    st.markdown("##### 👤 Datos de Identidad y Competitivos")
                    col_ed1, col_ed2 = st.columns(2)
                    with col_ed1:
                        st_fn = st.text_input("Nombre Completo", value=target_st.get("full_name", ""), key="st_fn")
                        st_riot = st.text_input("Riot ID (Nombre#TAG)", value=target_st.get("riot_id", "") or "", key="st_riot")
                        st_disc = st.text_input("Discord Tag", value=target_st.get("discord_tag", "") or "perez1473", key="st_disc")
                    with col_ed2:
                        ranks_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
                        c_tier = target_st.get("current_tier", "EMERALD")
                        t_idx = ranks_list.index(c_tier) if c_tier in ranks_list else 5
                        st_tier = st.selectbox("Rango (Tier)", ranks_list, index=t_idx, key="st_tier")
                        
                        divs = ["I", "II", "III", "IV"]
                        c_div = target_st.get("current_rank", "II")
                        d_idx = divs.index(c_div) if c_div in divs else 1
                        st_rank = st.selectbox("División", divs, index=d_idx, key="st_rank")
                        st_lp = st.number_input("LP Actuales", min_value=0, max_value=2500, value=int(target_st.get("current_lp", 35)), key="st_lp")
                        
                        lanes = ["JUNGLE", "TOP", "MID", "ADC", "SUPPORT"]
                        c_lane = target_st.get("main_lane", "JUNGLE")
                        l_idx = lanes.index(c_lane) if c_lane in lanes else 0
                        st_lane = st.selectbox("Línea Principal", lanes, index=l_idx, key="st_lane")

                    st.markdown("##### 🎒 Ajuste Manual de Créditos / Clases (Compensaciones o Bonos)")
                    col_cr1, col_cr2 = st.columns(2)
                    with col_cr1:
                        new_vod_rem = st.number_input("VODs Reviews Restantes", min_value=0, value=int(curr_vod_rem), step=1, key="n_vod_rem")
                        new_vod_tot = st.number_input("VODs Totales (Paquete)", min_value=0, value=max(int(curr_vod_tot), int(new_vod_rem)), step=1, key="n_vod_tot")
                    with col_cr2:
                        new_live_rem = st.number_input("LIVE Games Restantes", min_value=0, value=int(curr_live_rem), step=1, key="n_live_rem")
                        new_live_tot = st.number_input("LIVEs Totales (Paquete)", min_value=0, value=max(int(curr_live_tot), int(new_live_rem)), step=1, key="n_live_tot")

                    if st.button("💾 Guardar Cambios de Perfil y Créditos", type="primary", use_container_width=True):
                        # 1. Actualizar perfil
                        ok_p = update_student_profile(
                            supabase=supabase,
                            user_id=target_st_id,
                            full_name=st_fn,
                            riot_id=st_riot,
                            discord_tag=st_disc,
                            current_tier=st_tier,
                            current_rank=st_rank,
                            current_lp=int(st_lp),
                            main_lane=st_lane
                        )
                        # 2. Actualizar créditos
                        ok_c = adjust_student_credits(
                            supabase=supabase,
                            student_id=target_st_id,
                            vod_remaining=int(new_vod_rem),
                            live_remaining=int(new_live_rem),
                            vod_total=int(new_vod_tot),
                            live_total=int(new_live_tot)
                        )
                        if ok_p and ok_c:
                            st.success(f"¡Datos y créditos del alumno '{st_fn}' actualizados correctamente!")
                            st.rerun()
                        else:
                            st.error("Error al actualizar información en la base de datos.")
            else:
                st.info("Sin estudiantes para modificar.")

        # TAB 2: MATRICULAR ALUMNO
        with tab_st2:
            st.markdown("#### ➕ Matricular Nuevo Alumno Directamente")
            with st.container(border=True):
                col_ma1, col_ma2 = st.columns(2)
                with col_ma1:
                    new_s_name = st.text_input("Nombre Completo *", placeholder="ej: Lucas Silva", key="new_s_name")
                    new_s_email = st.text_input("Correo Electrónico *", placeholder="alumno@gmail.com", key="new_s_email")
                    new_s_pass = st.text_input("Contraseña Temporal", value="PerezAlumno2026!", type="password", key="new_s_pass")
                with col_ma2:
                    new_s_riot = st.text_input("Riot ID", placeholder="Invocador#LAN", key="new_s_riot")
                    new_s_disc = st.text_input("Discord Tag", placeholder="ej: usuario_disc", key="new_s_disc")
                    new_s_lane = st.selectbox("Línea", ["JUNGLE", "TOP", "MID", "ADC", "SUPPORT"], key="new_s_lane")

                if st.button("🚀 Matricular y Dar de Alta en la Academia", type="primary", use_container_width=True):
                    if not new_s_email or not new_s_name:
                        st.warning("Completa los campos obligatorios.")
                    else:
                        u_uid = str(uuid.uuid4())
                        ok = upsert_profile(
                            supabase=supabase,
                            user_id=u_uid,
                            email=new_s_email.strip().lower(),
                            role="student",
                            riot_id=new_s_riot,
                            discord_tag=new_s_disc or "perez1473",
                            full_name=new_s_name
                        )
                        if ok:
                            # Asignar paquete por defecto si existe
                            pkgs = get_packages(supabase)
                            if pkgs:
                                adjust_student_credits(supabase, u_uid, vod_remaining=3, live_remaining=1, vod_total=3, live_total=1)
                            st.success(f"¡Estudiante {new_s_name} matriculado con éxito!")
                            st.rerun()
                        else:
                            st.error("Error al matricular estudiante.")

        # TAB 3: DAR DE BAJA
        with tab_st3:
            st.markdown("#### 🗑️ Dar de Baja a un Estudiante")
            if detailed_students:
                del_st_map = {f"{s.get('full_name') or s.get('email')} ({s.get('email')})": s for s in detailed_students}
                sel_del_st = st.selectbox("Selecciona el alumno a dar de baja", list(del_st_map.keys()), key="sel_del_st")
                st_del_obj = del_st_map[sel_del_st]

                st.warning(f"⚠️ ¿Estás seguro de que deseas eliminar la cuenta de **{st_del_obj.get('full_name')}** ({st_del_obj.get('email')})?")
                if st.button("❌ Confirmar Eliminación del Estudiante", type="primary"):
                    ok = delete_user(supabase, st_del_obj.get("id"))
                    if ok:
                        st.success("Estudiante dado de baja del sistema.")
                        st.rerun()
                    else:
                        st.error("Error al eliminar al estudiante.")

    # ==============================================================================
    # 3. CONTROL DE COACHING Y AGENDA (SESIONES)
    # ==============================================================================
    elif "Coaching" in mod or "Agenda" in mod:
        st.subheader("🎮 Control de Coaching, Clases y Agenda Global")
        st.caption("Visualiza, agenda, reagenda y supervisa las clases de todos los coaches y alumnos:")

        if sessions:
            ses_rows = []
            for s in sessions:
                st_p = s.get("student") or {}
                co_p = s.get("coach") or {}
                ses_rows.append({
                    "Fecha y Hora": s.get("scheduled_at", "")[:16].replace("T", " "),
                    "Alumno": f"{st_p.get('full_name') or 'Alumno'} ({st_p.get('riot_id') or st_p.get('email')})",
                    "Coach": co_p.get("full_name") or co_p.get("email") or "Head Coach Perez",
                    "Tipo": s.get("service_type", "vod").upper(),
                    "Línea": s.get("role_lane", "JUNGLE"),
                    "Duración": f"{s.get('duration_minutes', 45)} min",
                    "Estado": s.get("status", "scheduled").capitalize()
                })
            st.dataframe(ses_rows, use_container_width=True)
        else:
            st.info("No hay sesiones agendadas en el sistema actualmente.")

        st.write("")
        tab_sc1, tab_sc2, tab_sc3 = st.tabs(["📅 Agendar Clase", "✏️ Reagendar / Editar Sesión", "🗑️ Cancelar o Eliminar"])

        # TAB 1: AGENDAR SESIÓN DESDE ADMIN
        with tab_sc1:
            st.markdown("#### 📅 Programar Clase para un Alumno")
            if students:
                st_opts = {f"{s.get('full_name') or s.get('email')} ({s.get('riot_id') or s.get('email')})": s.get("id") for s in students}
                coach_opts = {f"{c.get('full_name') or c.get('email')} ({c.get('email')})": c.get("id") for c in coaches}
                if not coach_opts:
                    coach_opts["Head Coach Perez"] = user.get("id")

                with st.container(border=True):
                    col_as1, col_as2 = st.columns(2)
                    with col_as1:
                        target_st_name = st.selectbox("Selecciona al Alumno *", list(st_opts.keys()), key="adm_sched_st")
                        target_st_id = st_opts[target_st_name]
                        target_co_name = st.selectbox("Asignar Coach *", list(coach_opts.keys()), key="adm_sched_co")
                        target_co_id = coach_opts[target_co_name]
                        s_type = st.radio("Tipo de Sesión", ["LIVE GAME Coaching (Discord)", "VOD Review (Repetición)", "Team Coaching 5v5"], key="adm_s_type")
                        s_type_code = "live" if "LIVE" in s_type else ("team" if "Team" in s_type else "vod")
                    with col_as2:
                        s_date = st.date_input("Fecha de la Clase", min_value=date.today(), key="adm_s_date")
                        s_time = st.selectbox("Hora Acordada", ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"], key="adm_s_time")
                        s_lane = st.selectbox("Carril a Entrenar", ["JUNGLE", "TOP", "MID", "ADC", "SUPPORT"], key="adm_s_lane")
                        s_dur = st.selectbox("Duración de la Sesión", [45, 60, 90, 120], key="adm_s_dur")

                    if st.button("🚀 Programar Clase en la Agenda", type="primary", use_container_width=True):
                        iso_sched = f"{s_date.isoformat()}T{s_time}:00Z"
                        ok = admin_create_session(
                            supabase=supabase,
                            student_id=target_st_id,
                            coach_id=target_co_id,
                            service_type=s_type_code,
                            role_lane=s_lane,
                            scheduled_at=iso_sched,
                            duration_minutes=int(s_dur),
                            discord_tag="perez1473"
                        )
                        if ok:
                            st.success("¡Clase programada exitosamente en la agenda del alumno y del coach!")
                            st.rerun()
                        else:
                            st.error("Error al programar la sesión.")
            else:
                st.info("Matricula alumnos primero para poder agendar clases.")

        # TAB 2: REAGENDAR O EDITAR SESIÓN
        with tab_sc2:
            st.markdown("#### ✏️ Reagendar o Cambiar Estado de Sesión")
            if sessions:
                ses_map = {}
                for s in sessions:
                    st_p = s.get("student") or {}
                    lbl = f"{s.get('scheduled_at', '')[:16]} — {st_p.get('full_name') or 'Alumno'} ({s.get('service_type', '').upper()})"
                    ses_map[lbl] = s

                sel_ses_label = st.selectbox("Selecciona la sesión a modificar", list(ses_map.keys()), key="sel_ses_mod")
                curr_s = ses_map[sel_ses_label]

                with st.container(border=True):
                    col_ms1, col_ms2 = st.columns(2)
                    with col_ms1:
                        m_date = st.date_input("Nueva Fecha", value=datetime.fromisoformat(curr_s.get("scheduled_at", "2026-10-18T15:00:00")[:10]), key="m_date")
                        m_time = st.selectbox("Nueva Hora", ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"], key="m_time")
                        m_type = st.selectbox("Tipo de Sesión", ["vod", "live", "team", "custom"], index=["vod", "live", "team", "custom"].index(curr_s.get("service_type") if curr_s.get("service_type") in ["vod", "live", "team", "custom"] else "vod"), key="m_type")
                    with col_ms2:
                        status_list = ["scheduled", "completed", "cancelled"]
                        c_stat = curr_s.get("status", "scheduled")
                        s_idx = status_list.index(c_stat) if c_stat in status_list else 0
                        m_status = st.selectbox("Estado de la Sesión", status_list, index=s_idx, key="m_status")
                        m_lane = st.selectbox("Línea", ["JUNGLE", "TOP", "MID", "ADC", "SUPPORT"], index=["JUNGLE", "TOP", "MID", "ADC", "SUPPORT"].index(curr_s.get("role_lane", "JUNGLE")), key="m_lane")
                        m_dur = st.number_input("Duración (min)", min_value=15, max_value=240, value=int(curr_s.get("duration_minutes", 45)), step=15, key="m_dur")

                    if st.button("💾 Guardar Cambios de la Sesión", type="primary", use_container_width=True):
                        new_iso = f"{m_date.isoformat()}T{m_time}:00Z"
                        ok = admin_update_session(
                            supabase=supabase,
                            session_id=curr_s.get("id"),
                            service_type=m_type,
                            role_lane=m_lane,
                            scheduled_at=new_iso,
                            duration_minutes=int(m_dur),
                            status=m_status
                        )
                        if ok:
                            st.success("¡Sesión actualizada correctamente!")
                            st.rerun()
                        else:
                            st.error("Error al actualizar la sesión.")
            else:
                st.info("Sin sesiones disponibles para modificar.")

        # TAB 3: ELIMINAR SESIÓN
        with tab_sc3:
            st.markdown("#### 🗑️ Cancelar o Eliminar Sesión")
            if sessions:
                del_ses_map = {f"{s.get('scheduled_at', '')[:16]} — Alumno ID {s.get('student_id')[:8]}": s for s in sessions}
                sel_del_ses = st.selectbox("Selecciona la sesión", list(del_ses_map.keys()), key="sel_del_ses")
                ses_del_target = del_ses_map[sel_del_ses]

                if st.button("🗑️ Eliminar Sesión de la Agenda", type="primary"):
                    ok = admin_delete_session(supabase, ses_del_target.get("id"))
                    if ok:
                        st.success("Sesión eliminada de la agenda.")
                        st.rerun()
                    else:
                        st.error("Error al eliminar la sesión.")

    # ==============================================================================
    # 4. CRUD Y AUDITORÍA DE PAGOS P2P
    # ==============================================================================
    elif "Pagos" in mod:
        st.subheader("💰 Auditoría, Validación y CRUD de Pagos P2P")
        st.caption("Supervisa transferencias por Binance y Nequi, valida comprobantes visuales o registra pagos manuales:")

        pending_payments = [p for p in payments if p.get("status") == "pending"]
        approved_payments = [p for p in payments if p.get("status") == "approved"]
        total_rev = sum([float(p.get("amount", 0.0)) for p in approved_payments])

        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            st.metric("Total Recaudado (Aprobado)", f"${total_rev:.2f} USD")
        with c_p2:
            st.metric("Pagos Pendientes de Revisión", len(pending_payments))
        with c_p3:
            st.metric("Total Pagos Registrados", len(payments))

        # Tabla de Pagos
        if payments:
            pay_rows = [{
                "Fecha": p.get("created_at")[:16].replace("T", " "),
                "Alumno": f"{p.get('profiles', {}).get('full_name') or 'Alumno'} ({p.get('profiles', {}).get('email')})" if p.get("profiles") else "N/A",
                "Paquete": p.get("packages", {}).get("title") if p.get("packages") else "Personalizado",
                "Monto ($ USD)": f"${p.get('amount'):.2f}",
                "Método": p.get("payment_method"),
                "Comprobante": "🖼️ Captura adjunta" if p.get("receipt_url") else "Sin imagen",
                "Estado": "🟡 Pendiente" if p.get("status") == "pending" else ("🟢 Aprobado" if p.get("status") == "approved" else "🔴 Rechazado")
            } for p in payments]
            st.dataframe(pay_rows, use_container_width=True)
        else:
            st.info("No hay pagos registrados aún.")

        st.write("")
        tab_py1, tab_py2, tab_py3 = st.tabs(["🟡 Validar Comprobantes Pendientes", "➕ Registrar Pago Manual Directo", "✏️ Modificar o Eliminar Pago"])

        # TAB 1: VALIDAR COMPROBANTES PENDIENTES
        with tab_py1:
            st.markdown("#### 🟡 Comprobantes Pendientes de Aprobación")
            if pending_payments:
                for pp in pending_payments:
                    p_id = pp.get("id")
                    st_info = pp.get("profiles") or {}
                    pkg_info = pp.get("packages") or {}

                    with st.container(border=True):
                        col_pv1, col_pv2 = st.columns([1, 2])
                        with col_pv1:
                            if pp.get("receipt_url"):
                                st.image(pp.get("receipt_url"), caption="Comprobante de Transferencia", width=260)
                            else:
                                st.warning("Sin imagen de comprobante adjunta.")
                        with col_pv2:
                            st.markdown(f"### **{pkg_info.get('title', 'Paquete de Clases')}**")
                            st.markdown(f"👤 **Alumno:** `{st_info.get('full_name') or st_info.get('email')}` | 🎮 **Riot:** `{st_info.get('riot_id') or 'N/A'}`")
                            st.markdown(f"💵 **Monto:** :green[**${pp.get('amount')} USD**] | 💳 **Medio:** `{pp.get('payment_method')}`")
                            st.caption(f"Fecha de envío: {pp.get('created_at', '')[:16].replace('T', ' ')} hrs")

                            c_b1, c_b2 = st.columns(2)
                            with c_b1:
                                if st.button(f"✅ Aprobar y Acreditar Clases", key=f"adm_app_{p_id}", type="primary", use_container_width=True):
                                    ok = admin_update_payment(supabase, p_id, status="approved")
                                    if ok:
                                        st.success("¡Pago aprobado y clases acreditadas al alumno!")
                                        st.rerun()
                                    else:
                                        st.error("Error al aprobar pago.")
                            with c_b2:
                                if st.button(f"❌ Rechazar Pago", key=f"adm_rej_{p_id}", use_container_width=True):
                                    admin_update_payment(supabase, p_id, status="rejected", notes="Comprobante inválido o no recibido")
                                    st.warning("Pago rechazado.")
                                    st.rerun()
            else:
                st.success("🎉 ¡No hay pagos pendientes de revisión! Todo al día.")

        # TAB 2: REGISTRAR PAGO MANUAL DIRECTO
        with tab_py2:
            st.markdown("#### ➕ Registrar Pago Manual / Efectivo / Cripto")
            st.caption("Permite al administrador ingresar pagos recibidos por canales alternativos y acreditar las clases de inmediato:")
            if students and packages:
                st_pay_map = {f"{s.get('full_name') or s.get('email')} ({s.get('email')})": s.get("id") for s in students}
                pkg_pay_map = {f"{p.get('title')} — ${p.get('price')} USD": p for p in packages}

                with st.container(border=True):
                    col_mp1, col_mp2 = st.columns(2)
                    with col_mp1:
                        sel_st_p = st.selectbox("Selecciona al Alumno *", list(st_pay_map.keys()), key="man_p_st")
                        pay_st_id = st_pay_map[sel_st_p]
                        sel_pkg_p = st.selectbox("Paquete Adquirido *", list(pkg_pay_map.keys()), key="man_p_pkg")
                        pay_pkg_obj = pkg_pay_map[sel_pkg_p]
                    with col_mp2:
                        pay_amt = st.number_input("Monto Registrado ($ USD)", min_value=0.0, value=float(pay_pkg_obj.get("price", 12.0)), step=0.5, key="man_p_amt")
                        pay_meth = st.selectbox("Medio de Pago", ["Binance Pay (USDT)", "Nequi", "Transferencia Bancaria", "Efectivo", "Otro"], key="man_p_meth")
                        auto_cred = st.checkbox("Acreditar clases al alumno automáticamente ahora mismo", value=True, key="man_p_cred")

                    if st.button("💳 Registrar y Procesar Pago", type="primary", use_container_width=True):
                        ok = admin_create_payment(
                            supabase=supabase,
                            student_id=pay_st_id,
                            package_id=pay_pkg_obj.get("id"),
                            amount=float(pay_amt),
                            payment_method=pay_meth,
                            status="approved",
                            auto_credit=auto_cred
                        )
                        if ok:
                            st.success("¡Pago registrado y clases acreditadas al estudiante exitosamente!")
                            st.rerun()
                        else:
                            st.error("Error al registrar el pago.")
            else:
                st.info("Se requieren alumnos y paquetes registrados para crear un pago.")

        # TAB 3: MODIFICAR O ELIMINAR PAGO
        with tab_py3:
            st.markdown("#### ✏️ Modificar o Eliminar Registro de Pago")
            if payments:
                pay_edit_map = {}
                for p in payments:
                    st_p = p.get("profiles") or {}
                    lbl = f"{p.get('created_at', '')[:10]} — ${p.get('amount')} USD — {st_p.get('email', 'Alumno')} ({p.get('status')})"
                    pay_edit_map[lbl] = p

                sel_pay_edit = st.selectbox("Selecciona el pago a corregir", list(pay_edit_map.keys()), key="sel_pay_cor")
                curr_pay = pay_edit_map[sel_pay_edit]

                with st.container(border=True):
                    col_ep1, col_ep2 = st.columns(2)
                    with col_ep1:
                        new_p_amt = st.number_input("Monto ($ USD)", min_value=0.0, value=float(curr_pay.get("amount", 0.0)), step=0.5, key="cor_p_amt")
                        new_p_meth = st.selectbox("Método", ["Binance Pay (USDT)", "Nequi", "Transferencia Bancaria", "Efectivo", "Otro"], index=0, key="cor_p_meth")
                    with col_ep2:
                        p_stats = ["pending", "approved", "rejected"]
                        c_ps = curr_pay.get("status", "pending")
                        ps_idx = p_stats.index(c_ps) if c_ps in p_stats else 0
                        new_p_stat = st.selectbox("Estado del Pago", p_stats, index=ps_idx, key="cor_p_stat")
                        new_p_notes = st.text_input("Notas de Auditoría", value=curr_pay.get("notes") or "", key="cor_p_notes")

                    col_bp1, col_bp2 = st.columns(2)
                    with col_bp1:
                        if st.button("💾 Guardar Modificación de Pago", type="primary", use_container_width=True):
                            ok = admin_update_payment(supabase, curr_pay.get("id"), status=new_p_stat, amount=float(new_p_amt), payment_method=new_p_meth, notes=new_p_notes)
                            if ok:
                                st.success("Pago actualizado con éxito.")
                                st.rerun()
                            else:
                                st.error("Error al actualizar pago.")
                    with col_bp2:
                        if st.button("🗑️ Eliminar Pago de la Base de Datos", use_container_width=True):
                            ok = admin_delete_payment(supabase, curr_pay.get("id"))
                            if ok:
                                st.success("Registro de pago eliminado.")
                                st.rerun()
                            else:
                                st.error("Error al eliminar el pago.")

    # ==============================================================================
    # 5. GESTIÓN DE COACHES Y ROLES DE USUARIO
    # ==============================================================================
    elif "Coaches" in mod or "Roles" in mod:
        st.subheader("🛡️ Gestión de Coaches, Staff y Roles de la Academia")
        st.caption("Asigna o actualiza los roles de acceso a la plataforma:")

        # Lista de Coaches
        st.markdown("#### 🎮 Coaches Activos en la Academia")
        if coaches:
            coach_data = [{
                "Nombre": c.get("full_name") or "Coach",
                "Email": c.get("email"),
                "Discord": c.get("discord_tag") or "perez1473",
                "Riot ID": c.get("riot_id") or "N/A",
                "Especialidad": c.get("main_lane", "JUNGLE"),
                "Rol": c.get("role")
            } for c in coaches]
            st.dataframe(coach_data, use_container_width=True)
        else:
            st.info("No hay coaches registrados aparte del Administrador.")

        st.divider()
        st.markdown("#### 🔄 Cambiar Rol de un Usuario Registrado")
        if all_users:
            u_options = {f"{u.get('email')} (Rol: {u.get('role').upper()})": u for u in all_users}
            sel_u_label = st.selectbox("Selecciona un usuario para cambiar su rol", list(u_options.keys()), key="sel_u_role")
            target_u = u_options[sel_u_label]

            col_ro1, col_ro2 = st.columns([2, 1])
            with col_ro1:
                new_role_val = st.selectbox("Nuevo Rol para este Usuario", ["student", "coach", "admin"], index=["student", "coach", "admin"].index(target_u.get("role", "student")), key="new_role_val")
            with col_ro2:
                st.write("")
                st.write("")
                if st.button("Actualizar Rol", type="primary", use_container_width=True):
                    ok = update_user_role(supabase, target_u.get("id"), new_role_val)
                    if ok:
                        st.success(f"Rol de {target_u.get('email')} actualizado a '{new_role_val}'.")
                        st.rerun()
                    else:
                        st.error("Error al actualizar rol.")
