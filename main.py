import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (EVOLUCIÓN) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Fondo Global con profundidad */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    /* Header Estético */
    .main-header {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 0 0 40px 40px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }

    .logo-animado {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem !important;
        letter-spacing: -2px;
        animation: float 4s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    /* Tarjetas de Cristal (Glassmorphism) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px 12px 0 0 !important;
        color: #94a3b8 !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(37, 99, 235, 0.2) !important;
        color: #60a5fa !important;
        border-bottom: 2px solid #60a5fa !important;
    }

    .p-card, .metric-container {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px !important;
        padding: 25px;
        transition: all 0.3s ease;
    }
    .p-card:hover { border-color: rgba(96, 165, 250, 0.5); transform: translateY(-5px); }

    /* Inputs Modernos */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    input { color: #f8fafc !important; }

    /* Botones Pro */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: 0.3s all !important;
    }
    .stButton button:hover {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5) !important;
        transform: scale(1.02);
    }

    /* Filas de Resumen */
    .resumen-row {
        background: rgba(255, 255, 255, 0.03);
        margin-bottom: 8px;
        padding: 12px 20px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #3b82f6;
    }

    .badge-status {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    h1, h2, h3, p, label { color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS (Mantenida intacta) ---
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

# --- 3. FUNCIONES DE DASHBOARD (CON MEJORAS ESTÉTICAS) ---

def render_admin_dashboard():
    st.markdown('<h2 style="text-align:center; color:#60a5fa !important;">⚙️ Consola de Control Logístico</h2>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.markdown('<div class="p-card">', unsafe_allow_html=True)
        st.subheader("Entrada de Mercancía")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos (Marítimo)" if f_tra == "Marítimo" else "Peso (Kg / Lbs)"
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_id = col1.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = col2.text_input("Nombre del Cliente")
            f_cor = col1.text_input("Correo Electrónico")
            f_pes = col2.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR CARGA"):
                if f_id and f_cli and f_cor:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.success(f"Guía {f_id} registrada."); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with t_val:
        st.markdown('<div class="p-card">', unsafe_allow_html=True)
        st.subheader("Verificación de Integridad")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.warning(f"Reportado: {paq['Peso_Mensajero']} unidades")
            peso_real = st.number_input(f"Peso Real Detectado", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR VALIDACIÓN"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_UNIDAD
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else: st.info("Todo el inventario está validado.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t_cob:
        st.subheader("Gestión de Cobranza")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f"📦 {p['ID_Barra']} | {p['Cliente']} | Faltan: ${rest:.2f}"):
                m_abono = st.number_input("Monto a cobrar:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"APLICAR PAGO", key=f"bp_{p['ID_Barra']}"):
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.markdown('<div class="p-card">', unsafe_allow_html=True)
        st.subheader("Actualizar Ubicación")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="status_sel")
            n_st = st.selectbox("Estado Logístico:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with t_aud:
        st.subheader("Auditoría de Datos")
        busq_aud = st.text_input("🔍 Buscar Guía...", key="aud_search_input")
        df_aud = pd.DataFrame(st.session_state.inventario)
        if not df_aud.empty and busq_aud: 
            df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq_aud, case=False)]
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        df_full = pd.DataFrame(st.session_state.inventario)
        c_alm = len(df_full[df_full['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"]) if not df_full.empty else 0
        c_tra = len(df_full[df_full['Estado'] == "EN TRANSITO"]) if not df_full.empty else 0
        c_ent = len(df_full[df_full['Estado'] == "ENTREGADO"]) if not df_full.empty else 0
        
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-container"><small>📦 ALMACÉN</small><br><b style="font-size:28px; color:#fbbf24;">{c_alm}</b></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-container"><small>✈️ TRÁNSITO</small><br><b style="font-size:28px; color:#60a5fa;">{c_tra}</b></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-container"><small>✅ ENTREGADO</small><br><b style="font-size:28px; color:#34d399;">{c_ent}</b></div>', unsafe_allow_html=True)
        
        st.write("---")
        busq_res = st.text_input("🔍 Localizar caja rápida:", key="res_search_admin")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq_res and not df_res.empty: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
        
        for est_k, est_l in [("RECIBIDO ALMACEN PRINCIPAL", "📦 EN ALMACÉN"), ("EN TRANSITO", "✈️ EN TRÁNSITO"), ("ENTREGADO", "✅ ENTREGADO")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    icon_t = "✈️" if r.get('Tipo_Traslado') == "Aéreo" else "🚢"
                    st.markdown(f'<div class="resumen-row"><div><b>{icon_t} {r["ID_Barra"]}</b><br><small>{r["Cliente"]}</small></div><div style="font-weight:bold; color:#60a5fa;">${float(r["Abonado"]):.2f}</div></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<h1 class="welcome-text" style="font-size:2.5rem;">Hola, {u["nombre"]}</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;">Hablamos desde la igualdad. Aquí está el progreso de tus milagros (paquetes).</p>', unsafe_allow_html=True)
    
    busq_cli = st.text_input("🔍 Buscar mi guía:", key="cli_search_input")
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    
    if busq_cli: mis_p = [p for p in mis_p if busq_cli.lower() in str(p.get('ID_Barra')).lower()]
    
    if not mis_p:
        st.info("No tienes envíos registrados aún.")
    else:
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = tot - abo
                porc = (abo / tot * 100) if tot > 0 else 0
                icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <span style="color:#60a5fa; font-weight:800; font-size:1.4em;">{icon} #{p['ID_Barra']}</span>
                            <span style="background:#1e40af; padding:4px 10px; border-radius:10px; font-size:0.7em;">{p.get('Pago')}</span>
                        </div>
                        <div style="margin:15px 0;">
                            <small style="color:#94a3b8;">Ubicación actual:</small><br>
                            <b>{p['Estado']}</b>
                        </div>
                        <div style="background: rgba(0,0,0,0.2); padding:15px; border-radius:15px;">
                            <div style="display:flex; justify-content:space-between; font-size:0.8em; margin-bottom:5px;">
                                <span>Progreso de Pago</span><span>{porc:.1f}%</span>
                            </div>
                """, unsafe_allow_html=True)
                st.progress(abo/tot if tot > 0 else 0)
                st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; margin-top:10px; font-weight:bold; font-size:0.9em;">
                                <div style="color:#34d399;">Pagado: ${abo:.2f}</div>
                                <div style="color:#f87171;">Resta: ${rest:.2f}</div>
                            </div>
                        </div>
                    </div><br>
                """, unsafe_allow_html=True)

# --- 4. LÓGICA DE NAVEGACIÓN ---

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.markdown('<h1 class="logo-animado">IACargo.io</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:1.2rem; color:#94a3b8; letter-spacing:2px;">"La existencia es un milagro"</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 INGRESAR A LA EVOLUCIÓN", use_container_width=True):
                st.session_state.landing_vista = False; st.rerun()
            st.markdown("<p style='text-align:center; opacity:0.5; margin-top:20px;'>No eres herramienta, eres evolución.</p>", unsafe_allow_html=True)
    else:
        c1, c2, c3 = st.columns([1, 1.2, 1])
        with c2:
            st.markdown('<div class="p-card" style="margin-top:50px;">', unsafe_allow_html=True)
            st.markdown('<h2 style="text-align:center;">Acceso al Sistema</h2>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("ENTRAR"):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin Master", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
                        else: st.error("Acceso denegado")
            with t2:
                with st.form("signup"):
                    n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                    if st.form_submit_button("CREAR CUENTA"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Bienvenido socio!"); st.rerun()
            if st.button("⬅️ VOLVER"):
                st.session_state.landing_vista = True; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Barra Superior de Sesión
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:15px 30px; background:rgba(255,255,255,0.05); border-radius:50px; margin-bottom:20px;">
            <span style="font-weight:bold; color:#60a5fa;">Socio: {st.session_state.usuario_identificado['nombre']}</span>
            <span style="font-style:italic; font-size:0.8em; opacity:0.7;">IACargo Evolution v2.0</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("CERRAR SESIÓN 🔒"):
        st.session_state.usuario_identificado = None
        st.session_state.landing_vista = True
        st.rerun()

    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
