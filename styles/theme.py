"""
Módulo de Estilos y Temas (Modo Oscuro & Modo Claro)
Plataforma Coaching PerezLoL
"""
import streamlit as st

def get_theme_css(theme: str = "dark") -> str:
    """Devuelve el bloque CSS inyectable según el tema seleccionado."""
    if theme == "light":
        return """
        <style>
            /* ==============================================================
               MODO CLARO (RIFT LIGHT THEME)
               ============================================================== */
            :root {
                --bg-main: #F4F6F9;
                --bg-card: #FFFFFF;
                --bg-sidebar: #FFFFFF;
                --text-main: #1A202C;
                --text-secondary: #4A5568;
                --border-color: #E2E8F0;
                --accent-gold: #9E741B;
                --accent-gold-hover: #7D5C14;
                --accent-blue: #0969DA;
            }

            /* Fondo general de la app */
            .stApp {
                background-color: var(--bg-main) !important;
                color: var(--text-main) !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            /* Header superior */
            header[data-testid="stHeader"] {
                background-color: rgba(244, 246, 249, 0.95) !important;
            }

            /* Barra lateral (Sidebar) */
            section[data-testid="stSidebar"] {
                background-color: var(--bg-sidebar) !important;
                border-right: 1px solid var(--border-color) !important;
            }
            section[data-testid="stSidebar"] * {
                color: var(--text-main);
            }
            section[data-testid="stSidebar"] .stCaption,
            section[data-testid="stSidebar"] p[data-testid="stCaptionContainer"],
            section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
                color: var(--text-secondary) !important;
            }

            /* Tarjetas / Contenedores dentro del Sidebar */
            section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #F8FAFC !important;
                border: 1px solid #CBD5E0 !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
                border-radius: 10px !important;
                padding: 6px !important;
            }

            /* Código inline (los tags `riot_tag` y `perez1473` en Modo Claro) */
            code {
                background-color: #EDF2F7 !important;
                color: #9E741B !important;
                padding: 2px 8px !important;
                border-radius: 6px !important;
                border: 1px solid #CBD5E0 !important;
                font-weight: 600 !important;
                font-size: 0.9em !important;
            }

            section[data-testid="stSidebar"] code {
                background-color: #EDF2F7 !important;
                color: #9E741B !important;
                border: 1px solid #CBD5E0 !important;
                padding: 2px 8px !important;
                font-weight: 700 !important;
            }

            /* Bloques de código (st.code) en Modo Claro */
            [data-testid="stCodeBlock"],
            [data-testid="stCodeBlock"] pre {
                background-color: #F8FAFC !important;
                border: 1px solid #CBD5E0 !important;
                border-radius: 8px !important;
            }
            [data-testid="stCodeBlock"] code,
            [data-testid="stCodeBlock"] span {
                background-color: transparent !important;
                color: #1A202C !important;
                border: none !important;
            }

            /* Botones de enlace (st.link_button de Discord) en Modo Claro */
            .stLinkButton a,
            [data-testid="stLinkButton"] a {
                background-color: #FFFFFF !important;
                color: #1A202C !important;
                border: 1px solid #CBD5E0 !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                text-decoration: none !important;
            }
            .stLinkButton a:hover,
            [data-testid="stLinkButton"] a:hover {
                background-color: #EDF2F7 !important;
                border-color: #9E741B !important;
                color: #9E741B !important;
            }

            /* Contenedores con borde (Tarjetas / Cards generales) */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: var(--bg-card) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05) !important;
                padding: 4px;
            }

            /* Títulos y Encabezados */
            h1, h2, h3, h4, h5, h6 {
                color: #0F172A !important;
                font-weight: 700 !important;
            }
            .main-title {
                color: var(--accent-gold) !important;
                text-shadow: none !important;
            }

            /* Párrafos, textos y markdown */
            p, span, label, div {
                color: var(--text-main);
            }
            .stCaption, [data-testid="stCaptionContainer"] {
                color: var(--text-secondary) !important;
            }

            /* ==============================================================
               INPUTS, TEXTAREA Y CONTENEDOR DE CONTRASEÑA (OJO)
               ============================================================== */
            /* Envoltorio raíz de todo el input (incluye el botón del ojo) */
            [data-testid="stTextInputRootElement"],
            div[data-baseweb="input"],
            div[data-baseweb="base-input"],
            .stTextArea div[data-baseweb="textarea"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CBD5E0 !important;
                border-radius: 8px !important;
                overflow: hidden !important;
            }

            [data-testid="stTextInputRootElement"]:focus-within,
            div[data-baseweb="input"]:focus-within,
            .stTextArea div[data-baseweb="textarea"]:focus-within {
                border-color: var(--accent-gold) !important;
                box-shadow: 0 0 0 1px var(--accent-gold) !important;
            }

            /* Campo de texto interno */
            [data-testid="stTextInputField"],
            .stTextInput input,
            .stTextArea textarea {
                background-color: transparent !important;
                color: #1A202C !important;
                border: none !important;
            }

            /* Botón del OJO de la contraseña y sus iconos (CERO FONDO NEGRO) */
            [data-testid="stTextInputRootElement"] button,
            div[data-baseweb="input"] button,
            div[data-baseweb="base-input"] button {
                background: transparent !important;
                background-color: transparent !important;
                border: none !important;
                cursor: pointer !important;
                color: #4A5568 !important;
            }

            [data-testid="stTextInputRootElement"] button:hover {
                background-color: #F1F5F9 !important;
                color: #1A202C !important;
            }

            [data-testid="stTextInputRootElement"] button svg,
            [data-testid="stTextInputRootElement"] button span,
            div[data-baseweb="input"] button svg,
            div[data-baseweb="input"] button span {
                color: #4A5568 !important;
                fill: #4A5568 !important;
            }

            /* ==============================================================
               PUNTOS Y OPCIONES DE RADIO (st.radio)
               ============================================================== */
            [data-testid="stRadio"] label,
            [data-testid="stRadioOption"] {
                color: #1A202C !important;
                cursor: pointer !important;
            }

            [data-testid="stRadioOption"] * {
                color: #1A202C !important;
            }

            /* Círculo exterior NO seleccionado (Fondo blanco, borde gris claro) */
            [data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child,
            [data-testid="stRadio"] [data-baseweb="radio"] > div:first-of-type {
                background-color: #FFFFFF !important;
                border: 2px solid #CBD5E0 !important;
                transition: border-color 0.2s ease, background-color 0.2s ease !important;
            }

            /* Hover sobre el círculo exterior */
            [data-testid="stRadio"] label[data-testid="stRadioOption"]:hover > div > div:first-child {
                border-color: var(--accent-gold) !important;
                background-color: #F8FAFC !important;
            }

            /* Círculo exterior SELECCIONADO (Aro dorado) */
            [data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child,
            [data-testid="stRadio"] label[data-testid="stRadioOption"] [aria-checked="true"] > div:first-child,
            [data-testid="stRadio"] input:checked + div {
                background-color: var(--accent-gold) !important;
                border-color: var(--accent-gold) !important;
            }

            /* Punto interior blanco en la opción seleccionada */
            [data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div,
            [data-testid="stRadio"] label[data-testid="stRadioOption"] [aria-checked="true"] > div:first-child > div,
            [data-testid="stRadio"] input:checked + div > div {
                background-color: #FFFFFF !important;
            }

            /* ==============================================================
               CHECKBOXES (CASILLAS DE TAREAS)
               ============================================================== */
            [data-testid="stCheckbox"] label * {
                color: #1A202C !important;
            }
            [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
                background-color: #FFFFFF !important;
                border: 2px solid #CBD5E0 !important;
                border-radius: 5px !important;
            }
            [data-testid="stCheckbox"] input:checked + div,
            [data-testid="stCheckbox"] [data-checked="true"] > div:first-child {
                background-color: var(--accent-gold) !important;
                border-color: var(--accent-gold) !important;
            }
            [data-testid="stCheckbox"] svg {
                stroke: #FFFFFF !important;
                fill: #FFFFFF !important;
            }

            /* ==============================================================
               SELECTBOX Y MENÚS DESPLEGABLES (DROPDOWNS)
               ============================================================== */
            .stSelectbox div[data-baseweb="select"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CBD5E0 !important;
                border-radius: 8px !important;
            }
            .stSelectbox div[data-baseweb="select"] * {
                color: #1A202C !important;
            }

            /* Menú desplegable flotante (Popover) */
            div[data-baseweb="popover"],
            ul[role="listbox"],
            div[data-baseweb="menu"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CBD5E0 !important;
                border-radius: 8px !important;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
            }
            li[role="option"],
            div[data-baseweb="menu"] li {
                background-color: #FFFFFF !important;
                color: #1A202C !important;
            }
            li[role="option"]:hover,
            li[aria-selected="true"],
            div[data-baseweb="menu"] li:hover {
                background-color: #F1F5F9 !important;
                color: #0F172A !important;
            }

            /* ==============================================================
               SUBIDOR DE ARCHIVOS (FILE UPLOADER)
               ============================================================== */
            [data-testid="stFileUploader"] {
                background-color: #FFFFFF !important;
                border: 2px dashed #CBD5E0 !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }
            [data-testid="stFileUploader"] * {
                color: #1A202C !important;
            }
            [data-testid="stFileUploader"] section {
                background-color: #F8FAFC !important;
            }
            [data-testid="stFileUploader"] button {
                background-color: #FFFFFF !important;
                color: #1A202C !important;
                border: 1px solid #CBD5E0 !important;
            }

            /* ==============================================================
               MÉTRICAS, BOTONES Y DETALLES
               ============================================================== */
            [data-testid="stMetricValue"] {
                color: var(--accent-gold) !important;
                font-weight: bold !important;
            }
            [data-testid="stMetricLabel"] {
                color: var(--text-secondary) !important;
            }

            /* Botones primarios */
            .stButton>button[kind="primary"] {
                background: linear-gradient(135deg, #C89B3C, #A67C1E) !important;
                color: #FFFFFF !important;
                border: none !important;
                font-weight: 600 !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 6px rgba(166, 124, 30, 0.3) !important;
            }
            .stButton>button[kind="primary"]:hover {
                background: linear-gradient(135deg, #B58A2B, #8C6514) !important;
            }

            /* Botones secundarios */
            .stButton>button[kind="secondary"] {
                background-color: #FFFFFF !important;
                color: #2D3748 !important;
                border: 1px solid #CBD5E0 !important;
                border-radius: 8px !important;
            }
            .stButton>button[kind="secondary"]:hover {
                background-color: #EDF2F7 !important;
                border-color: #A0AEC0 !important;
            }

            /* Expanders */
            [data-testid="stExpander"] {
                background-color: #FFFFFF !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 10px !important;
            }
            [data-testid="stExpander"] * {
                color: #1A202C !important;
            }

            hr {
                border-color: #E2E8F0 !important;
            }
        </style>
        """
    else:
        return """
        <style>
            /* ==============================================================
               MODO OSCURO (HEXTECH JUNGLE DARK THEME)
               ============================================================== */
            :root {
                --bg-main: #070C12;
                --bg-card: #0E1622;
                --bg-sidebar: #0A1018;
                --text-main: #E2E8F0;
                --text-secondary: #94A3B8;
                --border-color: #1E2D3D;
                --accent-gold: #C89B3C;
                --accent-gold-hover: #E4BE65;
                --accent-blue: #0AC8B9;
            }

            /* Fondo general de la app */
            .stApp {
                background-color: var(--bg-main) !important;
                color: var(--text-main) !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            /* Header */
            header[data-testid="stHeader"] {
                background-color: rgba(7, 12, 18, 0.85) !important;
            }

            /* Barra lateral (Sidebar) */
            section[data-testid="stSidebar"] {
                background-color: var(--bg-sidebar) !important;
                border-right: 1px solid var(--border-color) !important;
            }
            section[data-testid="stSidebar"] * {
                color: var(--text-main);
            }
            section[data-testid="stSidebar"] .stCaption,
            section[data-testid="stSidebar"] p[data-testid="stCaptionContainer"],
            section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
                color: var(--text-secondary) !important;
            }

            /* Tarjetas / Contenedores dentro del Sidebar */
            section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #0E1622 !important;
                border: 1px solid #1E2D3D !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
                border-radius: 10px !important;
                padding: 6px !important;
            }

            /* Código inline (los tags `riot_tag` y `perez1473` en Modo Oscuro) */
            code {
                background-color: #142232 !important;
                color: #E4BE65 !important;
                padding: 2px 8px !important;
                border-radius: 6px !important;
                border: 1px solid #233A52 !important;
                font-weight: 600 !important;
                font-size: 0.9em !important;
            }

            section[data-testid="stSidebar"] code {
                background-color: #142232 !important;
                color: #E4BE65 !important;
                border: 1px solid #233A52 !important;
                padding: 2px 8px !important;
                font-weight: 700 !important;
            }

            /* Bloques de código (st.code) en Modo Oscuro */
            [data-testid="stCodeBlock"],
            [data-testid="stCodeBlock"] pre {
                background-color: #0E1622 !important;
                border: 1px solid #1E2D3D !important;
                border-radius: 8px !important;
            }
            [data-testid="stCodeBlock"] code,
            [data-testid="stCodeBlock"] span {
                background-color: transparent !important;
                color: #E2E8F0 !important;
                border: none !important;
            }

            /* Botones de enlace (st.link_button de Discord) en Modo Oscuro */
            .stLinkButton a,
            [data-testid="stLinkButton"] a {
                background-color: #142232 !important;
                color: #E2E8F0 !important;
                border: 1px solid #233A52 !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                text-decoration: none !important;
            }
            .stLinkButton a:hover,
            [data-testid="stLinkButton"] a:hover {
                background-color: #1B2F44 !important;
                border-color: #C89B3C !important;
                color: #C89B3C !important;
            }

            /* Contenedores con borde (Tarjetas / Cards generales) */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: var(--bg-card) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
                padding: 4px;
            }

            /* Títulos y Encabezados */
            h1, h2, h3, h4, h5, h6 {
                color: #F8FAFC !important;
                font-weight: 700 !important;
            }
            .main-title {
                color: var(--accent-gold) !important;
                text-shadow: 0 0 12px rgba(200, 155, 60, 0.35) !important;
            }

            /* Párrafos, textos y markdown */
            p, span, label, div {
                color: var(--text-main);
            }
            .stCaption, [data-testid="stCaptionContainer"] {
                color: var(--text-secondary) !important;
            }

            /* ==============================================================
               INPUTS, TEXTAREA Y CONTENEDOR DE CONTRASEÑA (OJO)
               ============================================================== */
            /* Envoltorio raíz de todo el input */
            [data-testid="stTextInputRootElement"],
            div[data-baseweb="input"],
            div[data-baseweb="base-input"],
            .stTextArea div[data-baseweb="textarea"] {
                background-color: #121E2C !important;
                border: 1px solid #233A52 !important;
                border-radius: 8px !important;
                overflow: hidden !important;
            }

            [data-testid="stTextInputRootElement"]:focus-within,
            div[data-baseweb="input"]:focus-within,
            .stTextArea div[data-baseweb="textarea"]:focus-within {
                border-color: var(--accent-gold) !important;
                box-shadow: 0 0 0 1px var(--accent-gold) !important;
            }

            /* Campo de texto interno */
            [data-testid="stTextInputField"],
            .stTextInput input,
            .stTextArea textarea {
                background-color: transparent !important;
                color: #F8FAFC !important;
                border: none !important;
            }

            /* Botón del OJO de la contraseña y sus iconos */
            [data-testid="stTextInputRootElement"] button,
            div[data-baseweb="input"] button,
            div[data-baseweb="base-input"] button {
                background: transparent !important;
                background-color: transparent !important;
                border: none !important;
                cursor: pointer !important;
                color: #94A3B8 !important;
            }

            [data-testid="stTextInputRootElement"] button:hover {
                background-color: #1A283A !important;
                color: #F8FAFC !important;
            }

            [data-testid="stTextInputRootElement"] button svg,
            [data-testid="stTextInputRootElement"] button span,
            div[data-baseweb="input"] button svg,
            div[data-baseweb="input"] button span {
                color: #94A3B8 !important;
                fill: #94A3B8 !important;
            }

            /* ==============================================================
               PUNTOS Y OPCIONES DE RADIO (st.radio)
               ============================================================== */
            [data-testid="stRadio"] label,
            [data-testid="stRadioOption"] {
                color: #CBD5E0 !important;
                cursor: pointer !important;
            }

            [data-testid="stRadioOption"] * {
                color: #CBD5E0 !important;
            }

            /* Círculo exterior NO seleccionado */
            [data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child,
            [data-testid="stRadio"] [data-baseweb="radio"] > div:first-of-type {
                background-color: #121E2C !important;
                border: 2px solid #233A52 !important;
                transition: border-color 0.2s ease, background-color 0.2s ease !important;
            }

            /* Hover sobre el círculo exterior */
            [data-testid="stRadio"] label[data-testid="stRadioOption"]:hover > div > div:first-child {
                border-color: var(--accent-gold) !important;
                background-color: #1A283A !important;
            }

            /* Círculo exterior SELECCIONADO (Aro dorado) */
            [data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child,
            [data-testid="stRadio"] label[data-testid="stRadioOption"] [aria-checked="true"] > div:first-child,
            [data-testid="stRadio"] input:checked + div {
                background-color: var(--accent-gold) !important;
                border-color: var(--accent-gold) !important;
            }

            /* Punto interior oscuro/negro en la opción seleccionada */
            [data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div,
            [data-testid="stRadio"] label[data-testid="stRadioOption"] [aria-checked="true"] > div:first-child > div,
            [data-testid="stRadio"] input:checked + div > div {
                background-color: #070C12 !important;
            }

            /* ==============================================================
               CHECKBOXES (CASILLAS DE TAREAS)
               ============================================================== */
            [data-testid="stCheckbox"] label * {
                color: #E2E8F0 !important;
            }
            [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
                background-color: #121E2C !important;
                border: 2px solid #233A52 !important;
                border-radius: 5px !important;
            }
            [data-testid="stCheckbox"] input:checked + div,
            [data-testid="stCheckbox"] [data-checked="true"] > div:first-child {
                background-color: var(--accent-gold) !important;
                border-color: var(--accent-gold) !important;
            }
            [data-testid="stCheckbox"] svg {
                stroke: #070C12 !important;
                fill: #070C12 !important;
            }

            /* ==============================================================
               SELECTBOX Y MENÚS DESPLEGABLES (DROPDOWNS)
               ============================================================== */
            .stSelectbox div[data-baseweb="select"] {
                background-color: #121E2C !important;
                border: 1px solid #233A52 !important;
                border-radius: 8px !important;
            }
            .stSelectbox div[data-baseweb="select"] * {
                color: #F8FAFC !important;
            }

            /* Menú desplegable flotante */
            div[data-baseweb="popover"],
            ul[role="listbox"],
            div[data-baseweb="menu"] {
                background-color: #0E1622 !important;
                border: 1px solid #1E2D3D !important;
                border-radius: 8px !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
            }
            li[role="option"],
            div[data-baseweb="menu"] li {
                background-color: #0E1622 !important;
                color: #E2E8F0 !important;
            }
            li[role="option"]:hover,
            li[aria-selected="true"],
            div[data-baseweb="menu"] li:hover {
                background-color: #1A283A !important;
                color: var(--accent-gold) !important;
            }

            /* ==============================================================
               SUBIDOR DE ARCHIVOS (FILE UPLOADER)
               ============================================================== */
            [data-testid="stFileUploader"] {
                background-color: #0E1622 !important;
                border: 2px dashed #1E2D3D !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }
            [data-testid="stFileUploader"] * {
                color: #E2E8F0 !important;
            }
            [data-testid="stFileUploader"] section {
                background-color: #121E2C !important;
            }
            [data-testid="stFileUploader"] button {
                background-color: #142232 !important;
                color: #E2E8F0 !important;
                border: 1px solid #233A52 !important;
            }

            /* ==============================================================
               MÉTRICAS, BOTONES Y DETALLES
               ============================================================== */
            [data-testid="stMetricValue"] {
                color: var(--accent-gold) !important;
                font-weight: bold !important;
            }
            [data-testid="stMetricLabel"] {
                color: var(--text-secondary) !important;
            }

            /* Botones primarios */
            .stButton>button[kind="primary"] {
                background: linear-gradient(135deg, #C89B3C, #8C6514) !important;
                color: #070C12 !important;
                font-weight: 700 !important;
                border: none !important;
                border-radius: 8px !important;
                box-shadow: 0 0 10px rgba(200, 155, 60, 0.3) !important;
            }
            .stButton>button[kind="primary"]:hover {
                background: linear-gradient(135deg, #E4BE65, #A67C1E) !important;
                color: #000000 !important;
            }

            /* Botones secundarios */
            .stButton>button[kind="secondary"] {
                background-color: #142232 !important;
                color: #E2E8F0 !important;
                border: 1px solid #233A52 !important;
                border-radius: 8px !important;
            }
            .stButton>button[kind="secondary"]:hover {
                background-color: #1B2F44 !important;
                border-color: #C89B3C !important;
            }

            /* Expanders */
            [data-testid="stExpander"] {
                background-color: #0E1622 !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 10px !important;
            }
            [data-testid="stExpander"] * {
                color: #E2E8F0 !important;
            }

            hr {
                border-color: #1E2D3D !important;
            }
        </style>
        """

def render_theme_toggle():
    """Renderiza el botón fácil para alternar entre Modo Claro y Modo Oscuro."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    
    current_theme = st.session_state["theme"]
    
    if current_theme == "dark":
        btn_label = "☀️ Cambiar a Modo Claro"
        next_theme = "light"
    else:
        btn_label = "🌙 Cambiar a Modo Oscuro"
        next_theme = "dark"
        
    if st.button(btn_label, key="toggle_theme_btn", use_container_width=True):
        st.session_state["theme"] = next_theme
        st.rerun()
