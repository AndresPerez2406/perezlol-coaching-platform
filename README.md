# 🌲 PerezLoL Coaching Academy — League of Legends (v1.0 MVP)

<div align="center">

![Versión](https://img.shields.io/badge/Versi%C3%B3n-1.0%20(MVP%20Inicial)-orange?style=for-the-badge)
![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo%20Activo-yellow?style=for-the-badge)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Auth-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![League of Legends](https://img.shields.io/badge/League%20of%20Legends-All%20Roles-C89B3C?logo=leagueoflegends&logoColor=white)](https://www.leagueoflegends.com/)
[![Discord](https://img.shields.io/badge/Discord-perez1473-5865F2?logo=discord&logoColor=white)](https://discord.com/)

**Campus Virtual y Plataforma Web de Coaching Profesional para League of Legends**  
*Una academia multirrol diseñada para profesionalizar el coaching de esports, centralizar entrenamientos y escalar con múltiples coaches.*

[La Idea y Visión](#-la-idea-y-visión-del-proyecto) • [Estado Actual (v1.0)](#-estado-actual-del-proyecto-v10-mvp) • [Catálogo](#-catálogo-de-coaching-y-tarifas) • [Roadmap](#-roadmap-y-futuras-versiones) • [Instalación](#-instalación-y-ejecución-local)

</div>

---

> ⚠️ **AVISO: ESTA ES LA PRIMERA VERSIÓN (v1.0.0-ALPHA / MVP INICIAL)**  
> Este repositorio contiene la **primera versión funcional (Minimum Viable Product)** del campus virtual de la academia.  
> **El proyecto está en desarrollo activo y pruebas piloto:** no es un producto final de producción. Se construyó para validar el flujo de agendamiento, matriculación de estudiantes, asignación de tareas técnicas y validación de pagos P2P antes de automatizar todas las integraciones.

---

## 💡 La Idea y Visión del Proyecto

El coaching tradicional en League of Legends suele ser informal: acuerdos por mensajes directos de Discord, notas que se pierden, falta de seguimiento a largo plazo y pagos desordenados.

**PerezLoL Coaching Academy** nace con la misión de **profesionalizar la enseñanza de League of Legends** mediante un **Campus Virtual tipo Moodle**:

1. **Academia Multirrol Abierta a Múltiples Coaches:** La plataforma está diseñada para albergar entrenamientos en **todas las líneas del juego** (Top, Jungla, Mid, ADC y Support). La visión es integrar a varios coaches especializados para que cada estudiante elija su rol y mentor.
2. **Especialidad Inicial del Fundador (Rama de Jungla):** En esta primera etapa, el Coach Perez (`Discord: perez1473`) lidera la rama de **Jungla**, aplicando metodologías de macro, pathing, tracking y tempo.
3. **Seguimiento Estructurado del Alumno:** Cada estudiante tiene su propia aula virtual donde puede ver sus créditos de clases (VODs grabadas y LIVE Games en vivo), su próxima sesión en agenda y un cuaderno de tareas técnicas asignadas tras cada revisión.
4. **Pagos P2P Transparentes y Seguros:** Sistema de recarga mediante **Binance Pay (USDT)** y **Nequi (Colombia)** con subida de comprobante y acreditación directa por el coach o administrador.

---

## 📌 Estado Actual del Proyecto (v1.0 MVP)

### ✅ Lo que ya está implementado y funcionando en la v1.0:
- **Estructura Modular tipo Moodle:** Navegación centralizada en la barra lateral con módulos limpios e independientes.
- **Portal del Estudiante:**
  - Consulta de perfil con rango de invocador y Discord tag.
  - Panel de créditos activos (VOD Reviews y LIVE Games restantes).
  - Visualización de la próxima clase programada por el Coach.
  - Cuaderno de tareas/misiones técnicas con casillas interactivas de cumplimiento.
  - Tienda P2P para adquirir paquetes y subir comprobantes (Binance Pay / Nequi) con confirmación visual persistente.
  - Historial de comprobantes con estados (*Pendiente*, *Aprobado*, *Rechazado*).
  - Canal y acceso directo al Discord del Coach (`perez1473`).
- **Portal del Coach:**
  - Panel de control de alumnos con paquetes activos.
  - Agendamiento de clases simplificado: Alumno, Tipo de sesión, Fecha y Hora.
  - Validación y aprobación de pagos P2P (revisión de la captura del comprobante y acreditación inmediata de créditos al alumno).
  - Asignación de tareas técnicas personalizadas para cada estudiante.
  - Registro y matriculación administrativa de nuevos estudiantes.
- **Portal del Administrador:**
  - Auditoría básica de la academia y selector de vistas de supervisión.
- **Base de Datos y Seguridad:**
  - Esquema relacional en Supabase (PostgreSQL) con script de configuración de permisos ([`database/fix_rls.sql`](database/fix_rls.sql)) y soporte de `service_role`.

---

## 🗺️ Roadmap y Futuras Versiones

- [ ] **v1.1 — Incorporación de Múltiples Coaches por Rol:** Perfiles públicos para coaches de Top, Mid, ADC y Support, permitiendo que cada alumno elija su coach según su carril.
- [ ] **v1.2 — Pasarela de Pagos Automatizada:** Checkout automático (Stripe / Crypto Gateway) para acreditar paquetes al instante sin revisión manual de capturas.
- [ ] **v1.3 — Integración Profunda con Riot Games API:** Detección automática del historial de partidas del alumno, cálculo de KP% (Kill Participation), control de visión y estadísticas por rol en tiempo real.
- [ ] **v1.4 — Calendario y Reserva Autónoma:** Permitir que los alumnos elijan horarios disponibles directamente desde un calendario interactivo sincronizado con Google Calendar.
- [ ] **v1.5 — Videoteca VOD y Chat Integrado:** Subida de grabaciones de clases a almacenamiento en la nube privado para que el alumno pueda repasarlas cuando quiera.

---

## 🎮 Catálogo de Coaching y Tarifas (v1.0)

| Paquete | Contenido | Precio | Objetivo |
| :--- | :--- | :--- | :--- |
| **Pack Primer Coaching** | 1 LIVE Game + 3 VOD Reviews | **$14.00 USD** | ⭐ **Recomendado:** Diagnóstico en vivo y 3 semanas de pulido. |
| **Pack 4 VODs Reviews** | 4 Revisiones de Repetición | **$12.00 USD** | Análisis semanal de partidas grabadas (Ahorras $2 USD). |
| **LIVE GAME Coaching** | 1 Partida en Vivo + Review | **$5.00 USD** | Toma de decisiones en directo vía Discord. |
| **Sesión VOD Review** | 1 Análisis de Repetición (30-60m) | **$3.50 USD** | Revisión profunda de errores puntuales y tareas. |

---

## 🛠️ Stack Tecnológico

- **Frontend / Framework:** Python con [Streamlit](https://streamlit.io/) (Diseño Hextech LoL oscuro y responsivo).
- **Backend & Base de Datos:** [Supabase](https://supabase.com/) (PostgreSQL relacional, Auth y Storage).
- **Control de Versiones:** Git & GitHub.
- **Voz y Transmisión en Vivo:** Discord (`perez1473`).

---

## 📂 Estructura del Proyecto

```text
Plataforma Coaching/
├── app.py                      # Punto de entrada principal y sidebar de módulos
├── requirements.txt            # Dependencias del proyecto
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Exclusión de claves secretas y entornos virtuales
│
├── database/                   # Conexión y persistencia con Supabase
│   ├── client.py               # Singleton de conexión (soporta anon y service_role)
│   ├── operations.py           # Funciones CRUD (alumnos, paquetes, sesiones, pagos, tareas)
│   └── fix_rls.sql             # Script SQL para habilitar permisos en Supabase
│
└── views/                      # Módulos divididos por roles
    ├── login.py                # Acceso rápido por rol
    ├── student_view.py         # Módulos del alumno (Aula, Misiones, Tienda, Historial)
    ├── coach_view.py           # Módulos del coach (Gestión, Agenda, Pagos, Tareas)
    └── admin_view.py           # Auditoría y supervisión general
```

---

## ⚡ Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/AndresPerez2406/perezlol-coaching-platform.git
cd perezlol-coaching-platform
```

### 2. Crear y activar entorno virtual
```bash
# Windows:
python -m venv .venv
.\.venv\Scripts\activate

# Linux / Mac:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar librerías
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia `.env.example` a `.env`:
```bash
cp .env.example .env
```
Y añade tus credenciales de Supabase:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-publica
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key-secreta-opcional
```

### 5. Configurar permisos en Supabase
En tu panel de Supabase ➔ **SQL Editor**, ejecuta el script [`database/fix_rls.sql`](database/fix_rls.sql) para habilitar las operaciones de inserción y consulta de las tablas.

### 6. Iniciar el Campus Virtual
```bash
streamlit run app.py
```
Abre en tu navegador `http://localhost:8501`.

---

## 📞 Contacto y Admisiones

- **Academia:** PerezLoL Coaching Academy
- **Head Coach:** Perez (Especialidad: Jungla)
- **Discord Oficial:** `perez1473`
- **Juego:** League of Legends (LAS / LAN / NA)

---

<div align="center">
  <sub>PerezLoL Coaching Academy — Versión 1.0 (MVP en Desarrollo Activo) 🌲</sub>
</div>
