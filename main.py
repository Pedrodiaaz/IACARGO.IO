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
COSTO_REEMPAQUE = 5.0

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    .stDetails, [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important; 
        padding: 5px; 
        margin-bottom: 15px; 
        color: white !important;
    }
    
    .stButton > button, .stDownloadButton > button { 
        border-radius: 12px !important; 
        transition: all 0.3s ease !important; 
    }
    div.stButton > button[kind="primary"], .stForm div.stButton > button, div.stDownloadButton > button {
        background-color: #2563eb !important; color: white !important;
        border: none !important; font-weight: bold !important;
        width: 100% !important; padding: 10px 20px !important;
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
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px;
    }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
def calcular_monto(valor, tipo, reempaque_sel):
    monto_base = 0.0
    if tipo == "Aéreo": monto_base = valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": monto_base = valor * TARIFA_MARITIMO_FT3
    else: monto_base = valor * 5.0
    if reempaque_sel != "No": monto_base += COSTO_REEMPAQUE
    return monto_base

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
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos("inventario_logistica.csv")
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos("papelera_iacargo.csv")
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos("usuarios_iacargo.csv")
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = cargar_datos("notificaciones_iac.csv")
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. DASHBOARD ADMINISTRADOR ---

def render_admin_dashboard():
    st.title(" Consola de Control Logístico")
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # 1. REGISTRO
    with t_reg:
        st.subheader("Registro de Entrada")
        c1, c2 = st.columns(2)
        with c1: f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        with c2: f_reemp = st.selectbox("Servicio de Reempaque ($5)", ["No", "Small 16x12x12", "Medium 15x16x22", "Large 18x18x24", "Extra Large 22x22x22"])
        
        label_din = "Pies Cúbicos (ft³)" if f_tra == "Marítimo" else "Peso (Kilogramos)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary"):
                monto_calc = calcular_monto(f_pes, f_tra, f_reemp)
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto_calc, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Reempaque": f_reemp, "Abonado": 0.0, "Fecha_Registro": datetime.now(), "Historial_Pagos": []}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv")
                st.session_state.id_actual = generar_id_unico()
                st.rerun()

    # 2. VALIDACIÓN
    with t_val:
        st.subheader(" Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Valor Real (Kg/ft³)", value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR Y VALIDAR", type="primary"):
                paq['Peso_Almacen'] = v_real
                paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(v_real, paq['Tipo_Traslado'], paq['Reempaque'])
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    # 3. COBROS
    with t_cob:
        st.subheader(" Gestión de Cobros")
        busq_cobro = st.text_input("🔍 Buscar por Guía o Cliente:", key="admin_cobros_search")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        if busq_cobro:
            pendientes_p = [p for p in pendientes_p if busq_cobro.lower() in p['ID_Barra'].lower() or busq_cobro.lower() in p['Cliente'].lower()]

        for p in pendientes_p:
            rest = float(p['Monto_USD']) - float(p['Abonado'])
            reemp_label = f" (Incluye Reempaque {p['Reempaque']})" if p['Reempaque'] != "No" else ""
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']} | Debe: ${rest:.2f}{reemp_label}"):
                m_abono = st.number_input("Monto:", 0.0, float(rest), float(rest), key=f"c_{p['ID_Barra']}")
                if st.button("REGISTRAR PAGO", key=f"bc_{p['ID_Barra']}", type="primary"):
                    p.setdefault('Historial_Pagos', []).append({"fecha": datetime.now().strftime("%Y-%m-%d"), "monto": m_abono})
                    p['Abonado'] += m_abono
                    if (float(p['Monto_USD']) - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    # 4. ESTADOS
    with t_est:
        st.subheader(" Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == sel_e)
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"], index=["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"].index(paq['Estado']))
            if st.button("ACTUALIZAR", type="primary"):
                paq["Estado"] = n_st
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    # 5. AUDITORÍA
    with t_aud:
        st.subheader(" Auditoría y Edición")
        guia_ed = st.selectbox("Editar ID:", [p["ID_Barra"] for p in st.session_state.inventario])
        paq_ed = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed)
        c1, c2, c3 = st.columns(3)
        n_cli = c1.text_input("Cliente", value=paq_ed['Cliente'])
        n_reemp = c2.selectbox("Reempaque", ["No", "Small 16x12x12", "Medium 15x16x22", "Large 18x18x24", "Extra Large 22x22x22"], index=["No", "Small 16x12x12", "Medium 15x16x22", "Large 18x18x24", "Extra Large 22x22x22"].index(paq_ed['Reempaque']))
        n_val = c3.number_input("Valor (Kg/ft³)", value=float(paq_ed['Peso_Almacen']))
        if st.button("GUARDAR CAMBIOS", type="primary"):
            paq_ed.update({'Cliente': n_cli, 'Reempaque': n_reemp, 'Peso_Almacen': n_val, 'Monto_USD': calcular_monto(n_val, paq_ed['Tipo_Traslado'], n_reemp)})
            guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    # 6. RESUMEN
    with t_res:
        st.subheader(" Resumen General")
        busq_box = st.text_input("🔍 Código de caja:", key="res_search_admin")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq_box: df_res = df_res[df_res['ID_Barra'].str.contains(busq_box, case=False)]
        
        estados = [("RECIBIDO ALMACEN PRINCIPAL", "📦 ORIGEN"), ("EN TRANSITO", "✈️ TRANSITO"), ("RECIBIDO EN ALMACEN DE DESTINO", "🏢 DESTINO"), ("ENTREGADO", "✅ ENTREGADO")]
        for eid, elabel in estados:
            df_f = df_res[df_res['Estado'] == eid] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{elabel} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    re_tag = f" | {r['Reempaque']}" if r['Reempaque'] != "No" else ""
                    st.markdown(f'<div class="resumen-row"><b>{r["ID_Barra"]}</b> {r["Cliente"]}{re_tag}</div>', unsafe_allow_html=True)

# --- 4. DASHBOARD CLIENTE ---

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if p['Correo'].lower() == u['correo'].lower()]
    if not mis_p: st.info("Sin envíos.")
    else:
        for p in mis_p:
            tot, abo = float(p['Monto_USD']), float(p['Abonado'])
            perc = (abo/tot*100) if tot > 0 else 0
            reemp_info = f'<div style="color:#60a5fa; font-size:13px;">📦 Reempaque: {p["Reempaque"]} (+$5)</div>' if p['Reempaque'] != "No" else ""
            st.markdown(f"""<div class="p-card">
                <div style="display: flex; justify-content: space-between;"><b>{obtener_icono_transporte(p['Tipo_Traslado'])} #{p['ID_Barra']}</b> <span>{p['Estado']}</span></div>
                {reemp_info}
                <div style="margin-top:10px;">Total: <b>${tot:.2f}</b> | Pagado: <b style="color:#4ade80;">${abo:.2f}</b></div>
                <div style="width: 100%; background: #ef4444; height: 10px; border-radius: 5px; margin-top: 10px; overflow: hidden;"><div style="width: {perc}%; background: #22c55e; height: 100%;"></div></div>
            </div>""", unsafe_allow_html=True)

# --- HEADER Y LOGIN (Restaurados) ---
def render_header():
    c1, c2, c3 = st.columns([7, 1, 2])
    with c1: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with c3:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        with st.form("login"):
            le = st.text_input("Usuario/Correo"); lp = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
                # (Lógica de búsqueda de usuarios clientes)
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
