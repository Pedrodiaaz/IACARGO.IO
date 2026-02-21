import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

# --- TARIFAS ACTUALIZADAS ---
TARIFA_AEREO_KG = 6.0    # $6 por Kilogramo
TARIFA_MARITIMO_FT3 = 15.0  # $15 por Pie Cúbico

st.markdown("""
    <style>
    /* Fondo Global */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    /* --- ESTILO DE LOS DESPLEGABLES (EXPANDERS) EN COBROS --- */
    /* Forzamos el color azul y letras blancas SIEMPRE */
    [data-testid="stExpander"] {
        background: rgba(37, 99, 235, 1) !important; /* Azul Primario */
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px !important;
        margin-bottom: 10px;
    }

    /* Estilo del texto del título cuando está cerrado y abierto */
    [data-testid="stExpander"] summary p {
        color: white !important;
        font-weight: 700 !important;
    }

    /* Evitar que cambie de color al pasar el mouse o al abrirse */
    [data-testid="stExpander"] summary:hover, 
    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"][open] summary {
        background-color: #2563eb !important;
        color: white !important;
    }

    /* El contenido interior sí debe ser oscuro o transparente para legibilidad de los inputs */
    [data-testid="stExpanderDetails"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        border-radius: 0 0 15px 15px;
        padding: 20px;
    }

    /* --- OTROS ESTILOS --- */
    .notif-item {
        background: #f1f5f9;
        border-left: 4px solid #2563eb;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 8px;
        color: #1e293b !important;
    }

    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }

    .logo-animado {
        font-style: italic !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2.5s infinite;
        font-weight: 800;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }

    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    
    h1, h2, h3, label { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    else: return valor * 5.0

if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []

def agregar_notificacion(mensaje):
    hora = datetime.now().strftime("%H:%M")
    st.session_state.notificaciones.insert(0, {"msg": mensaje, "hora": hora})

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

# --- Inicialización ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. DASHBOARD ADMINISTRADOR ---
def render_admin_dashboard():
    st.title(" Consola de Control Logístico")
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "ft³" if f_tra == "Marítimo" else "Kg"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0)
            if st.form_submit_button("REGISTRAR", type="primary", use_container_width=True):
                monto = calcular_monto(f_pes, f_tra)
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.session_state.id_actual = generar_id_unico(); st.rerun()

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Valor Real", value=float(paq['Peso_Mensajero']))
            if st.button("VALIDAR", type="primary"):
                paq.update({'Peso_Almacen': v_real, 'Validado': True, 'Monto_USD': calcular_monto(v_real, paq['Tipo_Traslado'])})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader(" Gestión de Cobros")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            # Este expander ahora será azul fijo gracias al CSS arriba
            with st.expander(f"📦 {p['ID_Barra']} — {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"PAGAR", key=f"bp_{p['ID_Barra']}", type="primary"):
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader(" Auditoría y Edición")
        if st.checkbox(" Ver Papelera"):
            if st.session_state.papelera:
                guia_res = st.selectbox("Restaurar:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("Restaurar", type="primary"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
        else:
            df_aud = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df_aud, use_container_width=True)
            if st.session_state.inventario:
                st.write("---")
                guia_ed = st.selectbox("Gestionar ID:", [p["ID_Barra"] for p in st.session_state.inventario], key="ed_sel")
                paq_ed = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed)
                c1, c2, c3 = st.columns(3)
                n_cli = c1.text_input("Cliente", value=paq_ed['Cliente'])
                n_val = c2.number_input("Valor", value=float(paq_ed['Peso_Almacen']))
                n_tra = c3.selectbox("Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], index=["Aéreo", "Marítimo", "Envio Nacional"].index(paq_ed.get('Tipo_Traslado', 'Aéreo')))
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 GUARDAR", type="primary", use_container_width=True):
                        paq_ed.update({'Cliente': n_cli, 'Peso_Almacen': n_val, 'Tipo_Traslado': n_tra, 'Monto_USD': calcular_monto(n_val, n_tra)})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
                with col_btn2:
                    if st.button("🗑️ ELIMINAR", type="primary", use_container_width=True):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()

    with t_res:
        df_res = pd.DataFrame(st.session_state.inventario)
        busq_box = st.text_input(" Buscar caja por código:", key="res_search_admin")
        if busq_box and not df_res.empty: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_box, case=False)]
        for est_k, est_l, _ in [("RECIBIDO ALMACEN PRINCIPAL", " EN ALMACÉN", "Alm"), ("EN TRANSITO", " EN TRÁNSITO", "Tra"), ("ENTREGADO", " ENTREGADO", "Ent")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                    st.markdown(f'<div class="resumen-row"><div style="color:#2563eb; font-weight:800;">{icon} {r["ID_Barra"]}</div><div style="color:#1e293b; flex-grow:1; margin-left:15px;">{r["Cliente"]}</div><div style="color:#475569; font-weight:700;">${float(r["Abonado"]):.2f}</div></div>', unsafe_allow_html=True)

# --- (Resto de funciones: Header, Login y Client se mantienen igual) ---
def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        with st.popover("🔔"):
            for n in st.session_state.notificaciones: st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary", use_container_width=True):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="text-align:center;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                        if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            with t2:
                with st.form("signup"):
                    n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta", type="primary", use_container_width=True):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else:
        u = st.session_state.usuario_identificado
        st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
        mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
        if not mis_p: st.info("Sin envíos.")
        else:
            for p in mis_p:
                st.markdown(f'<div style="background:rgba(255,255,255,0.1); padding:15px; border-radius:15px; margin-bottom:10px;"><b>Guía:</b> {p["ID_Barra"]} | <b>Estado:</b> {p["Estado"]}</div>', unsafe_allow_html=True)
