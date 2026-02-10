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
    /* Fondo y Base */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    /* Logo Animado */
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

    /* Contenedores */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* ==========================================================
       ESTILO BOTONES PERMANENTES (LOGIN Y REGISTRO)
       ========================================================== */
    /* Apuntamos a los botones que están dentro de formularios (Login y Registro) */
    div[data-testid="stForm"] button, 
    button[kind="secondaryFormSubmit"],
    button[kind="primaryFormSubmit"] {
        background-color: #2563eb !important; /* Azul firme */
        color: white !important;              /* Letras blancas */
        border: 1px solid #3b82f6 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        transition: none !important;          /* Elimina cualquier transición */
        box-shadow: none !important;          /* Elimina sombras */
    }

    /* Forzamos que al pasar el cursor NO cambie nada */
    div[data-testid="stForm"] button:hover,
    div[data-testid="stForm"] button:active,
    div[data-testid="stForm"] button:focus {
        background-color: #2563eb !important; /* Mismo azul */
        color: white !important;              /* Mismas letras */
        border: 1px solid #3b82f6 !important;
        transform: none !important;           /* Evita movimientos */
        box-shadow: none !important;
    }

    /* Estatus y Resumen */
    .header-resumen {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        margin: 10px 0;
        border-left: 6px solid #60a5fa;
    }
    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 15px;
        border-bottom: 2px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
        border-radius: 4px;
    }
    .resumen-id { font-weight: 800; color: #2563eb; width: 150px; }
    .resumen-cliente { flex-grow: 1; font-weight: 500; font-size: 1.1em; }
    .resumen-data { font-weight: 700; color: #475569; text-align: right; }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def generar_id_unico():
    caracteres = string.ascii_uppercase + string.digits
    return f"IAC-{''.join(random.choices(caracteres, k=6))}"

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): 
    pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()

# --- 3. FUNCIONES ADMIN ---
def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"], key="admin_reg_tra")
        label_din = "Pies Cúbicos" if f_tra == "Marítimo" else "Peso Mensajero (Kg)"
        with st.form("reg_form", clear_on_submit=True):
            st.info(f"ID sugerido: **{st.session_state.id_actual}**")
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            
            # BOTÓN AZUL PERMANENTE
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.success(f"Guía {f_id} registrada."); st.rerun()

    # Resto de secciones (se mantienen iguales para estabilidad)
    with t_val:
        st.subheader("⚖️ Validación")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in pendientes])
            peso_real = st.number_input("Peso Real", min_value=0.0)
            if st.button("⚖️ Confirmar Validación"):
                paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
                paq.update({'Peso_Almacen': peso_real, 'Validado': True, 'Monto_USD': peso_real * PRECIO_POR_UNIDAD})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader("💰 Cobros")
        for p in [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']:
            with st.expander(f"💵 {p['ID_Barra']} - {p['Cliente']}"):
                m = st.number_input("Abono", 0.0, key=f"c_{p['ID_Barra']}")
                if st.button("Pagar", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] += m
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("✈️ Estados")
        if st.session_state.inventario:
            sel = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            est = st.selectbox("Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel: p["Estado"] = est
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_res:
        st.subheader("📊 Resumen")
        for est_k, est_l in [("RECIBIDO ALMACEN PRINCIPAL", "📦 ALMACÉN"), ("EN TRANSITO", "✈️ TRÁNSITO"), ("ENTREGADO", "✅ ENTREGADO")]:
            df_f = [p for p in st.session_state.inventario if p['Estado'] == est_k]
            st.markdown(f'<div class="header-resumen">{est_l} ({len(df_f)})</div>', unsafe_allow_html=True)
            for r in df_f:
                icon = "✈️" if r.get('Tipo_Traslado') == "Aéreo" else "🚢"
                st.markdown(f'<div class="resumen-row"><div class="resumen-id">{icon} {r["ID_Barra"]}</div><div class="resumen-cliente">{r["Cliente"]}</div><div class="resumen-data">${r["Abonado"]:.2f}</div></div>', unsafe_allow_html=True)

# --- 4. FUNCIÓN CLIENTE ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if p.get('Correo', '').lower() == u['correo'].lower()]
    if not mis_p: st.info("Sin paquetes.")
    else:
        for p in mis_p:
            tot = p['Monto_USD']; abo = p['Abonado']
            icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
            st.markdown(f'<div class="p-card"><b>{icon} {p["ID_Barra"]}</b> - {p["Estado"]}</div>', unsafe_allow_html=True)
            st.progress(abo/tot if tot > 0 else 0)

# --- 5. LOGICA LOGIN ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png")
    else: st.markdown('<h1 class="logo-animado">IACargo.io</h1>', unsafe_allow_html=True)
    if st.session_state.usuario_identificado:
        if st.button("Salir"): st.session_state.usuario_identificado = None; st.rerun()
    st.caption("“La existencia es un milagro” | “No eres herramienta, eres evolución”")

if st.session_state.usuario_identificado is None:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registro"])
        with t1:
            with st.form("login"):
                le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                # BOTÓN AZUL PERMANENTE
                if st.form_submit_button("Entrar", use_container_width=True):
                    if le == "admin" and lp == "admin123":
                        st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                    u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                    if u: st.session_state.usuario_identificado = u; st.rerun()
                    else: st.error("Error")
        with t2:
            with st.form("signup"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.rerun()
else:
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
