import streamlit as st
from datetime import datetime, date
from database.operations import (
    get_coach_sessions, complete_session, assign_task,
    get_coach_tasks, update_task_feedback, save_session_notes,
    get_all_users, book_session, get_student_package
)

def render_coach_view(supabase, user, active_module=None):
    coach_id = user.get("id")
    coach_name = user.get("full_name") or user.get("riot_id") or "Coach Perez"
    coach_disc = user.get("discord_tag") or "perez1473"
    
    # Módulo activo o por defecto
    mod = active_module or "👥 Mis Estudiantes Asignados"
    
    st.markdown(f"<h2 class='main-title'>🛡️ Panel de Control del Coach — {coach_name}</h2>", unsafe_allow_html=True)
    st.caption(f"Especialidad: **Jungla & Macro** | Canal oficial de voz Discord: `perez1473`")

    # Consultar datos en tiempo real
    coach_sessions = get_coach_sessions(supabase) if supabase else []
    all_users = get_all_users(supabase) if supabase else []
    students = [u for u in all_users if u.get("role") == "student"]
    coach_tasks = get_coach_tasks(supabase, coach_id) if supabase else []
    completed_tasks = [t for t in coach_tasks if t.get("is_completed")]

    # Métricas clave del Coach (Sin pagos ni matrículas)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Alumnos Asignados", len(students))
    with col2:
        st.metric("Clases en Agenda", len([s for s in coach_sessions if s.get("status") == "scheduled"]))
    with col3:
        st.metric("Tareas Activas", len(coach_tasks))
    with col4:
        st.metric("Misiones Cumplidas", len(completed_tasks), delta=f"{len(completed_tasks)}/{len(coach_tasks)}" if coach_tasks else "0")

    st.divider()

    # ==============================================================================
    # MÓDULO 1: MIS ESTUDIANTES ASIGNADOS
    # ==============================================================================
    if "Estudiantes" in mod or "Alumnos" in mod:
        st.subheader("👥 Directorio de Mis Estudiantes")
        st.caption("Supervisa a tus alumnos, sus roles, ligas actuales y el saldo de clases de sus paquetes:")

        if students:
            for s in students:
                s_id = s.get("id")
                s_name = s.get("full_name") or "Alumno"
                s_riot = s.get("riot_id") or "Sin Riot ID"
                s_disc = s.get("discord_tag") or "No registrado"
                s_email = s.get("email") or "Sin email"
                s_tier = s.get("current_tier", "GOLD")
                s_rank = s.get("current_rank", "IV")
                s_lp = s.get("current_lp", 0)
                s_lane = s.get("main_lane", "JUNGLE").upper()

                # Paquete activo y créditos restantes
                st_pkg = get_student_package(supabase, s_id) if supabase else None
                v_rem = st_pkg.get("vod_classes_remaining", 0) if st_pkg else 0
                l_rem = st_pkg.get("live_classes_remaining", 0) if st_pkg else 0
                v_comp = st_pkg.get("vod_classes_completed", 0) if st_pkg else 0
                l_comp = st_pkg.get("live_classes_completed", 0) if st_pkg else 0
                pkg_title = st_pkg.get("packages", {}).get("title", "Sin paquete activo") if st_pkg else "Sin paquete activo"

                # Tareas del estudiante
                st_tasks = [t for t in coach_tasks if t.get("student_id") == s_id]
                st_done_tasks = len([t for t in st_tasks if t.get("is_completed")])

                with st.container(border=True):
                    c_st1, c_st2, c_st3 = st.columns([2.5, 2.5, 1.5])
                    with c_st1:
                        st.markdown(f"#### **{s_name}** (`{s_riot}`)")
                        st.write(f"🎮 **Rol:** `{s_lane}` | 🏆 **Rango:** `{s_tier} {s_rank}` ({s_lp} LP)")
                        st.write(f"📧 `{s_email}` | 🎙️ Discord: `{s_disc}`")
                    with c_st2:
                        st.markdown(f"📦 **Plan:** {pkg_title}")
                        st.write(f"• **VODs Restantes:** :green[**{v_rem} disponibles**] *(Completadas: {v_comp})*")
                        st.write(f"• **LIVEs Restantes:** :blue[**{l_rem} disponibles**] *(Completadas: {l_comp})*")
                        st.caption(f"🎯 Misiones completadas: **{st_done_tasks}** de **{len(st_tasks)}**")
                    with c_st3:
                        st.write("")
                        st.caption("Estado: **Activo**")
                        if st.button("📅 Agendar Clase", key=f"btn_sched_fast_{s_id}", use_container_width=True):
                            st.session_state["target_student_preselected"] = s_id
                            st.session_state["coach_active_mod"] = "📅 Programar y Gestionar Clases"
                            st.rerun()
                        if st.button("📝 Dejar Tarea", key=f"btn_task_fast_{s_id}", use_container_width=True):
                            st.session_state["target_student_preselected"] = s_id
                            st.session_state["coach_active_mod"] = "📝 Dejar Tareas y Retroalimentación"
                            st.rerun()
        else:
            st.info("Aún no hay estudiantes registrados en la academia.")

    # ==============================================================================
    # MÓDULO 2: PROGRAMAR Y GESTIONAR CLASES
    # ==============================================================================
    elif "Programar" in mod or "Clases" in mod:
        st.subheader("📅 Programación y Control de Clases")
        st.caption("Agenda sesiones de VOD o LIVE Game para tus estudiantes y gestiona las sesiones agendadas:")

        tab_agendar, tab_agenda = st.tabs(["➕ Agendar Nueva Clase", "📋 Sesiones en Agenda"])

        with tab_agendar:
            if students:
                student_dict = {f"{s.get('full_name') or 'Alumno'} ({s.get('riot_id') or s.get('email')})": s for s in students}
                
                # Pre-seleccionar si vino de la tarjeta del estudiante
                preselected_idx = 0
                if "target_student_preselected" in st.session_state:
                    for idx, s in enumerate(students):
                        if s.get("id") == st.session_state["target_student_preselected"]:
                            preselected_idx = idx
                            break

                sel_st_label = st.selectbox("Selecciona al Alumno", list(student_dict.keys()), index=preselected_idx, key="sched_st_select")
                target_student = student_dict[sel_st_label]
                target_st_id = target_student.get("id")

                with st.container(border=True):
                    col_sc1, col_sc2 = st.columns(2)
                    with col_sc1:
                        sched_type = st.radio("Modalidad de Clase", ["LIVE GAME Coaching (En Vivo por Discord)", "VOD Review (Análisis de Repetición)"], key="sched_type_rad")
                        sched_service = "live" if "LIVE" in sched_type else "vod"
                        sched_date = st.date_input("Fecha de la Sesión", min_value=date.today(), key="sched_date_input")
                        sched_time = st.selectbox("Hora Acordada", ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"], index=4, key="sched_time_sel")
                    with col_sc2:
                        sched_dur = st.select_slider("Duración Estimada (Minutos)", options=[30, 45, 60, 90], value=45, key="sched_dur_slider")
                        sched_discord = st.text_input("Canal o Voz de Discord", value=f"Canal de Voz PerezLoL (Coach: {coach_disc})", key="sched_disc_input")
                        sched_notes = st.text_area("Objetivo / Temas Previos a Trabajar", placeholder="Ej: Revisión de primeros 3 clears, control de oleadas en bot para primer dragón.", key="sched_notes_input")

                    if st.button("🚀 Confirmar y Agendar Clase en Calendario", type="primary", use_container_width=True):
                        sched_iso = f"{sched_date.isoformat()}T{sched_time}:00Z"
                        if supabase:
                            ok = book_session(
                                supabase=supabase,
                                student_id=target_st_id,
                                service_type=sched_service,
                                scheduled_at=sched_iso,
                                coach_id=coach_id,
                                duration_minutes=sched_dur,
                                vod_url=sched_notes,
                                discord_tag=sched_discord
                            )
                            if ok:
                                st.success(f"¡Clase agendada exitosamente para {target_student.get('full_name')}! Aparecerá de inmediato en su Aula Virtual.")
                                st.session_pop = st.session_state.pop("target_student_preselected", None)
                                st.rerun()
                            else:
                                st.error("Hubo un error al registrar la clase en la base de datos.")
                        else:
                            st.success("Clase agendada (Modo Local).")
            else:
                st.info("No hay estudiantes registrados para agendar clases.")

        with tab_agenda:
            st.markdown("##### Historial y Clases en Agenda")
            filter_status = st.selectbox("Filtrar por estado", ["Todas", "scheduled (Programadas)", "completed (Completadas)", "cancelled (Canceladas)"])
            
            filtered_sessions = coach_sessions
            if "scheduled" in filter_status:
                filtered_sessions = [s for s in coach_sessions if s.get("status") == "scheduled"]
            elif "completed" in filter_status:
                filtered_sessions = [s for s in coach_sessions if s.get("status") == "completed"]
            elif "cancelled" in filter_status:
                filtered_sessions = [s for s in coach_sessions if s.get("status") == "cancelled"]

            if filtered_sessions:
                for cs in filtered_sessions:
                    cs_id = cs.get("id")
                    st_p = cs.get("profiles") or {}
                    cs_type = cs.get("service_type", "vod").upper()
                    cs_time = cs.get("scheduled_at", "")[:16].replace("T", " ")
                    cs_status = cs.get("status", "scheduled")
                    cs_dur = cs.get("duration_minutes", 45)
                    cs_st_name = st_p.get("full_name") or st_p.get("riot_id") or "Alumno"

                    with st.container(border=True):
                        c_cs1, c_cs2 = st.columns([3, 1.2])
                        with c_cs1:
                            st.markdown(f"#### **{cs_type} Coaching** — `{cs_time}`")
                            st.write(f"👤 **Alumno:** **{cs_st_name}** (`{st_p.get('riot_id', 'Sin Riot ID')}`) | 🎙️ Discord: `{cs_p_tag}`" if (cs_p_tag := cs.get("discord_tag")) else f"👤 **Alumno:** **{cs_st_name}** (`{st_p.get('riot_id', 'Sin Riot ID')}`)")
                            st.caption(f"Duración: **{cs_dur} min** | Estado: `{cs_status.upper()}`")
                            if cs.get("vod_url"):
                                st.caption(f"📝 Notas iniciales: {cs.get('vod_url')}")
                        with c_cs2:
                            st.write("")
                            if cs_status == "scheduled":
                                with st.expander("✅ Finalizar Clase"):
                                    st.write("Al finalizar, se descontará automáticamente el crédito del paquete del estudiante.")
                                    hw_txt = st.text_input("Resumen técnico", placeholder="Conceptos trabajados", key=f"comp_txt_{cs_id}")
                                    if st.button("Confirmar Finalizada", key=f"btn_comp_{cs_id}", type="primary", use_container_width=True):
                                        ok = complete_session(supabase, cs_id, coach_id)
                                        if ok:
                                            if hw_txt and supabase:
                                                save_session_notes(
                                                    supabase=supabase,
                                                    session_id=cs_id,
                                                    coach_id=coach_id,
                                                    student_id=cs.get("student_id"),
                                                    strengths="Buen tracking inicial",
                                                    areas_to_improve="Ganks forzados sin visión",
                                                    pathing=hw_txt,
                                                    champion_pool="",
                                                    homework_summary=hw_txt
                                                )
                                            st.success("¡Clase marcada como completada y crédito descontado!")
                                            st.rerun()
                                        else:
                                            st.error("Error al completar la sesión.")
                            elif cs_status == "completed":
                                st.success("✅ Clase Realizada")
                            else:
                                st.warning("❌ Cancelada")
            else:
                st.info("No hay sesiones en esta categoría.")

    # ==============================================================================
    # MÓDULO 3: ASIGNAR TAREAS Y NOTAS TÉCNICAS
    # ==============================================================================
    elif "Tareas" in mod or "Retroalimentación" in mod:
        st.subheader("📝 Misiones Prácticas y Tareas para Estudiantes")
        st.caption("Deja tareas personalizadas con objetivos concretos para que tus estudiantes las apliquen en SoloQ:")

        tab_new_task, tab_task_list = st.tabs(["➕ Asignar Nueva Misión", "📋 Auditoría y Feedback de Tareas"])

        with tab_new_task:
            if students:
                st_opts = {f"{s.get('full_name') or 'Alumno'} ({s.get('riot_id') or s.get('email')})": s.get("id") for s in students}
                
                t_pre_idx = 0
                if "target_student_preselected" in st.session_state:
                    for idx, (lbl, sid) in enumerate(st_opts.items()):
                        if sid == st.session_state["target_student_preselected"]:
                            t_pre_idx = idx
                            break

                sel_student_label = st.selectbox("Seleccionar Alumno", list(st_opts.keys()), index=t_pre_idx, key="task_student_sel")
                chosen_s_id = st_opts[sel_student_label]

                with st.container(border=True):
                    st.markdown("##### Detalles de la Misión / Tarea Técnica")
                    c_t1, c_t2 = st.columns([2.5, 1.5])
                    with c_t1:
                        t_title = st.text_input("Título de la Misión", placeholder="Ej: Full clear hacia bot antes del 3:25 con Nocturne.")
                        t_desc = st.text_area("Pautas Detalladas de Ejecución", placeholder="Hacer kiting sin recibir daño de los campamentos medianos. Guardar smite para cangrejo.", height=110)
                    with c_t2:
                        t_cat = st.selectbox("Categoría / Área", [
                            "pathing (Rutas y Tiempos de Limpieza)",
                            "vision_control (Control de Visión y Wards)",
                            "wave_management (Control de Oleadas y Reseteos)",
                            "objective_setup (Control de Dragones / Barón / Herald)",
                            "invade_macro (Tracking y Contrajungla)",
                            "champion_pool (Pool de Campeones y Matchups)",
                            "mental (Mentalidad y No Forzar Plays)"
                        ])
                        cat_slug = t_cat.split(" ")[0]
                        t_due = st.date_input("Fecha Límite de Cumplimiento", min_value=date.today(), key="task_due_key")

                    if st.button("🎯 Asignar Misión al Alumno", type="primary", use_container_width=True):
                        if not t_title:
                            st.warning("Escribe el título de la tarea.")
                        elif supabase:
                            ok = assign_task(
                                supabase=supabase,
                                student_id=chosen_s_id,
                                coach_id=coach_id,
                                title=t_title,
                                description=t_desc,
                                category=cat_slug,
                                due_date=t_due.isoformat()
                            )
                            if ok:
                                st.success("¡Tarea asignada exitosamente! El estudiante la verá en su Cuaderno de Misiones.")
                                st.session_state.pop("target_student_preselected", None)
                                st.rerun()
                            else:
                                st.error("Error al registrar la tarea.")
                        else:
                            st.success("Tarea asignada (Modo Local).")
            else:
                st.info("No hay estudiantes registrados para asignar tareas.")

        with tab_task_list:
            st.markdown("##### Historial de Misiones y Feedback del Coach")
            if coach_tasks:
                for ct in coach_tasks:
                    ct_id = ct.get("id")
                    st_p = ct.get("profiles") or {}
                    st_label = st_p.get("full_name") or st_p.get("riot_id") or "Alumno"
                    ct_title = ct.get("title", "")
                    ct_cat = ct.get("category", "pathing").upper()
                    ct_desc = ct.get("description", "")
                    ct_due = ct.get("due_date", "Sin fecha")
                    is_done = ct.get("is_completed", False)
                    current_fb = ct.get("coach_feedback", "") or ""

                    with st.container(border=True):
                        c_tk1, c_tk2 = st.columns([3, 1.5])
                        with c_tk1:
                            st.markdown(f"**[{ct_cat}] {ct_title}**")
                            st.write(f"👤 **Alumno:** `{st_label}` ({st_p.get('riot_id', '')}) | 📅 Límite: `{ct_due}`")
                            if ct_desc:
                                st.caption(f"Instrucciones: {ct_desc}")
                        with c_tk2:
                            if is_done:
                                st.success("✅ Completada por el alumno")
                            else:
                                st.warning("⏳ En progreso / Pendiente")

                        # Espacio de feedback del coach
                        with st.expander(f"💬 Retroalimentación del Coach ({'Con notas' if current_fb else 'Sin notas'})"):
                            new_fb = st.text_area("Comentarios y Correcciones del Coach", value=current_fb, key=f"fb_area_{ct_id}")
                            if st.button("Guardar Feedback", key=f"btn_save_fb_{ct_id}"):
                                if supabase:
                                    ok = update_task_feedback(supabase, ct_id, new_fb)
                                    if ok:
                                        st.success("Feedback actualizado.")
                                        st.rerun()
                                    else:
                                        st.error("Error al actualizar feedback.")
            else:
                st.info("Aún no has asignado tareas a tus estudiantes.")
