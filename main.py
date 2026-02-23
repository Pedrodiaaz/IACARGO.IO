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
    
    .stDetails, [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important; 
        padding: 5px; margin-bottom: 15px; color: white !important;
    }
    
    .notif-item {
        background: #f1f5f9; border-left: 4px solid #2563eb;
        padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9em; color: #1e293b !important;
    }

    .stButton > button, .stDownloadButton > button { 
        border-radius: 12px !important; 
        transition: all 0.3s ease !important; 
    }

    div.stButton > button[kind="primary"], 
    .stForm div.stButton > button {
        background-color: #2563eb !important; 
        color: white !important;
        border: none !important; 
        font-weight: bold !important;
        width: 100% !important; 
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }

    .p-card {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px; transition: transform 0.3s ease;
    }
    .p-card:hover { transform: translateY(-5px); border-color: #60a5fa; }

    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB, ARCHIVO_USUARIOS, ARCHIVO_PAPELERA, ARCHIVO_NOTIF = "inventario_logistica.csv", "usuarios_iacargo.csv", "papelera_iacargo.csv", "notificaciones_iac.csv"

def calcular_monto(valor, tipo, aplica_reempaque=False):
    monto = (valor * TARIFA_AEREO_KG) if tipo == "Aéreo" else (valor * TARIFA_MARITIMO_FT3) if tipo == "Marítimo" else (valor * 5.0)
    return monto + COSTO_REEMPAQUE_FIJO if aplica_reempaque else monto

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
for key, val in [('inventario', cargar_datos(ARCHIVO_DB)), ('usuarios', cargar_datos(ARCHIVO_USUARIOS)), ('notificaciones', cargar_datos(ARCHIVO_NOTIF)), ('usuario_identificado', None), ('landing_vista', True)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 3. DASHBOARDS ---

# (La función render_admin_dashboard se mantiene igual a tu código previo, solo incluimos la llamada correcta)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    # Buscador de paquetes (REESTABLECIDO)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    
    if not mis_p:
        st.info("No se encontraron paquetes asociados a tu cuenta.")
    else:
        busq = st.text_input("🔍 Buscar en mis paquetes (ID o Estado):", placeholder="Ej: IAC-123456")
        if busq:
            mis_p = [p for p in mis_p if busq.lower() in str(p.get('ID_Barra','')).lower() or busq.lower() in str(p.get('Estado','')).lower()]

        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0))
                abo = float(p.get('Abonado', 0.0))
                perc = (abo / tot * 100) if tot > 0 else 0
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                
                # Visualización de Card Avanzada (REESTABLECIDA)
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
                        {f'<div style="text-align:right;"><small style="color:#4ade80;">📦 Reempaque</small><div style="font-size:12px; font-weight:bold; color:white;">OPTIMIZADO</div></div>' if p.get('Reempaque') else ''}
                    </div>
                    <div style="margin-top: 15px; display: flex; justify-content: space-between; font-size: 13px;">
                        <span style="color:white;">Pagado: <b style="color:#4ade80;">${abo:.2f}</b></span>
                        <span style="color:white;">Pendiente: <b style="color:#f87171;">${(tot-abo):.2f}</b></span>
                    </div>
                    <div style="width: 100%; background-color: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; margin-top: 8px; overflow: hidden; display: flex;">
                        <div style="width: {perc}%; background: linear-gradient(90deg, #22c55e, #4ade80); height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    u = st.session_state.usuario_identificado
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        # Sistema de Notificaciones dinámico (REESTABLECIDO)
        mías = [n for n in st.session_state.notificaciones if n['para'] in [u['correo'], 'admin' if u['rol'] == 'admin' else '']]
        with st.popover("🔔"):
            if mías:
                for n in mías[:5]: st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
                if st.button("Limpiar avisos"):
                    st.session_state.notificaciones = [n for n in st.session_state.notificaciones if n['para'] != u['correo']]
                    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF); st.rerun()
            else: st.write("Sin avisos nuevos.")
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- LÓGICA DE CONTROL ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:80px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p style="font-size:20px;">"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary"):
                        if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            with t2:
                with st.form("signup"):
                    n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta", type="primary"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Cuenta creada!"); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin":
        # Aquí invoco tu función de admin previa para no duplicar código en esta respuesta
        from __main__ import render_admin_dashboard
        render_admin_dashboard() 
    else:
        render_client_dashboard()
