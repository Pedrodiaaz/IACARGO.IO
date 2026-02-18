import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    /* Fondo Global */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    /* ESTILO DE LA CAMPANA AMARILLA CON PUNTO ROJO */
    .bell-wrapper {
        position: relative;
        display: inline-block;
        font-size: 26px;
        cursor: pointer;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px;
        border-radius: 50%;
        line-height: 1;
        border: 1px solid rgba(255, 255, 0, 0.3);
    }
    .bell-icon { color: #facc15; } /* Amarillo */
    
    .red-dot {
        position: absolute;
        top: 2px;
        right: 2px;
        height: 12px;
        width: 12px;
        background-color: #ef4444; /* Rojo Alerta */
        border-radius: 50%;
        border: 2px solid #0f172a;
    }

    /* Botones Primary UNIFICADOS */
    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 10px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }

    .notif-item {
        background: rgba(255,255,255,0.08);
        border-left: 4px solid #facc15;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 8px;
        font-size: 0.9em;
    }

    .logo-animado {
        font-style: italic !important;
        font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        animation: pulse 2.5s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
    }
    
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }

    .metric-container { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); }
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []
if 'ver_notificaciones' not in st.session_state: st.session_state.ver_notificaciones = False

def agregar_notificacion(mensaje):
    hora = datetime.now().strftime("%H:%M")
    st.session_state.notificaciones.insert(0, {"msg": mensaje, "hora": hora, "leida": False})
    if len(st.session_state.notificaciones) > 8: st.session_state.notificaciones.pop()

# --- (Funciones de Soporte Manteniendo Funcionalidad) ---
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

def obtener_icono_transporte(tipo):
    iconos = {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}
    return iconos.get(tipo, "📦")

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. CABECERA CON CAMPANA DINÁMICA ---
def render_header():
    c_logo, c_notif, c_exit = st.columns([6, 2, 2])
    
    with c_logo:
        st.markdown('<div class="logo-animado" style="font-size:35px;">IACargo.io</div>', unsafe_allow_html=True)
    
    with c_notif:
        # Lógica del punto rojo: si hay alguna notificación no leída
        hay_nuevas = any(not n['leida'] for n in st.session_state.notificaciones)
        dot_html = '<div class="red-dot"></div>' if hay_nuevas else ""
        
        # Simulamos el click usando un botón invisible o un expander minimalista
        st.markdown(f'''
            <div class="bell-wrapper">
                <span class="bell-icon">🔔</span>
                {dot_html}
            </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("Ver Actividad"):
            if not st.session_state.notificaciones:
                st.caption("No hay alertas.")
            else:
                for n in st.session_state.notificaciones:
                    st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
                    n['leida'] = True # Se marcan como leídas al abrir el menú
                if st.button("Limpiar todo", type="primary"):
                    st.session_state.notificaciones = []; st.rerun()

    with c_exit:
        if st.button("CERRAR SESIÓN", type="primary", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.session_state.landing_vista = True
            st.rerun()

# --- 4. DASHBOARDS (SIN ALTERACIONES FUNCIONALES) ---

def render_admin_dashboard():
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        f_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        with st.form("reg_form"):
            f_id = st.text_input("Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Cliente")
            f_pes = st.number_input("Peso/Medida", min_value=0.0)
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": "user@mail.com", "Peso_Almacen": f_pes, "Monto_USD": f_pes*5, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Abonado": 0.0, "Tipo_Traslado": f_tra}
                st.session_state.inventario.append(nuevo)
                agregar_notificacion(f"Nuevo registro: {f_id}")
                st.rerun()

    with t_cob:
        for p in [x for x in st.session_state.inventario if x['Pago'] == 'PENDIENTE']:
            with st.expander(f"📦 {p['ID_Barra']} - {p['Cliente']}"):
                if st.button(f"PAGAR TOTAL ${p['Monto_USD']}", key=p['ID_Barra'], type="primary"):
                    p['Pago'] = 'PAGADO'; p['Abonado'] = p['Monto_USD']
                    agregar_notificacion(f"Pago completo: {p['ID_Barra']}")
                    st.rerun()

    with t_est:
        if st.session_state.inventario:
            guia = st.selectbox("Guía", [p['ID_Barra'] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estatus", ["EN TRANSITO", "ENTREGADO"])
            if st.button("ACTUALIZAR", type="primary"):
                for p in st.session_state.inventario:
                    if p['ID_Barra'] == guia: p['Estado'] = n_st
                agregar_notificacion(f"Estatus {guia}: {n_st}")
                st.rerun()
    
    with t_res:
        st.subheader("Resumen General")
        busq = st.text_input("🔍 Buscar caja por código:")
        df_res = pd.DataFrame(st.session_state.inventario)
        if not df_res.empty:
            if busq: df_res = df_res[df_res['ID_Barra'].str.contains(busq, case=False)]
            st.dataframe(df_res[['ID_Barra', 'Cliente', 'Estado', 'Pago']], use_container_width=True)

# --- NAVEGACIÓN ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="text-align:center;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1></div>', unsafe_allow_html=True)
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
                st.session_state.landing_vista = False; st.rerun()
    else:
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                if u == "admin": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin":
        render_admin_dashboard()
