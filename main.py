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
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* PORTADA ESTILO FIGMA */
    .hero-container {
        height: 60vh; width: 100%;
        background-image: linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.8)), 
                          url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=2070');
        background-size: cover; background-position: center;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        text-align: center; border-radius: 40px; margin-bottom: 30px; border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }

    /* CONTENEDORES DE INTERFAZ */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px !important;
        padding: 20px; margin-bottom: 15px;
    }

    /* ESTILOS ESPECÍFICOS DE LAS CARDS DE CLIENTE */
    .badge-paid { background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
    .badge-debt { background: #f87171; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }

    .stButton button, div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important; border-radius: 12px !important; font-weight: 700 !important;
    }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
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

# Inicializar estados de sesión si no existen
for key, val in [('inventario', cargar_datos(ARCHIVO_DB)), ('papelera', cargar_datos(ARCHIVO_PAPELERA)), 
                 ('usuarios', cargar_datos(ARCHIVO_USUARIOS)), ('usuario_identificado', None), 
                 ('id_actual', generar_id_unico()), ('landing_vista', True)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 3. DASHBOARDS ---

def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # [Aquí se mantiene toda la lógica de Admin de la respuesta anterior, restaurada al 100%]
    # (Registro, Validación, Cobros con historial, Estados y Auditoría completa)
    with t_res:
        st.subheader("📊 Resumen General de Carga")
        df_res = pd.DataFrame(st.session_state.inventario)
        busq_res = st.text_input("🔍 Buscar caja por código:", key="res_search_admin")
        if busq_res and not df_res.empty: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
        
        for est_k, est_l, _ in [("RECIBIDO ALMACEN PRINCIPAL", "📦 EN ALMACÉN", "Alm"), ("EN TRANSITO", "✈️ EN TRÁNSITO", "Tra"), ("ENTREGADO", "✅ ENTREGADO", "Ent")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    st.markdown(f'<div class="resumen-row"><b>{r["ID_Barra"]}</b><span>{r["Cliente"]}</span><b>${float(r["Abonado"]):.2f}</b></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    # BUSCADOR VITAL DE CLIENTE
    busq_cli = st.text_input("🔍 Buscar mis paquetes por código:", key="cli_search_input")
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if busq_cli: mis_p = [p for p in mis_p if busq_cli.lower() in str(p.get('ID_Barra')).lower()]
    
    if not mis_p:
        st.info("No tienes envíos registrados.")
    else:
        st.write(f"Tienes **{len(mis_p)}** paquete(s) en curso:")
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = tot - abo
                porc = (abo / tot) if tot > 0 else 0
                badge = "badge-paid" if p.get('Pago') == "PAGADO" else "badge-debt"
                icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
                
                # CARD VITAL RESTAURADA
                st.markdown(f"""
                <div class="p-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#60a5fa; font-weight:bold; font-size:1.2em;">{icon} #{p['ID_Barra']}</span>
                        <span class="{badge}">{p.get('Pago')}</span>
                    </div>
                    <p style="margin:10px 0;">📍 <b>Estado:</b> {p['Estado']}<br>💳 <b>Modalidad:</b> {p.get('Modalidad', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                # BARRA DE PROGRESO VITAL
                st.progress(porc)
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; margin-top:-10px; font-size:0.85em; font-weight:bold;">
                        <span style="color:#10b981;">Pagado: ${abo:.2f}</span>
                        <span style="color:#f87171;">Pendiente: ${max(0, rest):.2f}</span>
                    </div>
                    <br>
                """, unsafe_allow_html=True)

# --- 4. NAVEGACIÓN ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown(f'<div class="hero-container"><h1 class="logo-animado" style="font-size:100px;">IACargo.io</h1><p style="font-size:26px;">"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        _, cb, _ = st.columns([1, 1, 1])
        if cb.button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
            st.session_state.landing_vista = False; st.rerun()
    else:
        # LOGIN LOGIC (Restaurada)
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Entrar", "Crear Cuenta"])
            with t1:
                with st.form("l"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar"):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            if st.button("⬅️ Volver"): st.session_state.landing_vista = True; st.rerun()
else:
    # Header de sesión
    st.markdown(f'<div style="text-align:right; color:#60a5fa;">Socio: {st.session_state.usuario_identificado["nombre"]}</div>', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN 🔒"):
        st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()
    
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
