import streamlit as st
from datetime import datetime, date
from database.operations import (
    get_pending_payments, approve_payment, reject_payment,
    get_coach_sessions, complete_session, assign_task,
    save_session_notes, get_all_users, enroll_new_student,
    book_session, get_student_package
)

def render_coach_view(supabase, user, active_module=None):
    coach_id = user.get("id")
    coach_email = user.get("email", "Coach")
    mod = active_module or "👥 Gestión de Estudiantes"
    
    st.title("🛡️ Panel de Control del Coach - PerezLoL (Only JG)")
    st.caption(f"Sesión activa: **Coach Perez** | Discord: `perez1473`")

    # Datos en tiempo real desde Supabase
    pending_payments = get_pending_payments(supabase) if supabase else []
    coach_sessions = get_coach_sessions(supabase) if supabase else []
    all_users = get_all_users(supabase) if supabase else []
    students = [u for u in all_users if u.get("role") == "student"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Alumnos JG Asignados", len(students))
    with col2:
        st.metric("Comprobantes por Validar", len(pending_payments), delta="Pendientes", delta_color="inverse")
    with col3:
        st.metric("Clases Programadas", len(coach_sessions))
    with col4:
        st.metric("Duración por Sesión", "30 - 60 min")

    st.divider()

    # ==============================================================================
    # MÓDULO 1: GESTIÓN DE ESTUDIANTES
    # ==============================================================================
    if "Gestión de Estudiantes" in mod:
        st.subheader("👥 Ficha y Control de Alumnos")
        st.caption("Supervisa el avance, rango y créditos restantes de tus alumnos:")

        if students:
            for s in students:
                s_id = s.get("id")
                s_name = s.get("full_name") or "Alumno"
                s_riot = s.get("riot_id") or "Sin Riot ID"
                s_disc = s.get("discord_tag") or "perez1473"
                s_email = s.get("email")
                s_tier = s.get("current_tier", "EMERALD")
                s_rank = s.get("current_rank", "II")
                
                # Paquete activo
                st_pkg = get_student_package(supabase, s_id) if supabase else None
                v_rem = st_pkg.get("vod_classes_remaining", 0) if st_pkg else 0
                l_rem = st_pkg.get("live_classes_remaining", 0) if st_pkg else 0
                pkg_t = st_pkg.get("packages", {}).get("title", "Sin paquete activo") if st_pkg else "Sin paquete activo"

                with st.container(border=True):
                    col_st1, col_st2, col_st3 = st.columns([2, 2, 1])
                    with col_st1:
                        st.markdown(f"#### **{s_name}** (`{s_riot}`)")
                        st.write(f"📧 **Email:** `{s_email}` | 🎙️ **Discord:** `{s_disc}`")
                        st.write(f"🏆 **Rango:** `{s_tier} {s_rank}`")
                    with col_st2:
                        st.markdown(f"📦 **Plan:** {pkg_t}")
                        st.write(f"• **VODs Restantes:** :green[**{v_rem} clases**]")
                        st.write(f"• **LIVEs Restantes:** :blue[**{l_rem} clases**]")
                    with col_st3:
                        st.write("")
                        st.caption("Alumno Activo")
        else:
            st.info("No hay estudiantes matriculados aún en la plataforma.")

    # ==============================================================================
    # MÓDULO 2: PROGRAMAR CLASES (SOLO ALUMNO, TIPO, FECHA Y HORA - SIN LINK)
    # ==============================================================================
    elif "Programar Clases" in mod:
        st.subheader("📅 Programar Clase para un Alumno")
        st.caption("Agenda una fecha de sesión para tu alumno. El alumno la verá automáticamente en su panel central:")

        if students:
            student_dict = {f"{s.get('full_name') or 'Alumno'} ({s.get('riot_id') or s.get('email')})": s for s in students}
            sel_st_label = st.selectbox("Selecciona al Alumno", list(student_dict.keys()), key="sched_st_select")
            target_student = student_dict[sel_st_label]
            target_st_id = target_student.get("id")

            with st.container(border=True):
                col_sc1, col_sc2 = st.columns(2)
                with col_sc1:
                    sched_type = st.radio("Tipo de Sesión", ["LIVE GAME Coaching (Discord)", "VOD Review (Repetición)"], key="sched_type_rad")
                    sched_service = "live" if "LIVE" in sched_type else "vod"
                    sched_date = st.date_input("Fecha de la Sesión", min_value=date.today(), key="sched_date_input")
                with col_sc2:
                    sched_time = st.selectbox("Hora Acordada", ["14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"], key="sched_time_sel")

                if st.button("Agendar Clase para el Alumno", type="primary", use_container_width=True):
                    sched_iso = f"{sched_date.isoformat()}T{sched_time}:00Z"
                    if supabase:
                        ok = book_session(
                            supabase=supabase,
                            student_id=target_st_id,
                            service_type=sched_service,
                            scheduled_at=sched_iso,
                            coach_id=coach_id,
                            duration_minutes=45,
                            vod_url="",
                            discord_tag="perez1473"
                        )
                        if ok:
                            st.success(f"¡Clase programada para {target_student.get('full_name')}! Aparecerá de inmediato en su panel de estudio.")
                            st.rerun()
                        else:
                            st.error("Error al programar la sesión.")
                    else:
                        st.success("Clase agendada (Modo Demo).")

            st.divider()
            st.subheader("Sesiones Registradas en Agenda")
            if coach_sessions:
                for cs in coach_sessions:
                    cs_id = cs.get("id")
                    st_p = cs.get("profiles") or {}
                    cs_type = cs.get("service_type", "vod").upper()
                    cs_time = cs.get("scheduled_at", "")[:16].replace("T", " ")
                    cs_status = cs.get("status")
                    
                    with st.container(border=True):
                        c_cs1, c_cs2 = st.columns([3, 1])
                        with c_cs1:
                            st.markdown(f"**{cs_type} - {cs_time}** | Alumno: `{st_p.get('riot_id', 'Alumno')}` ({st_p.get('email', '')})")
                            st.write(f"Estado: `{cs_status.capitalize()}` | Duración: {cs.get('duration_minutes', 45)} min")
                        with c_cs2:
                            if cs_status != "completed":
                                if st.button("Marcar Completada", key=f"btn_comp_{cs_id}", use_container_width=True):
                                    ok = complete_session(supabase, cs_id, coach_id)
                                    if ok:
                                        st.success("Sesión completada y crédito descontado.")
                                        st.rerun()
                            else:
                                st.write("✅ Finalizada")
            else:
                st.caption("No hay sesiones agendadas aún.")
        else:
            st.info("Primero matricula a un estudiante para poder programarle clases.")

    # ==============================================================================
    # MÓDULO 3: APROBAR PAGOS P2P (CHULEAR COMPROBANTES)
    # ==============================================================================
    elif "Aprobar Pagos" in mod or "Validar Pagos" in mod:
        st.subheader("💰 Comprobantes de Pago por Validar")
        st.caption("El alumno transfiere por Binance o Nequi y adjunta su comprobante. Revisa la imagen y chulea el pago:")

        if pending_payments:
            for pay in pending_payments:
                p_id = pay.get("id")
                student_prof = pay.get("profiles") or {}
                pkg_data = pay.get("packages") or {}
                st_name = student_prof.get("full_name") or student_prof.get("email") or "Alumno"
                st_riot = student_prof.get("riot_id") or "Sin Riot ID"
                pkg_title = pkg_data.get("title") or "Paquete Coaching"
                amt = pay.get("amount")
                method = pay.get("payment_method")
                dt = pay.get("created_at")[:16].replace("T", " ")
                receipt_img = pay.get("receipt_url")

                with st.container(border=True):
                    c_info, c_action = st.columns([3, 1])
                    with c_info:
                        st.markdown(f"""
                        * **Alumno:** `{st_riot}` ({st_name})
                        * **Paquete a Acreditar:** **{pkg_title}**
                        * **Monto:** **${amt} USD** | **Medio de Pago:** **{method}**
                        * **Fecha de solicitud:** {dt}
                        """)
                        if receipt_img:
                            with st.expander("🖼️ Ver Captura del Comprobante Subido", expanded=True):
                                st.image(receipt_img, caption=f"Comprobante {method} - {st_name}", width=340)
                        else:
                            st.caption("⚠️ Sin imagen adjunta.")
                    with c_action:
                        st.write("")
                        if st.button("✅ Chulear / Aprobar", key=f"app_{p_id}", type="primary", use_container_width=True):
                            ok = approve_payment(supabase, p_id, coach_id)
                            if ok:
                                st.success("¡Pago aprobado y clases acreditadas al alumno!")
                                st.rerun()
                            else:
                                st.error("Error al aprobar pago.")
                        if st.button("❌ Rechazar", key=f"rej_{p_id}", use_container_width=True):
                            ok = reject_payment(supabase, p_id, coach_id, "Comprobante no válido")
                            if ok:
                                st.warning("Pago rechazado.")
                                st.rerun()
        else:
            st.info("No hay pagos pendientes de validación en este momento.")

    # ==============================================================================
    # MÓDULO 4: ASIGNAR TAREAS Y NOTAS TÉCNICAS
    # ==============================================================================
    elif "Tareas y Notas" in mod:
        st.subheader("📝 Tareas y Retroalimentación Técnica")
        st.caption("Asigna misiones prácticas de Jungla a tus estudiantes:")

        if students:
            st_opts = {f"{s.get('full_name') or 'Alumno'} ({s.get('riot_id') or s.get('email')})": s.get("id") for s in students}
            sel_student_label = st.selectbox("Seleccionar Alumno", list(st_opts.keys()), key="task_student_sel")
            chosen_s_id = st_opts[sel_student_label]

            with st.container(border=True):
                st.markdown("##### Nueva Misión de Jungla")
                c_t1, c_t2 = st.columns([3, 1])
                with c_t1:
                    t_title = st.text_input("Título de la Misión", placeholder="Ej: Full clear hacia bot antes del 3:25 con Nocturne.")
                    t_desc = st.text_area("Pautas Detalladas", placeholder="Hacer kiting sin recibir daño de los campamentos medianos.")
                with c_t2:
                    t_cat = st.selectbox("Categoría", ["pathing", "vision_control", "objective_setup", "invade_macro", "champion_pool", "mental"])
                    t_due = st.date_input("Fecha límite", min_value=date.today(), key="task_due_key")

                if st.button("Asignar Tarea al Alumno", type="primary", use_container_width=True):
                    if not t_title:
                        st.warning("Escribe el título de la tarea.")
                    elif supabase:
                        ok = assign_task(
                            supabase=supabase,
                            student_id=chosen_s_id,
                            coach_id=coach_id,
                            title=t_title,
                            description=t_desc,
                            category=t_cat,
                            due_date=t_due.isoformat()
                        )
                        if ok:
                            st.success("¡Tarea asignada con éxito al estudiante!")
                            st.rerun()
                        else:
                            st.error("Error al asignar tarea.")
                    else:
                        st.success("Tarea asignada (Modo Demo).")
        else:
            st.info("Matricula a un estudiante primero.")

    # ==============================================================================
    # MÓDULO 5: MATRICULAR NUEVO ALUMNO
    # ==============================================================================
    elif "Matricular" in mod:
        st.subheader("➕ Matricular Nuevo Alumno a la Academia")
        st.caption("Crea la cuenta del estudiante para que pueda ingresar con sus credenciales:")

        with st.container(border=True):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                en_name = st.text_input("Nombre Completo del Alumno", placeholder="Ej: Carlos Gómez", key="en_name_c")
                en_email = st.text_input("Correo Electrónico", placeholder="alumno@gmail.com", key="en_email_c")
                en_pass = st.text_input("Contraseña Provisional", value="PerezAlumno2026!", type="password", key="en_pass_c")
            with col_e2:
                en_riot = st.text_input("Riot ID del Alumno (ej: Invocador#LAN)", placeholder="Faker#KR1", key="en_riot_c")
                en_disc = st.text_input("Discord del Alumno", placeholder="usuario_discord", key="en_disc_c")

            if st.button("Crear y Matricular Estudiante", type="primary", use_container_width=True):
                if not en_email or not en_pass or not en_name:
                    st.warning("Completa el nombre, correo y contraseña.")
                else:
                    new_uid = enroll_new_student(supabase, en_email, en_pass, en_name, en_riot, en_disc)
                    if new_uid:
                        st.success(f"¡Alumno {en_name} matriculado con éxito! Ya puede ingresar con su correo {en_email}.")
                        st.rerun()
                    else:
                        st.error("Error al registrar alumno en Supabase.")
