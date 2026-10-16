import streamlit as st
import base64
from datetime import datetime
from database.operations import (
    get_packages, get_student_package, submit_payment, get_student_payments,
    get_student_sessions, get_student_tasks, toggle_task,
    update_profile_details, update_account_password, get_profile
)

def render_student_view(supabase, user, active_module=None):
    student_id = user.get("id")
    module = active_module or "📊 Mi Aula & Clases Activas"

    # --------------------------------------------------------------------------
    # DATOS DEL ESTUDIANTE (Sincronizados con Supabase)
    # --------------------------------------------------------------------------
    db_profile = get_profile(supabase, student_id) if supabase else None
    current_name = db_profile.get("full_name") if db_profile else (user.get("full_name") or user.get("email", "Estudiante"))
    student_riot = db_profile.get("riot_id") if db_profile else (user.get("riot_id") or "Sin Riot ID")
    student_discord = db_profile.get("discord_tag") if db_profile else (user.get("discord_tag") or "perez1473")
    student_avatar = db_profile.get("avatar_url") if db_profile else None
    student_tier = db_profile.get("current_tier", "EMERALD") if db_profile else "EMERALD"
    student_rank = db_profile.get("current_rank", "II") if db_profile else "II"
    student_lp = db_profile.get("current_lp", 35) if db_profile else 35

    # Consultar créditos y paquete activo
    active_pkg = get_student_package(supabase, student_id) if supabase else None
    vod_rem = active_pkg.get("vod_classes_remaining", 0) if active_pkg else 0
    live_rem = active_pkg.get("live_classes_remaining", 0) if active_pkg else 0
    vod_tot = active_pkg.get("vod_classes_total", 0) if active_pkg else 0
    vod_comp = active_pkg.get("vod_classes_completed", 0) if active_pkg else 0
    live_tot = active_pkg.get("live_classes_total", 0) if active_pkg else 0
    live_comp = active_pkg.get("live_classes_completed", 0) if active_pkg else 0

    # Tareas y sesiones
    tasks_list = get_student_tasks(supabase, student_id) if supabase else []
    completed_tasks = len([t for t in tasks_list if t.get("is_completed")])
    total_tasks = len(tasks_list)

    student_sessions = get_student_sessions(supabase, student_id) if supabase else []
    scheduled_sessions = [s for s in student_sessions if s.get("status") == "scheduled"]
    next_session = scheduled_sessions[0] if scheduled_sessions else None

    # ==============================================================================
    # MÓDULO 1: MI AULA & CLASES ACTIVAS (DASHBOARD VISUAL PRINCIPAL)
    # ==============================================================================
    if "Mi Aula" in module:
        st.subheader("🎓 Aula Virtual de Entrenamiento — League of Legends")
        st.caption(f"Estudiante: **{current_name}** | Discord Coach: `perez1473` | Discord Alumno: `{student_discord}`")

        # Banner de Comunicación y Acceso al Coach Perez
        with st.container(border=True):
            col_cc1, col_cc2 = st.columns([3, 1])
            with col_cc1:
                st.markdown("### 🎙️ Contacto Directo con tu Coach Perez (Especialidad: Jungla)")
                st.markdown(
                    "Las revisiones de VOD y sesiones LIVE Game se realizan por llamada de voz y pantalla compartida vía **Discord**.  \n"
                    "• **Discord del Coach:** `perez1473` (Perez)  \n"
                    "• **Especialidad del Coach:** Jungla (Rutas de Jungleo, Tracking del JG Rival, Control de Oleadas y Objetivos)."
                )
            with col_cc2:
                st.write("")
                st.code("perez1473", language="text")
                st.link_button("🌐 Abrir Discord Web", "https://discord.com/app", use_container_width=True)

        st.write("")

        # 1. Hero Card del Invocador
        with st.container(border=True):
            col_av, col_det = st.columns([1, 5])
            with col_av:
                if student_avatar:
                    st.image(student_avatar, width=105)
                else:
                    st.markdown(
                        """
                        <div style='background: linear-gradient(135deg, #091428, #0A323C); border: 2px solid #C89B3C; border-radius: 50%; width: 90px; height: 90px; display: flex; align-items: center; justify-content: center; font-size: 40px;'>
                            🌲
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            with col_det:
                st.markdown(f"### **{current_name}**")
                st.markdown(f"🎮 **Riot ID:** `{student_riot}` | 🎙️ **Discord:** `{student_discord}`")
                st.markdown(f"🏆 **Rango de Invocador:** :blue[**{student_tier} {student_rank}**] ({student_lp} LP) — *Especialidad: Jungla*")

        st.write("")

        # 2. Paquete Activo y Créditos
        with st.container(border=True):
            st.markdown("#### 📦 Tu Paquete de Clases")
            if active_pkg:
                pkg_data = active_pkg.get("packages") or {}
                pkg_title = pkg_data.get("title", "Plan Activo")
                st.success(f"**Plan en Curso:** {pkg_title}")

                c_m1, c_m2 = st.columns(2)
                with c_m1:
                    st.metric("VOD Reviews Disponibles", f"{vod_rem} clases", delta=f"{vod_comp} de {vod_tot} completadas")
                    r_v = (vod_comp / vod_tot) if vod_tot > 0 else 0.0
                    st.progress(r_v, text=f"Progreso VODs: {vod_comp}/{vod_tot}")
                    st.caption("Consiste en 1 análisis exhaustivo de partida grabada (30 a 60 min).")
                with c_m2:
                    st.metric("LIVE Games Disponibles", f"{live_rem} clases", delta=f"{live_comp} de {live_tot} completadas")
                    r_l = (live_comp / live_tot) if live_tot > 0 else 0.0
                    st.progress(r_l, text=f"Progreso LIVEs: {live_comp}/{live_tot}")
                    st.caption("Partida en directo vía Discord (`perez1473`) con feedback en tiempo real.")
            else:
                st.warning("⚠️ No tienes un paquete activo actualmente.")
                st.write("Adquiere clases en el módulo **'🛒 Comprar Clases / Recargar (P2P)'** en el menú de la izquierda.")

        st.write("")

        # 3. Próxima Clase Programada por el Coach
        with st.container(border=True):
            st.markdown("#### 📅 Próxima Clase Programada por el Coach")
            if next_session:
                s_type = next_session.get("service_type", "vod").upper()
                s_date = next_session.get("scheduled_at", "")[:16].replace("T", " ")
                s_dur = next_session.get("duration_minutes", 45)
                
                if s_type == "LIVE":
                    st.info(f"🔴 **LIVE GAME COACHING**  \n📅 **Fecha y Hora:** {s_date} hrs  \n⏱️ **Duración:** {s_dur} min  \n🎙️ **Canal:** Discord `perez1473` (Conexión en llamada directa con pantalla compartida).")
                else:
                    st.info(f"📹 **VOD REVIEW SESIÓN**  \n📅 **Fecha y Hora:** {s_date} hrs  \n⏱️ **Duración:** {s_dur} min  \n🎙️ **Canal:** Discord `perez1473`.")
            else:
                st.info("ℹ️ No tienes sesiones programadas por ahora. El Coach fijará tu fecha de clase según tu disponibilidad en Discord (`perez1473`).")

        st.write("")

        # 4. Resumen de Misiones Técnicas
        with st.container(border=True):
            st.markdown("#### 🏹 Cuaderno de Misiones JG")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.write(f"**Misiones Completadas:** {completed_tasks} de {total_tasks}")
                p_val = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0
                st.progress(p_val)
            with col_p2:
                st.caption("Ve al módulo **'🎯 Misiones & Tareas JG'** en el menú lateral para revisar tus tareas asignadas y marcarlas como realizadas.")

    # ==============================================================================
    # MÓDULO 2: MISIONES & TAREAS JG
    # ==============================================================================
    elif "Misiones" in module:
        st.subheader("🎯 Misiones Técnicas y Tareas JG")
        st.caption("Pautas y objetivos asignados por el Coach para perfeccionar tu juego en la Jungla:")

        if tasks_list:
            st.write("Marca con el checkbox cada tarea a medida que la cumplas en tus partidas:")
            for t in tasks_list:
                t_id = t.get("id")
                is_done = t.get("is_completed", False)
                title = t.get("title", "")
                cat = t.get("category", "pathing").upper()
                desc = t.get("description", "")
                due = t.get("due_date", "")

                with st.container(border=True):
                    chk = st.checkbox(f"**[{cat}]** {title}", value=is_done, key=f"moodle_task_{t_id}")
                    if desc:
                        st.caption(f"Instrucciones: {desc}")
                    if due:
                        st.caption(f"📅 Fecha límite: {due}")

                    if chk != is_done and supabase:
                        toggle_task(supabase, t_id, chk)
                        st.rerun()
        else:
            with st.container(border=True):
                st.info("🌱 No tienes tareas asignadas en este momento. El Coach te dejará tus misiones tras tu primera clase.")
                st.markdown("""
                **Misiones típicas que trabajarás:**
                * 🏹 **[PATHING]** Full clear hacia botlane antes del 3:25 con Nocturne/Hecarim.
                * 👁️ **[VISION]** Ward de control en raptores enemigos al 1:15 para identificar la ruta rival.
                * ⏳ **[TEMPO]** Respetar el ciclo de respawn y no forzar ganks con campamentos listos.
                """)

    # ==============================================================================
    # MÓDULO 3: COMPRAR CLASES / RECARGAR P2P
    # ==============================================================================
    elif "Comprar Clases" in module:
        st.subheader("🛒 Tienda de Clases de la Academia — Seleccionar Paquete")
        st.caption("Elige tu paquete o modalidad de coaching, realiza tu transferencia P2P y sube la captura de tu comprobante:")

        # Banner de bienvenida al estudiante recién registrado
        if st.session_state.get("just_registered"):
            st.info(
                f"🎉 **¡Bienvenido a PerezLoL Coaching Academy, {current_name}!**  \n\n"
                "Tu perfil de invocador ha sido creado exitosamente. Para comenzar tus entrenamientos personalizados con el Coach, "
                "escoge a continuación el paquete que deseas adquirir y sube tu comprobante de pago.",
                icon="🎮"
            )

        # BANNER DE CONFIRMACIÓN EN VERDE (PERSISTENTE TRAS SUBIR COMPROBANTE)
        if st.session_state.get("payment_sent_success"):
            st.success(
                "🎉 **¡SOLICITUD DE COMPRA Y COMPROBANTE ENVIADOS CON ÉXITO!**  \n\n"
                "Tu comprobante ha sido registrado correctamente. El Administrador verificará tu transferencia y te acreditará las clases correspondientes en tu Aula Virtual.  \n"
                "👉 Puedes consultar el estado de tu pago en la pestaña **'📑 Historial de Comprobantes'**.",
                icon="✅"
            )
            st.balloons()
            if st.button("➕ Subir otro comprobante"):
                st.session_state["payment_sent_success"] = False
                st.rerun()
            st.divider()

        # --------------------------------------------------------------------------
        # CATÁLOGO DINÁMICO DE PAQUETES Y MODOS DE COACHING
        # --------------------------------------------------------------------------
        db_packages = get_packages(supabase) if supabase else []
        if not db_packages:
            db_packages = [
                {"id": "p1", "title": "Pack Primer Coaching (Recomendado)", "price": 14.00, "vod_classes": 3, "live_classes": 1, "description": "1 clase en vivo para auditar tus hábitos y 3 VODs semanales para pulir micro y macro."},
                {"id": "p2", "title": "Pack 4 VODs Reviews", "price": 12.00, "vod_classes": 4, "live_classes": 0, "description": "4 revisiones minuciosas de partidas grabadas para afianzar conceptos clave."},
                {"id": "p3", "title": "1 LIVE GAME Coaching", "price": 5.00, "vod_classes": 0, "live_classes": 1, "description": "1 partida en directo vía Discord con análisis de decisiones en tiempo real."},
                {"id": "p4", "title": "1 Sesión VOD Review", "price": 3.50, "vod_classes": 1, "live_classes": 0, "description": "Revisión individual detallada con entrega de puntos prioritarios de mejora."}
            ]

        st.markdown("#### 🌟 Modos de Coaching Disponibles")
        
        # Renderizar en 2 columnas elegantes
        cols = st.columns(2)
        for i, pkg in enumerate(db_packages):
            col_target = cols[i % 2]
            with col_target:
                p_id = pkg.get("id")
                p_title = pkg.get("title", "Paquete Coaching")
                p_price = pkg.get("price", 0.0)
                p_vod = pkg.get("vod_classes", 0)
                p_live = pkg.get("live_classes", 0)
                p_desc = pkg.get("description", "Sesiones personalizadas de League of Legends.")

                with st.container(border=True):
                    st.markdown(f"### **{p_title}**")
                    st.markdown(f"💰 :green[**${p_price:.2f} USD**] | 📹 **{p_vod} VODs** + 🔴 **{p_live} LIVEs**")
                    st.write(p_desc)
                    if st.button(f"👉 Escoger este Paquete (${p_price:.2f} USD)", key=f"btn_pick_pkg_{p_id}", use_container_width=True):
                        st.session_state["preselected_pkg_id"] = p_id
                        st.rerun()

        st.divider()
        st.subheader("Subir Comprobante de Transferencia P2P")

        # Mapeo de paquetes para el formulario
        pkg_menu = {}
        for p in db_packages:
            pkg_menu[f"{p.get('title')} — ${p.get('price'):.2f} USD"] = p

        # Calcular índice preseleccionado
        pre_idx = 0
        if "preselected_pkg_id" in st.session_state:
            for idx, p in enumerate(db_packages):
                if p.get("id") == st.session_state["preselected_pkg_id"]:
                    pre_idx = idx
                    break

        sel_p_label = st.selectbox("Paquete Seleccionado a Adquirir", list(pkg_menu.keys()), index=pre_idx)
        selected_pkg_obj = pkg_menu[sel_p_label]

        # Caja de canales oficiales de pago
        with st.container(border=True):
            st.markdown("#### 💳 Canales Oficiales de Pago P2P")
            st.markdown(
                "Realiza tu pago por cualquiera de los siguientes medios oficiales:  \n"
                "• **Binance Pay (USDT):** Solicita el Pay ID al Staff o Coach por Discord: `perez1473`.  \n"
                "• **Nequi / Bancolombia (Colombia):** Solicita el número de cuenta o código QR por Discord: `perez1473`."
            )
            col_co1, col_co2 = st.columns([2, 1])
            with col_co1:
                st.markdown("🎙️ **Discord Oficial:** `perez1473` (Perez)")
            with col_co2:
                st.link_button("💬 Abrir Discord", "https://discord.com/app", use_container_width=True)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            method_chosen = st.selectbox("Medio de Pago Utilizado", ["Binance Pay (USDT)", "Nequi", "Transferencia Bancaria", "Otro Medio"])
            st.metric("Monto a Validar", f"${selected_pkg_obj.get('price', 0.0):.2f} USD")
        with col_f2:
            receipt_img = st.file_uploader("Adjunta foto o captura del comprobante *", type=["png", "jpg", "jpeg", "webp"])
            if receipt_img is not None:
                st.image(receipt_img, caption="Vista previa del comprobante", width=220)

        if st.button("🚀 Enviar Comprobante para Acreditación", type="primary", use_container_width=True):
            if receipt_img is None:
                st.warning("⚠️ Debes adjuntar la imagen del comprobante de transferencia.")
            elif not supabase:
                st.session_state["payment_sent_success"] = True
                st.rerun()
            else:
                try:
                    f_b = receipt_img.read()
                    b64 = base64.b64encode(f_b).decode("utf-8")
                    mime = receipt_img.type or "image/png"
                    data_uri = f"data:{mime};base64,{b64}"

                    ok = submit_payment(
                        supabase=supabase,
                        student_id=student_id,
                        package_id=selected_pkg_obj.get("id"),
                        amount=float(selected_pkg_obj.get("price", 0.0)),
                        payment_method=method_chosen,
                        receipt_url=data_uri,
                        reference_number=""
                    )
                    if ok:
                        st.session_state["payment_sent_success"] = True
                        st.rerun()
                    else:
                        st.error("Error al registrar el comprobante en la base de datos.")
                except Exception as e:
                    st.error(f"Error al procesar el archivo: {e}")

    # ==============================================================================
    # MÓDULO 4: HISTORIAL DE COMPROBANTES
    # ==============================================================================
    elif "Historial" in module:
        st.subheader("📑 Estado de tus Comprobantes Enviados")
        st.caption("Verifica si tus transferencias ya fueron aprobadas por el Coach o Admin:")

        my_payments = get_student_payments(supabase, student_id) if supabase else []
        if my_payments:
            for mp in my_payments:
                s_raw = mp.get("status", "pending")
                s_badge = "🟡 Pendiente de Aprobación" if s_raw == "pending" else ("🟢 Aprobado (Clases Acreditadas)" if s_raw == "approved" else "🔴 Rechazado")
                pkg_t = mp.get("packages", {}).get("title", "Coaching") if mp.get("packages") else "Coaching"
                
                with st.container(border=True):
                    st.markdown(f"#### **{pkg_t}** — ${mp.get('amount')} USD")
                    st.write(f"**Medio:** {mp.get('payment_method')} | **Fecha:** {mp.get('created_at')[:10]}")
                    st.write(f"**Estado:** {s_badge}")
        else:
            st.info("No has enviado comprobantes de pago aún.")

    # ==============================================================================
    # MÓDULO 5: MI PERFIL & AJUSTES
    # ==============================================================================
    elif "Mi Perfil" in module:
        st.subheader("👤 Mi Perfil de Invocador & Ajustes de Cuenta")
        st.caption("Actualiza tus datos de League of Legends, foto de perfil y seguridad:")

        with st.container(border=True):
            st.markdown("#### 1. Datos del Invocador")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                new_full_name = st.text_input("Nombre Completo", value=current_name, key="st_name_moodle")
                new_riot = st.text_input("Riot ID (ej: Invocador#LAN)", value=student_riot, key="st_riot_moodle")
            with col_p2:
                new_disc = st.text_input("Discord Tag", value=student_discord, key="st_disc_moodle")
                new_avatar_file = st.file_uploader("Cambiar Foto de Perfil", type=["png", "jpg", "jpeg"], key="st_av_moodle")

            if st.button("Guardar Cambios de Perfil", type="primary", use_container_width=True):
                final_avatar = student_avatar
                if new_avatar_file is not None:
                    try:
                        b = new_avatar_file.read()
                        b64 = base64.b64encode(b).decode("utf-8")
                        m = new_avatar_file.type or "image/png"
                        final_avatar = f"data:{m};base64,{b64}"
                    except Exception:
                        pass

                if supabase:
                    ok = update_profile_details(
                        supabase=supabase,
                        user_id=student_id,
                        full_name=new_full_name,
                        riot_id=new_riot,
                        discord_tag=new_disc,
                        avatar_url=final_avatar or ""
                    )
                    if ok:
                        st.success("¡Perfil actualizado con éxito!")
                        st.rerun()
                    else:
                        st.error("Error al actualizar perfil.")
                else:
                    st.success("Perfil actualizado (Modo Demo).")

        st.write("")
        with st.container(border=True):
            st.markdown("#### 2. Seguridad y Contraseña")
            st.write(f"Correo registrado: **{user.get('email', '')}**")
            p1 = st.text_input("Nueva Contraseña", type="password", key="chg_p1_m")
            p2 = st.text_input("Confirmar Nueva Contraseña", type="password", key="chg_p2_m")
            if st.button("Actualizar Contraseña", use_container_width=True):
                if not p1 or len(p1) < 6:
                    st.warning("Mínimo 6 caracteres.")
                elif p1 != p2:
                    st.error("Las contraseñas no coinciden.")
                elif supabase:
                    ok = update_account_password(supabase, p1)
                    if ok:
                        st.success("¡Contraseña actualizada correctamente!")
                    else:
                        st.error("No se pudo actualizar la contraseña.")
                else:
                    st.success("Contraseña actualizada (Modo Demo).")
