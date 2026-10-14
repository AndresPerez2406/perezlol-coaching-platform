import streamlit as st
from database.client import get_supabase_client
from views.login import render_login
from views.student_view import render_student_view
from views.coach_view import render_coach_view
from views.admin_view import render_admin_view

st.set_page_config(
    page_title="PerezLoL Campus Virtual | Only JG",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom LoL Hextech Jungle Theme Styling
st.markdown("""
<style>
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #C89B3C;
        text-shadow: 0 0 10px rgba(200, 155, 60, 0.3);
    }
    .stButton>button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    supabase = get_supabase_client()
    
    # Inicializar estado de sesión
    if "user" not in st.session_state:
        st.session_state["user"] = None

    selected_module = None
        
    with st.sidebar:
        st.title("🌲 PerezLoL Campus")
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
                selected_module = st.radio("Navegación:", student_modules, label_visibility="collapsed")

                st.write("")
                with st.container(border=True):
                    st.markdown("💬 **Coach Perez** *(Especialidad: Jungla)*")
                    st.caption("🎙️ Discord: `perez1473`")
                    st.link_button("Abrir Discord", "https://discord.com/app", use_container_width=True)

            elif real_role == "coach":
                st.markdown("### 📋 Menú de Gestión del Coach")
                coach_modules = [
                    "👥 Gestión de Estudiantes",
                    "📅 Programar Clases para Alumnos",
                    "💰 Aprobar Pagos P2P (Chulear)",
                    "📝 Dejar Tareas y Notas Técnicas",
                    "➕ Matricular Nuevo Alumno"
                ]
                selected_module = st.radio("Navegación:", coach_modules, label_visibility="collapsed")

            elif real_role == "admin":
                st.markdown("### 🛡️ Menú de Administración")
                # Admin puede alternar vistas de supervisión
                active_view = st.selectbox("Modo de Vista:", ["Administrador Central", "Vista Coach", "Vista Estudiante"])
                if active_view == "Vista Estudiante":
                    real_role = "student"
                    student_modules = [
                        "📊 Mi Aula & Clases Activas",
                        "🎯 Misiones & Tareas JG",
                        "🛒 Comprar Clases / Recargar (P2P)",
                        "📑 Historial de Comprobantes",
                        "👤 Mi Perfil & Ajustes"
                    ]
                    selected_module = st.radio("Navegación:", student_modules, label_visibility="collapsed")
                elif active_view == "Vista Coach":
                    real_role = "coach"
                    coach_modules = [
                        "👥 Gestión de Estudiantes",
                        "📅 Programar Clases para Alumnos",
                        "💰 Aprobar Pagos P2P (Chulear)",
                        "📝 Dejar Tareas y Notas Técnicas",
                        "➕ Matricular Nuevo Alumno"
                    ]
                    selected_module = st.radio("Navegación:", coach_modules, label_visibility="collapsed")
                else:
                    admin_modules = [
                        "👥 Gestión de Usuarios y Roles",
                        "📦 Catálogo de Paquetes",
                        "📑 Auditoría Global de Pagos"
                    ]
                    selected_module = st.radio("Navegación:", admin_modules, label_visibility="collapsed")

            st.divider()
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
