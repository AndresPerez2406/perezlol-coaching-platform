import streamlit as st
from database.client import get_supabase_client
from views.login import render_login
from views.student_view import render_student_view
from views.coach_view import render_coach_view
from views.admin_view import render_admin_view
from styles.theme import get_theme_css

st.set_page_config(
    page_title="PerezLoL Campus Virtual | LoL Coaching",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    supabase = get_supabase_client()
    
    # Inicializar estado de sesión
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    # Inyectar estilos del tema activo (Oscuro / Claro)
    st.markdown(get_theme_css(st.session_state["theme"]), unsafe_allow_html=True)

    selected_module = None
        
    with st.sidebar:
        # Cabecera con botón rápido de cambio de tema
        col_sb_title, col_sb_theme = st.columns([3, 1])
        with col_sb_title:
            st.title("🌲 PerezLoL")
        with col_sb_theme:
            st.write("")
            cur_th = st.session_state.get("theme", "dark")
            icon_btn = "☀️" if cur_th == "dark" else "🌙"
            if st.button(icon_btn, key="top_theme_toggle_btn", use_container_width=True):
                st.session_state["theme"] = "light" if cur_th == "dark" else "dark"
                st.rerun()

        st.caption("Campus Virtual & Academia de Coaching | **League of Legends**")
        
        if st.session_state["user"]:
            user_data = st.session_state["user"]
            real_role = user_data.get("role", "student")
            email = user_data.get("email", "")
            riot_tag = user_data.get("riot_id") or "Sin Riot ID"
            
            # Badge del usuario
            st.markdown(f"**Usuario:** `{riot_tag}`")
            st.caption(f"📧 {email} | Rol: **{real_role.upper()}**")
            st.divider()

            # MÓDULOS DEL CAMPUS VIRTUAL (ESTILO MOODLE) EN EL SIDEBAR
            if real_role == "student":
                st.markdown("### 📚 Módulos del Campus")
                student_modules = [
                    "📊 Mi Aula & Clases Activas",
                    "🎯 Misiones & Tareas Técnicas",
                    "🛒 Comprar Clases / Recargar (P2P)",
                    "📑 Historial de Comprobantes",
                    "👤 Mi Perfil & Ajustes"
                ]
                default_st_idx = 0
                if st.session_state.get("just_registered") or st.session_state.get("student_target_module") == "🛒 Comprar Clases / Recargar (P2P)":
                    default_st_idx = 2

                selected_module = st.radio("Navegación:", student_modules, index=default_st_idx, label_visibility="collapsed")

                st.write("")
                with st.container(border=True):
                    st.markdown("💬 **Coach Perez** *(Especialidad: Jungla)*")
                    st.caption("🎙️ Discord: `perez1473`")
                    st.link_button("Abrir Discord", "https://discord.com/app", use_container_width=True)

            elif real_role == "coach":
                st.markdown("### 📋 Menú del Coach")
                coach_modules = [
                    "👥 Mis Estudiantes Asignados",
                    "📅 Programar y Gestionar Clases",
                    "📝 Asignar Tareas y Misiones Técnicas"
                ]
                coach_idx = 0
                if st.session_state.get("coach_active_mod") in coach_modules:
                    coach_idx = coach_modules.index(st.session_state["coach_active_mod"])
                    st.session_state["coach_active_mod"] = None

                selected_module = st.radio("Navegación:", coach_modules, index=coach_idx, label_visibility="collapsed")

            elif real_role == "admin":
                st.markdown("### 🛡️ Menú de Administración")
                # Admin puede alternar vistas de supervisión
                active_view = st.selectbox("Modo de Vista:", ["Administrador Central", "Vista Coach", "Vista Estudiante"])
                if active_view == "Vista Estudiante":
                    real_role = "student"
                    student_modules = [
                        "📊 Mi Aula & Clases Activas",
                        "🎯 Misiones & Tareas Técnicas",
                        "🛒 Comprar Clases / Recargar (P2P)",
                        "📑 Historial de Comprobantes",
                        "👤 Mi Perfil & Ajustes"
                    ]
                    selected_module = st.radio("Navegación:", student_modules, label_visibility="collapsed")
                elif active_view == "Vista Coach":
                    real_role = "coach"
                    coach_modules = [
                        "👥 Mis Estudiantes Asignados",
                        "📅 Programar y Gestionar Clases",
                        "📝 Asignar Tareas y Misiones Técnicas"
                    ]
                    selected_module = st.radio("Navegación:", coach_modules, label_visibility="collapsed")
                else:
                    admin_modules = [
                        "📦 Paquetes & Modos de Coaching",
                        "🎓 CRUD de Estudiantes",
                        "🎮 Agenda & Control de Coaching",
                        "💰 CRUD y Auditoría de Pagos",
                        "🛡️ Gestión de Coaches y Roles"
                    ]
                    selected_module = st.radio("Navegación:", admin_modules, label_visibility="collapsed")

            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                if supabase:
                    try:
                        supabase.auth.sign_out()
                    except Exception:
                        pass
                st.session_state["user"] = None
                st.rerun()
        else:
            st.info("Inicia sesión en el campus para acceder a tus módulos.")

    # Enrutamiento de vistas según el rol y módulo seleccionado
    if not st.session_state["user"]:
        render_login(supabase)
    else:
        role = st.session_state["user"].get("role", "student")
        if real_role == "student":
            render_student_view(supabase, st.session_state["user"], selected_module)
        elif real_role == "coach":
            render_coach_view(supabase, st.session_state["user"], selected_module)
        else:
            render_admin_view(supabase, st.session_state["user"], selected_module)

if __name__ == "__main__":
    main()
