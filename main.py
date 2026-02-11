import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Fondo Global */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    /* Ocultar barra lateral */
    [data-testid="stSidebar"] { display: none; }
    
    /* Contenedor Superior Derecho (Botones alineados) */
    .header-controls {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Estilo unificado para botones de acción (Notif y Logout) */
    .stButton button, .stPopover button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.8em !important;
        text-transform: uppercase !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        transition: all 0.3s ease !important;
        padding: 8px 15px !important;
        height: auto !important;
        width: auto !important;
    }

    /* Estilo específico para el Popover de Notificaciones para que parezca un botón */
    div[data-testid="stPopover"] > button {
        width: 100% !important;
    }

    .logo-animado {
        font-style: italic !important;
        font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        animation: pulse 2.5s infinite;
        font-weight: 800;
        margin-bottom: 5px;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }

    .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
    }

    .notif-item { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 8px 0; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 20px; }
    
    /* Inputs */
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #1e293b !important; }
    
    .badge-paid { background: #10b981; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    .badge-debt { background: #f87171; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
ARCHIVO_NOTIF = "notificaciones_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []
def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

# Inicializar estados
for key, val in [('inventario', cargar_datos(ARCHIVO_DB)), ('papelera', cargar_datos(ARCHIVO_PAPELERA)), 
                 ('usuarios', cargar_datos(ARCHIVO_USUARIOS)), ('notificaciones', cargar_datos(ARCHIVO_NOTIF)),
                 ('usuario_identificado', None), ('id_actual', generar_id_unico()), ('landing_vista', True)]:
    if key not in st.session_state: st.session_state[key] = val

def registrar_notificacion(correo, id_barra, nuevo_estado):
    notif = {"Correo": correo.lower().strip(), "ID": id_barra, "Estado": nuevo_estado, "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M")}
    st.session_state.notificaciones.append(notif)
    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF)

# --- 3. COMPONENTE DE CABECERA (NOTIF + LOGOUT) ---
def render_header_controls():
    u = st.session_state.usuario_identificado
    if u:
        # Contenedor flotante para ambos botones
        st.markdown('<div class="header-controls">', unsafe_allow_html=True)
        col_n, col_l = st.columns([1, 1])
        
        with col_n:
            mis_notif = [n for n in st.session_state.notificaciones if n["Correo"] == u["correo"].lower().strip()]
            with st.popover(f"🔔 ({len(mis_notif)})"):
                st.markdown("<h4 style='color:black;'>Notificaciones</h4>", unsafe_allow_html=True)
                if not mis_notif: st.write("Sin novedades.")
                else:
                    for n in reversed(mis_notif[-5:]):
                        st.markdown(f"<div style='color:black; font-size:0.8em; border-bottom:1px solid #eee; padding:5px;'><b>{n['ID']}</b>: {n['Estado']}<br><small>{n['Fecha']}</small></div>", unsafe_allow_html=True)
        
        with col_l:
            if st.button("SALIR 🔒"):
                st.session_state.usuario_identificado = None
                st.session_state.landing_vista = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. DASHBOARDS ---
def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    # ... (El contenido de admin se mantiene igual para no alterar la lógica funcional)
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    # [Aquí iría el resto de tu lógica de admin que ya tienes construida]
    st.info("Panel administrativo activo. Use las pestañas para gestionar la carga.")

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    busq_cli = st.text_input("🔍 Buscar mis paquetes:", key="cli_search")
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    
    if not mis_p:
        st.info("No tienes envíos registrados.")
    else:
        cols = st.columns(2)
        for i, p in enumerate(mis_p):
            with cols[i % 2]:
                tot = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = tot - abo
                porc = (abo / tot) if tot > 0 else 0
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#60a5fa; font-weight:800;">📦 #{p['ID_Barra']}</span>
                            <span class="badge-paid">{p.get('Pago')}</span>
                        </div>
                        <p>📍 Estatus: {p['Estado']}</p>
                """, unsafe_allow_html=True)
                st.progress(porc)
                st.markdown(f"<small>Pendiente: ${rest:.2f}</small></div>", unsafe_allow_html=True)

# --- 5. LÓGICA DE NAVEGACIÓN ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown("<br><br><br><div style='text-align:center;'><h1 class='logo-animado' style='font-size:80px;'>IACargo.io</h1><p>\"La existencia es un milagro\"</p></div>", unsafe_allow_html=True)
        if st.button("🚀 INGRESAR AL SISTEMA"):
            st.session_state.landing_vista = False; st.rerun()
    else:
        # Pantalla de Login (simplificada para el ejemplo, usa tu lógica de tabs)
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
            with st.form("login"):
                le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                if st.form_submit_button("Entrar"):
                    if le == "admin" and lp == "admin123":
                        st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin@iacargo.io"}; st.rerun()
                    # (Aquí añadirías la lógica de búsqueda de usuario en CSV)
else:
    render_header_controls() # Llamada a los botones unificados
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
