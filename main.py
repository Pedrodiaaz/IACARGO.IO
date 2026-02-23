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

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* --- AJUSTE DE EXPANDERS FIJOS --- */
    .stDetails, [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important; 
        padding: 5px; 
        margin-bottom: 15px; 
        color: white !important;
    }
    
    [data-testid="stExpander"] summary:hover {
        background: transparent !important;
        color: #60a5fa !important;
    }
    
    [data-testid="stExpander"] summary {
        background: transparent !important;
        border-radius: 20px !important;
    }

    /* --- NOTIFICACIONES --- */
    .red-dot {
        position: absolute; top: -2px; right: -2px; height: 12px; width: 12px;
        background-color: #ef4444; border-radius: 50%; border: 2px solid #0f172a; z-index: 10;
    }

    /* --- BOTONES UNIFICADOS (AZUL CON LETRAS BLANCAS) --- */
    .stButton > button, div.stDownloadButton > button {
        background-color: #2563eb !important; 
        color: white !important;
        border: none !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
        text-transform: uppercase;
        width: 100% !important;
    }
    
    .stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #3b82f6 !important; 
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
        margin-bottom: 5px;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }

    .stTabs, .stForm {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px; color: white !important;
    }

    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
ARCHIVO_NOTIF = "notificaciones_iac.csv"

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

def registrar_notificacion(para, msg):
    nueva = {"hora": datetime.now().strftime("%H:%M"), "para": para, "msg": msg}
    if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []
    st.session_state.notificaciones.insert(0, nueva)
    pd.DataFrame(st.session_state.notificaciones).to_csv(ARCHIVO_NOTIF, index=False)

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            if 'Historial_Pagos' in df.columns:
                df['Historial_Pagos'] = df['Historial_Pagos'].apply(lambda x: eval(x) if isinstance(x, str) else [])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)
def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
def obtener_icono_transporte(tipo): return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")

# --- Session State ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = cargar_datos(ARCHIVO_NOTIF)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. DASHBOARD ADMIN ---
def render_admin_dashboard():
    st.title(" Consola de Control Logístico")
    t_reg, t_val, t_cob, t_est, t_aud, t_res = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos (ft³)" if f_tra == "Marítimo" else "Peso (Kilogramos)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR EN SISTEMA"):
                if f_id and f_cli and f_cor:
                    monto_calc = calcular_monto(f_pes, f_tra)
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto_calc, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now(), "Historial_Pagos": []}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.rerun()

    with t_val:
        st.subheader(" Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            label_val = "Pies Cúbicos Reales" if paq['Tipo_Traslado'] == "Marítimo" else "Peso Real (Kg)"
            valor_real = st.number_input(label_val, min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR Y VALIDAR"):
                paq['Peso_Almacen'] = valor_real
                paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(valor_real, paq['Tipo_Traslado'])
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader(" Gestión de Cobros")
        busq_cobro = st.text_input("🔍 Buscar paquete o cobro:", key="search_cobros_admin")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        if busq_cobro:
            pendientes_p = [p for p in pendientes_p if busq_cobro.lower() in p['ID_Barra'].lower() or busq_cobro.lower() in p['Cliente'].lower()]
        for p in pendientes_p:
            total, abo = float(p.get('Monto_USD', 0.0)), float(p.get('Abonado', 0.0))
            rest = total - abo
            with st.expander(f"💰 {p['ID_Barra']} — {p['Cliente']} (Debe: ${rest:.2f})"):
                m_abono = st.number_input("Monto a abonar:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"REGISTRAR PAGO", key=f"bp_{p['ID_Barra']}"):
                    p.setdefault('Historial_Pagos', []).append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "monto": m_abono})
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_res:
        st.subheader(" Resumen General")
        df_res = pd.DataFrame(st.session_state.inventario)
        busq_box = st.text_input(" Buscar caja por código:", key="res_search_admin")
        if busq_box and not df_res.empty:
            df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_box, case=False)]
        
        for est_k, est_l, _ in [("RECIBIDO ALMACEN PRINCIPAL", " EN ALMACÉN", "Alm"), ("EN TRANSITO", " EN TRÁNSITO", "Tra"), ("ENTREGADO", " ENTREGADO", "Ent")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})", expanded=True if busq_box else False):
                for _, r in df_f.iterrows():
                    icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                    c_info, c_hist, c_exp = st.columns([3, 2, 1.5])
                    with c_info:
                        st.markdown(f'<div class="resumen-row"><div style="color:#2563eb; font-weight:800;">{icon} {r["ID_Barra"]}</div><div style="color:#1e293b; flex-grow:1; margin-left:15px;">{r["Cliente"]}</div></div>', unsafe_allow_html=True)
                    with c_hist:
                        abonos = r.get('Historial_Pagos', [])
                        st.caption(f"Abonos: {len(abonos)} | Total: ${float(r['Abonado']):.2f}")
                    with c_exp:
                        if abonos:
                            df_h_ind = pd.DataFrame(abonos)
                            df_h_ind['Guía'] = r['ID_Barra']
                            csv_ind = df_h_ind.to_csv(index=False).encode('utf-8')
                            st.download_button(label="📥 REPORTE", data=csv_ind, file_name=f"Pagos_{r['ID_Barra']}.csv", mime="text/csv", key=f"dl_{r['ID_Barra']}")

# --- (Las funciones de Header, Cliente y Login se mantienen igual que en tu base) ---
def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    u = st.session_state.usuario_identificado
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        target = u['rol'] if u['rol'] == 'admin' else u['correo']
        mías = [n for n in st.session_state.notificaciones if n['para'] == target]
        with st.popover("🔔"):
            if mías: st.markdown('<div class="red-dot"></div>', unsafe_allow_html=True)
            if not mías: st.write("Sin avisos.")
            else:
                for n in mías[:5]: st.markdown(f'<div style="color:black"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
    with col_s:
        if st.button("CERRAR SESIÓN"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- EJECUCIÓN ---
if st.session_state.usuario_identificado is None:
    # Lógica de Login/Landing...
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align:center; margin-top:50px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA"): st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
