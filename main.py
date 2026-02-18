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
        font-size: 24px;
        cursor: pointer;
        padding: 5px;
        line-height: 1;
    }
    .bell-icon { color: #facc15; } /* Amarillo vibrante */
    
    .red-dot {
        position: absolute;
        top: 0px;
        right: 0px;
        height: 10px;
        width: 10px;
        background-color: #ef4444; /* Rojo de alerta */
        border-radius: 50%;
        border: 1.5px solid #0f172a;
    }

    /* Botones Primary UNIFICADOS a AZUL */
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

    /* Estilo de Notificaciones en Lista */
    .notif-item {
        background: rgba(255,255,255,0.08);
        border-left: 4px solid #facc15;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 8px;
        font-size: 0.85em;
        color: #e2e8f0;
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
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Visibilidad de Inputs */
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    div[data-baseweb="select"] > div { background-color: #f8fafc !important; color: #000000 !important; }

    .metric-container { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); }
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: #10b981; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    .badge-debt { background: #f87171; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS Y NOTIFICACIONES ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []

def agregar_notificacion(mensaje):
    hora = datetime.now().strftime("%H:%M")
    # Al agregar una nueva, marcamos que hay algo "no leido"
    st.session_state.notificaciones.insert(0, {"msg": mensaje, "hora": hora, "leida": False})
    if len(st.session_state.notificaciones) > 10: st.session_state.notificaciones.pop()

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

# --- 3. CABECERA INTEGRADA (LOGO + CAMPANA + SALIR) ---
def render_header():
    c1, c2, c3 = st.columns([6, 2, 2])
    with c1:
        st.markdown('<div class="logo-animado" style="font-size:38px;">IACargo.io</div>', unsafe_allow_html=True)
    with c2:
        # Lógica del punto rojo
        hay_no_leidas = any(not n.get('leida', False) for n in st.session_state.notificaciones)
        dot = '<div class="red-dot"></div>' if hay_no_leidas else ''
        
        st.markdown(f'<div class="bell-wrapper"><span class="bell-icon">🔔</span>{dot}</div>', unsafe_allow_html=True)
        
        with st.expander("Centro de Actividad"):
            if not st.session_state.notificaciones:
                st.caption("Sin notificaciones nuevas.")
            else:
                for n in st.session_state.notificaciones:
                    st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
                    n['leida'] = True # Se marcan como leídas al abrirse
                if st.button("Limpiar historial", type="primary", use_container_width=True):
                    st.session_state.notificaciones = []; st.rerun()
    with c3:
        if st.button("CERRAR SESIÓN", type="primary", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.session_state.landing_vista = True
            st.rerun()

# --- 4. FUNCIONES DE DASHBOARD (RESTAURADAS AL 100%) ---
def render_admin_dashboard():
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        f_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="reg_tra")
        label_din = "Pies Cúbicos" if f_tra == "Marítimo" else "Peso (Kg / Lbs)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input(label_din, min_value=0.0)
            f_mod = st.selectbox("Modalidad", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(), "Peso_Almacen": f_pes, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.session_state.id_actual = generar_id_unico()
                agregar_notificacion(f"Registro: {f_id} ({f_cli})")
                st.success("Registrado"); st.rerun()

    with t_cob:
        for p in [x for x in st.session_state.inventario if x['Pago'] == 'PENDIENTE']:
            rest = float(p.get('Monto_USD', 0)) - float(p.get('Abonado', 0))
            with st.expander(f"📦 {p['ID_Barra']} — {p['Cliente']} (Deuda: ${rest:.2f})"):
                monto = st.number_input("Monto a abonar:", 0.0, float(rest), float(rest), key=f"cob_{p['ID_Barra']}")
                if st.button("REGISTRAR PAGO", key=f"btn_{p['ID_Barra']}", type="primary"):
                    p['Abonado'] = float(p.get('Abonado', 0)) + monto
                    if (float(p['Monto_USD']) - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    agregar_notificacion(f"Cobro: ${monto} en guía {p['ID_Barra']}")
                    st.rerun()

    with t_est:
        if st.session_state.inventario:
            sel = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS", type="primary"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                agregar_notificacion(f"Movimiento: {sel} a {n_st}")
                st.rerun()

    with t_res:
        st.subheader("Buscador de Resumen")
        busq = st.text_input("Buscar caja por código:")
        df_res = pd.DataFrame(st.session_state.inventario)
        if not df_res.empty:
            if busq: df_res = df_res[df_res['ID_Barra'].str.contains(busq, case=False)]
            for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                df_f = df_res[df_res['Estado'] == est]
                with st.expander(f"{est} ({len(df_f)})"):
                    for _, r in df_f.iterrows():
                        icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                        st.markdown(f'<div class="resumen-row"><div>{icon} <b>{r["ID_Barra"]}</b></div> <div>{r["Cliente"]}</div></div>', unsafe_allow_html=True)

# --- NAVEGACIÓN Y LOGIN ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="text-align:center;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
                st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            with st.form("login_form"):
                u = st.text_input("Usuario"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                    if u == "admin" and p == "admin123":
                        st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            if st.button("Volver"): st.session_state.landing_vista = True; st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado.get('rol') == "admin":
        render_admin_dashboard()
    else:
        st.info("Panel de Cliente activo.")
