import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

TARIFA_AEREO_KG = 6.0    
TARIFA_MARITIMO_FT3 = 15.0  
COSTO_REEMPAQUE_FIJO = 5.0

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Contenedores visuales */
    .stDetails, [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important; 
        padding: 5px; margin-bottom: 15px; color: white !important;
    }

    /* Notificaciones y Popover */
    .red-dot {
        position: absolute; top: -2px; right: -2px; height: 12px; width: 12px;
        background-color: #ef4444; border-radius: 50%; border: 2px solid #0f172a; z-index: 10;
    }
    .notif-item {
        background: #f1f5f9; border-left: 4px solid #2563eb;
        padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9em; color: #1e293b !important;
    }

    /* Botones */
    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #2563eb !important; color: white !important;
        border-radius: 12px !important; font-weight: bold !important;
        width: 100% !important; padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }

    /* Cards del Cliente */
    .p-card {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px; transition: transform 0.3s ease;
    }
    .p-card:hover { transform: translateY(-5px); border-color: #60a5fa; }
    
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_NOTIF = "notificaciones_iac.csv"

def calcular_monto(valor, tipo, aplica_reempaque=False):
    monto = (valor * TARIFA_AEREO_KG) if tipo == "Aéreo" else (valor * TARIFA_MARITIMO_FT3) if tipo == "Marítimo" else (valor * 5.0)
    if aplica_reempaque: monto += COSTO_REEMPAQUE_FIJO
    return monto

def registrar_notificacion(para, msg):
    nueva = {"hora": datetime.now().strftime("%H:%M"), "para": para, "msg": msg}
    st.session_state.notificaciones.insert(0, nueva)
    pd.DataFrame(st.session_state.notificaciones).to_csv(ARCHIVO_NOTIF, index=False)

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Historial_Pagos' in df.columns: df['Historial_Pagos'] = df['Historial_Pagos'].apply(lambda x: eval(x) if isinstance(x, str) else [])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)
def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def obtener_icono_transporte(tipo): return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")

# --- Session State ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = cargar_datos(ARCHIVO_NOTIF)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. INTERFAZ DE USUARIO (CLIENTE) ---

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    # Filtro de paquetes del usuario actual
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    
    if not mis_p:
        st.info("Actualmente no tienes paquetes registrados en nuestro sistema.")
    else:
        # Buscador de paquetes (Recuperado)
        busq = st.text_input("🔍 Buscar paquete por ID:", placeholder="Ej: IAC-123456")
        if busq:
            mis_p = [p for p in mis_p if busq.lower() in str(p.get('ID_Barra', '')).lower()]

        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0))
                abo = float(p.get('Abonado', 0.0))
                pendiente = tot - abo
                perc = (abo / tot * 100) if tot > 0 else 0
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                
                # Render de la Card
                st.markdown(f"""
                <div class="p-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color:#60a5fa; font-weight:800; font-size: 22px;">{icon} #{p['ID_Barra']}</span>
                        <span style="background:rgba(96,165,250,0.2); color:#60a5fa; padding: 5px 12px; border-radius:12px; font-size:12px; font-weight:bold;">{p['Estado']}</span>
                    </div>
                    <hr style="opacity:0.1; margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <small style="opacity:0.6; color:white;">Total a pagar</small>
                            <div style="font-size: 24px; font-weight: 800; color:white;">${tot:.2f}</div>
                        </div>
                        {f'<div style="text-align:right;"><small style="color:#4ade80;">📦 Reempaque</small><div style="font-size:14px; font-weight:bold; color:white;">Incluido</div></div>' if p.get('Reempaque') else ''}
                    </div>
                    <div style="margin-top: 15px; display: flex; justify-content: space-between; font-size: 14px;">
                        <span style="color:white;">Pagado: <b style="color:#4ade80;">${abo:.2f}</b></span>
                        <span style="color:white;">Pendiente: <b style="color:#f87171;">${pendiente:.2f}</b></span>
                    </div>
                    <div style="width: 100%; background-color: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; margin-top: 8px; overflow: hidden;">
                        <div style="width: {perc}%; background: linear-gradient(90deg, #22c55e, #4ade80); height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- HEADER (Recuperado) ---
def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    u = st.session_state.usuario_identificado
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        target = u['rol'] if u['rol'] == 'admin' else u['correo']
        mías = [n for n in st.session_state.notificaciones if n['para'] == target]
        with st.popover("🔔"):
            if mías:
                st.markdown(f'<div style="color:black;">Tienes {len(mías)} avisos nuevos:</div>', unsafe_allow_html=True)
                for n in mías[:5]: st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
                if st.button("Limpiar Notificaciones"):
                    st.session_state.notificaciones = [n for n in st.session_state.notificaciones if n['para'] != target]
                    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF); st.rerun()
            else: st.write("No hay notificaciones nuevas.")
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- BLOQUE PRINCIPAL ---
if st.session_state.usuario_identificado is None:
    # Lógica de Login/Landing... (Se mantiene igual para no romper el acceso)
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:50px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        # Formulario de login...
        with st.form("login"):
            le = st.text_input("Usuario/Correo")
            lp = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar"):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}
                    st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u:
                    st.session_state.usuario_identificado = u
                    st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin":
        # Aquí iría el render_admin_dashboard() que ya tenemos
        st.write("Panel de Administrador Activo") # (Simplificado para este bloque)
    else:
        render_client_dashboard()
