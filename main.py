import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

# --- TARIFAS ACTUALIZADAS (Manteniendo coherencia con lo pactado) ---
TARIFA_AEREO_KG = 6.0    # Solo por peso
TARIFA_MARITIMO_FT3 = 15.0  # Solo por dimensión

st.markdown("""
    <style>
    /* Fondo Global */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    /* --- LOGO ANIMADO IACARGO --- */
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

    /* --- ESTILO DE TARJETAS DE USUARIO (Técnico y Limpio) --- */
    .user-card {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }
    .user-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(96, 165, 250, 0.5);
    }

    /* --- BARRA DE PROGRESO PERSONALIZADA --- */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #60a5fa, #a78bfa) !important;
    }

    /* --- EXPANDERS ESTÁTICOS (Corrección anterior) --- */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stExpander"] summary { color: white !important; background-color: transparent !important; }
    [data-testid="stExpander"] summary:hover, [data-testid="stExpander"] summary:focus {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
    }

    /* Botones, Inputs y Notificaciones (Fondo blanco para lectura) */
    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    div[data-testid="stPopoverContent"] { background-color: #ffffff !important; border-radius: 15px !important; }
    div[data-testid="stPopoverContent"] * { color: #1e293b !important; }

    .welcome-text { 
        background: linear-gradient(90deg, #ffffff, #60a5fa); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 800; font-size: 42px; margin-bottom: 20px; 
    }
    
    h1, h2, h3, p, span, label { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo).to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

def obtener_icono_transporte(tipo):
    return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")

# --- Session State ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []

# --- 3. DASHBOARD CLIENTE (RESTAURADO) ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]} 👋</div>', unsafe_allow_html=True)
    st.markdown("### Mis Envíos en curso")
    
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    
    if not mis_p:
        st.info("Actualmente no tienes paquetes registrados. ¡Contáctanos para tu próximo envío!")
    else:
        col1, col2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (col1 if i % 2 == 0 else col2):
                tot = float(p.get('Monto_USD', 0.0))
                abo = float(p.get('Abonado', 0.0))
                progreso = (abo / tot) if tot > 0 else 0
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                
                # Tarjeta Visual Evolucionada
                st.markdown(f"""
                <div class="user-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 24px;">{icon} <b>{p['ID_Barra']}</b></span>
                        <span style="background: #2563eb; padding: 4px 12px; border-radius: 20px; font-size: 12px;">{p['Estado']}</span>
                    </div>
                    <hr style="opacity: 0.1; margin: 15px 0;">
                    <p style="margin: 0; font-size: 14px; opacity: 0.8;">Tipo: {p.get('Tipo_Traslado', 'N/A')}</p>
                    <p style="margin: 5px 0; font-size: 18px;"><b>Total: ${tot:.2f}</b></p>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; margin-top: 10px;">
                        <span>Pagado: ${abo:.2f}</span>
                        <span>Restante: ${(tot-abo):.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(progreso, 1.0))
                st.markdown("<br>", unsafe_allow_html=True)

# --- 4. DASHBOARD ADMIN (Lógica Compacta) ---
def render_admin_dashboard():
    st.markdown('<div class="welcome-text">Panel Administrativo</div>', unsafe_allow_html=True)
    t_reg, t_val, t_cob, t_res = st.tabs(["📥 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "📊 RESUMEN"])
    
    with t_reg:
        with st.form("admin_reg"):
            f_id = st.text_input("ID Tracking", value=generar_id_unico())
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo"])
            f_pes = st.number_input("Peso/Volumen inicial", min_value=0.0)
            if st.form_submit_button("REGISTRAR", type="primary"):
                monto = calcular_monto(f_pes, f_tra)
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto, "Estado": "RECIBIDO ALMACEN", "Pago": "PENDIENTE", "Tipo_Traslado": f_tra, "Abonado": 0.0}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Registrado"); st.rerun()

    with t_val:
        pends = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pends:
            sel = st.selectbox("Guía a validar", [p["ID_Barra"] for p in pends])
            val = st.number_input("Valor Real Almacén", min_value=0.0)
            if st.button("VALIDAR PESO/VOL"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel:
                        p["Peso_Almacen"] = val
                        p["Validado"] = True
                        p["Monto_USD"] = calcular_monto(val, p["Tipo_Traslado"])
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
    
    with t_cob:
        for p in st.session_state.inventario:
            if p['Abonado'] < p['Monto_USD']:
                with st.expander(f"{p['ID_Barra']} - {p['Cliente']}"):
                    abo = st.number_input("Abono", 0.0, float(p['Monto_USD']-p['Abonado']), key=p['ID_Barra'])
                    if st.button("PAGAR", key="btn"+p['ID_Barra']):
                        p['Abonado'] += abo
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_res:
        st.subheader("Búsqueda y Estados")
        busq = st.text_input("🔍 Buscar por código o cliente")
        df = pd.DataFrame(st.session_state.inventario)
        if not df.empty and busq:
            df = df[df['ID_Barra'].str.contains(busq, case=False) | df['Cliente'].str.contains(busq, case=False)]
        st.dataframe(df, use_container_width=True)

# --- NAVEGACIÓN Y LOGIN ---
def render_header():
    c1, c2, c3 = st.columns([7, 1, 2])
    with c1: st.markdown('<div class="logo-animado" style="font-size:35px;">IACargo.io</div>', unsafe_allow_html=True)
    with c2:
        with st.popover("🔔"):
            st.write("Notificaciones")
            for n in st.session_state.notificaciones: st.write(f"• {n}")
    with c3:
        if st.button("SALIR", type="primary", use_container_width=True):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p style="font-size:20px;">"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA EVOLUTIVO", type="primary", use_container_width=True):
            st.session_state.landing_vista = False; st.rerun()
    else:
        # Formulario de Acceso
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<h2 style="text-align:center;">Acceso Privado</h2>', unsafe_allow_html=True)
            tab_in, tab_reg = st.tabs(["Login", "Registro"])
            with tab_in:
                with st.form("L"):
                    u_email = st.text_input("Email")
                    u_pass = st.text_input("Password", type="password")
                    if st.form_submit_button("ENTRAR", type="primary"):
                        if u_email == "admin" and u_pass == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}
                            st.rerun()
                        user = next((u for u in st.session_state.usuarios if u['correo'] == u_email.lower().strip() and u['password'] == hash_password(u_pass)), None)
                        if user: st.session_state.usuario_identificado = user; st.rerun()
            with tab_reg:
                with st.form("R"):
                    n_nom = st.text_input("Nombre Completo")
                    n_ema = st.text_input("Correo Electrónico")
                    n_pas = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("CREAR CUENTA"):
                        st.session_state.usuarios.append({"nombre": n_nom, "correo": n_ema.lower().strip(), "password": hash_password(n_pas), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Cuenta Creada!"); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
