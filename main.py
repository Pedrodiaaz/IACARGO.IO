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
    
    /* --- CONTENEDORES --- */
    .stDetails, [data-testid="stExpander"], .stTabs, .stForm {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important; 
        padding: 15px; 
        margin-bottom: 15px; 
        color: white !important;
    }

    /* --- BOTONES UNIFICADOS --- */
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
    
    .stButton > button:hover {
        background-color: #3b82f6 !important; 
        transform: translateY(-2px) !important;
    }

    /* --- LOGO Y TEXTO --- */
    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    /* --- INPUTS --- */
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; }
    
    /* --- BARRA DE PROGRESO PERSONALIZADA --- */
    .progress-container { width: 100%; background-color: #334155; border-radius: 10px; margin: 10px 0; }
    .progress-bar { height: 12px; background: linear-gradient(90deg, #22c55e, #10b981); border-radius: 10px; transition: width 0.5s ease; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIONES DE APOYO ---
def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Historial_Pagos' in df.columns:
                df['Historial_Pagos'] = df['Historial_Pagos'].apply(lambda x: eval(x) if isinstance(x, str) else [])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

# --- INITIALIZE STATE ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos("inventario.csv")
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()

# --- 3. DASHBOARD ADMINISTRADOR ---
def render_admin_dashboard():
    st.markdown('<h2 class="logo-animado">Panel de Control Evolución</h2>', unsafe_allow_html=True)
    
    t_reg, t_val, t_cob, t_est, t_aud, t_res = st.tabs([
        "📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "🚚 ESTADOS", "🛠️ AUDITORÍA", "📊 RESUMEN"
    ])

    # --- TAB: REGISTRO (CON REEMPAQUE) ---
    with t_reg:
        st.subheader("Entrada de Mercancía")
        col_a, col_b = st.columns(2)
        with col_a:
            f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Nacional"])
            f_cli = st.text_input("Cliente")
        with col_b:
            f_cor = st.text_input("Correo")
            f_reempaque = st.toggle("¿Requiere Reempaque?", help="Optimización de espacio para proveedores")

        with st.form("reg_form"):
            f_id = st.text_input("ID Tracking", value=st.session_state.id_actual)
            label_din = "Pies Cúbicos (ft³)" if f_tra == "Marítimo" else "Peso Inicial (Kg)"
            f_pes = st.number_input(label_din, min_value=0.0)
            f_mod = st.selectbox("Modalidad", ["Pago Completo", "Pago en Cuotas", "Cobro Destino"])
            
            if st.form_submit_button("REGISTRAR PAQUETE"):
                nuevo = {
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(),
                    "Peso_Original": f_pes, "Peso_Final": 0.0, "Validado": False,
                    "Monto_Total": calcular_monto(f_pes, f_tra), "Estado": "EN ALMACÉN",
                    "Abonado": 0.0, "Tipo": f_tra, "Reempaque": f_reempaque,
                    "Historial_Pagos": [], "Modalidad": f_mod, "Fecha": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, "inventario.csv")
                st.session_state.id_actual = generar_id_unico()
                st.rerun()

    # --- TAB: VALIDACIÓN ---
    with t_val:
        st.subheader("Verificación de Integridad")
        pendientes = [p for p in st.session_state.inventario if not p['Validado']]
        if not pendientes: st.info("No hay paquetes pendientes por validar.")
        for p in pendientes:
            with st.expander(f"Validar: {p['ID_Barra']} - {p['Cliente']}"):
                v_real = st.number_input(f"Peso/Dimensión Real", value=float(p['Peso_Original']), key=f"v_{p['ID_Barra']}")
                if v_real != p['Peso_Original']:
                    st.warning(f"⚠️ Variación detectada. Original: {p['Peso_Original']} | Nuevo: {v_real}")
                if st.button("CONFIRMAR VALIDACIÓN", key=f"btn_v_{p['ID_Barra']}"):
                    p['Peso_Final'] = v_real
                    p['Validado'] = True
                    p['Monto_Total'] = calcular_monto(v_real, p['Tipo'])
                    guardar_datos(st.session_state.inventario, "inventario.csv")
                    st.rerun()

    # --- TAB: COBROS (CON BUSCADOR Y BARRA DE PROGRESO) ---
    with t_cob:
        st.subheader("Gestión Financiera")
        busq_c = st.text_input("🔍 Buscar por Guía o Cliente", key="busq_cobros")
        
        for p in st.session_state.inventario:
            if busq_c.lower() in p['ID_Barra'].lower() or busq_c.lower() in p['Cliente'].lower():
                total = p['Monto_Total']
                abonado = p['Abonado']
                porcentaje = min((abonado / total), 1.0) * 100 if total > 0 else 0
                
                with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']} (${abonado:.2f} / ${total:.2f})"):
                    # Barra de progreso visual
                    st.markdown(f"""
                        <div class="progress-container"><div class="progress-bar" style="width: {porcentaje}%;"></div></div>
                        <p style='text-align:right; font-size:12px;'>{porcentaje:.1f}% Pagado</p>
                    """, unsafe_allow_html=True)
                    
                    m_pago = st.number_input("Monto a abonar", min_value=0.0, max_value=total-abonado, key=f"pago_{p['ID_Barra']}")
                    if st.button("REGISTRAR ABONO", key=f"btn_p_{p['ID_Barra']}"):
                        p['Abonado'] += m_pago
                        p['Historial_Pagos'].append({"fecha": datetime.now().strftime("%d/%m/%Y"), "monto": m_pago})
                        guardar_datos(st.session_state.inventario, "inventario.csv")
                        st.rerun()

    # --- TAB: ESTADOS ---
    with t_est:
        st.subheader("Seguimiento de Logística")
        for p in st.session_state.inventario:
            col1, col2 = st.columns([2, 1])
            col1.write(f"**{p['ID_Barra']}** - Actual: `{p['Estado']}`")
            nuevo_est = col2.selectbox("Cambiar a:", ["EN ALMACÉN", "EN TRÁNSITO", "ENTREGADO"], key=f"est_{p['ID_Barra']}")
            if nuevo_est != p['Estado']:
                if st.button("Actualizar", key=f"upd_{p['ID_Barra']}"):
                    p['Estado'] = nuevo_est
                    guardar_datos(st.session_state.inventario, "inventario.csv"); st.rerun()

    # --- TAB: AUDITORÍA / EDICIÓN (RECUPERADA) ---
    with t_aud:
        st.subheader("🛠️ Auditoría y Modificación de Datos")
        busq_aud = st.text_input("🔍 Buscar guía para editar:", key="busq_aud")
        for i, p in enumerate(st.session_state.inventario):
            if busq_aud.lower() in p['ID_Barra'].lower():
                with st.expander(f"EDITAR: {p['ID_Barra']}"):
                    new_cli = st.text_input("Nombre Cliente", value=p['Cliente'], key=f"edit_c_{i}")
                    new_cor = st.text_input("Correo", value=p['Correo'], key=f"edit_m_{i}")
                    if st.button("GUARDAR CAMBIOS", key=f"save_{i}"):
                        p['Cliente'] = new_cli
                        p['Correo'] = new_cor
                        guardar_datos(st.session_state.inventario, "inventario.csv")
                        st.success("Actualizado")

    # --- TAB: RESUMEN (Buscador por código y 3 estados) ---
    with t_res:
        st.subheader("📦 Estado General del Inventario")
        busq_r = st.text_input("🔍 Buscar código de caja:", key="busq_res")
        
        estados = ["EN ALMACÉN", "EN TRÁNSITO", "ENTREGADO"]
        cols_est = st.columns(3)
        
        for idx, est in enumerate(estados):
            with cols_est[idx]:
                st.markdown(f"### {est}")
                items = [p for p in st.session_state.inventario if p['Estado'] == est]
                if busq_r:
                    items = [p for p in items if busq_r.lower() in p['ID_Barra'].lower()]
                for it in items:
                    st.markdown(f"**{it['ID_Barra']}**\n{it['Cliente']}")
                    st.divider()

# --- 4. HEADER Y LOGIN ---
def render_header():
    c1, c2 = st.columns([8, 2])
    c1.markdown('<h1 class="logo-animado">IACargo.io</h1>', unsafe_allow_html=True)
    if c2.button("CERRAR SESIÓN"):
        st.session_state.usuario_identificado = None
        st.rerun()

if st.session_state.usuario_identificado is None:
    st.markdown('<div style="text-align:center; margin-top:100px;">', unsafe_allow_html=True)
    st.markdown('<h1 class="logo-animado" style="font-size:60px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write('"La existencia es un milagro"')
    if st.button("ENTRAR AL SISTEMA"):
        st.session_state.usuario_identificado = {"rol": "admin"}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    render_header()
    render_admin_dashboard()
