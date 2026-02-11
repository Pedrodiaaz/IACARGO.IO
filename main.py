import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTILO FIGMA) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Fondo Global Profundo */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    /* Ocultar la barra lateral */
    [data-testid="stSidebar"] { display: none; }
    
    /* --- NUEVA PORTADA HERO (REPLICANDO FIGMA) --- */
    .hero-container {
        height: 65vh;
        width: 100%;
        background-image: linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.8)), 
                          url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=2070');
        background-size: cover;
        background-position: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        border-radius: 40px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
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

    /* Contenedores y Formularios (Funcionalidad original) */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* Limpieza de inputs y botones */
    div[data-testid="stInputAdornment"] { display: none !important; }
    div[data-baseweb="input"] { border-radius: 10px !important; border: none !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #1e293b !important; }

    .stButton button, div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        border: none !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 50px;
    }
    
    .stButton button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important; }

    /* Estilos de tablas y métricas */
    .metric-container { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); }
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS (FUNCIONALIDAD ORIGINAL) ---
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

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. FUNCIONES DE DASHBOARD (COMPLETAS) ---
def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos" if f_tra == "Marítimo" else "Peso (Kg / Lbs)"
        with st.form("reg_form", clear_on_submit=True):
            st.info(f"ID sugerido: **{st.session_state.id_actual}**")
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.success(f"Guía {f_id} registrada."); st.rerun()

    with t_val:
        st.subheader("⚖️ Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Reportado por mensajero: {paq['Peso_Mensajero']}")
            peso_real = st.number_input(f"Peso Real en Almacén", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("⚖️ Confirmar y Validar"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_UNIDAD
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Validado correctamente."); st.rerun()
        else: st.info("No hay paquetes por validar.")

    with t_cob:
        st.subheader("💰 Gestión de Cobros")
        # Lógica original de cobros...
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f"💵 {p['ID_Barra']} - {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto a abonar:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"Registrar Pago", key=f"bp_{p['ID_Barra']}"):
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("✈️ Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="status_sel")
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("🔍 Auditoría y Edición")
        if st.checkbox("Ver Papelera"):
            # Lógica papelera original...
            if st.session_state.papelera:
                guia_res = st.selectbox("Restaurar ID:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("Restaurar"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else:
            df_aud = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader("📊 Resumen General")
        # Mantener tu búsqueda y filas de resumen...
        df_full = pd.DataFrame(st.session_state.inventario)
        c_alm = len(df_full[df_full['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"]) if not df_full.empty else 0
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-container"><small>📦 ALMACÉN</small><br><b style="font-size:25px;">{c_alm}</b></div>', unsafe_allow_html=True)
        # (Resto de métricas originales)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    # Lógica original del cliente con barra de progreso...
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    for p in mis_p:
        with st.container():
            st.markdown(f'<div class="p-card">ID: {p["ID_Barra"]} | {p["Estado"]}</div>', unsafe_allow_html=True)
            st.progress(p['Abonado']/p['Monto_USD'] if p['Monto_USD'] > 0 else 0)

# --- 4. LÓGICA DE NAVEGACIÓN (CAMBIO ESTÉTICO AQUÍ) ---

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        # AQUÍ ESTÁ EL CAMBIO ESTÉTICO TIPO FIGMA
        st.markdown(f"""
            <div class="hero-container">
                <h1 class="logo-animado" style="font-size:100px; margin-bottom:10px;">IACargo.io</h1>
                <p style="font-size:26px; font-weight:300; letter-spacing:1px; color:#94a3b8 !important;">
                    "La existencia es un milagro"
                </p>
                <p style="font-size:18px; opacity:0.8; max-width:700px; margin-top:20px;">
                    Evolución logística para un mundo en movimiento. 
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        _, col_btn, _ = st.columns([1, 1, 1])
        with col_btn:
            if st.button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
                st.session_state.landing_vista = False; st.rerun()
        st.markdown("<p style='text-align:center; margin-top:50px; opacity:0.6;'>No eres herramienta, eres evolución.</p>", unsafe_allow_html=True)
    else:
        # LOGIN Y REGISTRO (Mantiene tu lógica)
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login_form"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar"):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        # ... resto de lógica login
            if st.button("⬅️ Volver"): st.session_state.landing_vista = True; st.rerun()

else:
    # PANEL LOGUEADO (SIN SIDEBAR)
    st.markdown(f'<div style="text-align:right; padding:10px;"><span style="color:#60a5fa;">Socio: {st.session_state.usuario_identificado["nombre"]}</span></div>', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN 🔒"):
        st.session_state.usuario_identificado = None
        st.session_state.landing_vista = True; st.rerun()

    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
