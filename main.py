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
COSTO_REEMPAQUE_FIJO = 5.0 

st.markdown("""
    <style>
    /* Fondo y Base */
    .stApp { background: radial-gradient(circle at top left, #0f172a 0%, #020617 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Contenedores de Cristal (Glassmorphism) */
    .stDetails, [data-testid="stExpander"], .stTabs, .stForm {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important; 
        padding: 15px; margin-bottom: 20px;
    }

    /* Botones de Identidad IACargo (Azul Vibrante) */
    div.stButton > button, .stForm div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important; 
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        width: 100% !important; 
        padding: 12px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.6) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    }

    /* Inputs Estilizados */
    div[data-baseweb="input"] { 
        border-radius: 12px !important; 
        background-color: rgba(255, 255, 255, 0.9) !important; 
        border: 2px solid transparent !important;
    }
    div[data-baseweb="input"]:focus-within { border-color: #60a5fa !important; }
    div[data-baseweb="input"] input { color: #0f172a !important; font-weight: 600 !important; }

    /* Logo Animado */
    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #60a5fa);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: shine 3s linear infinite; font-weight: 800;
    }
    @keyframes shine { to { background-position: 200% center; } }

    /* Tarjetas de Paquete */
    .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .p-card:hover { border-color: #60a5fa; background: rgba(255, 255, 255, 0.08) !important; }
    
    /* Notificaciones */
    .notif-item {
        background: white; border-left: 5px solid #2563eb;
        padding: 12px; margin-bottom: 8px; border-radius: 10px; color: #1e293b !important;
    }

    /* Tabs Visual */
    button[data-baseweb="tab"] { color: #94a3b8 !important; font-weight: 600 !important; }
    button[aria-selected="true"] { color: #60a5fa !important; border-bottom-color: #60a5fa !important; }

    /* Welcome Text */
    .welcome-text { 
        font-size: 32px; font-weight: 800; 
        background: linear-gradient(90deg, #ffffff, #94a3b8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS (Mantenida) ---
ARCHIVO_DB, ARCHIVO_USUARIOS, ARCHIVO_PAPELERA, ARCHIVO_NOTIF = "inventario_logistica.csv", "usuarios_iacargo.csv", "papelera_iacargo.csv", "notificaciones_iac.csv"

def calcular_monto(valor, tipo, aplica_reempaque=False):
    monto = (valor * TARIFA_AEREO_KG) if tipo == "Aéreo" else (valor * TARIFA_MARITIMO_FT3) if tipo == "Marítimo" else (valor * 5.0)
    return monto + COSTO_REEMPAQUE_FIJO if aplica_reempaque else monto

def registrar_notificacion(para, msg):
    nueva = {"hora": datetime.now().strftime("%H:%M"), "para": para, "msg": msg}
    st.session_state.notificaciones.insert(0, nueva)
    pd.DataFrame(st.session_state.notificaciones).to_csv(ARCHIVO_NOTIF, index=False)

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            if 'Historial_Pagos' in df.columns: df['Historial_Pagos'] = df['Historial_Pagos'].apply(lambda x: eval(x) if isinstance(x, str) else [])
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

# --- 3. DASHBOARDS ---

def render_admin_dashboard():
    st.markdown('<div class="welcome-text">Consola de Control Logístico</div>', unsafe_allow_html=True)
    tabs = st.tabs(["📥 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "📍 ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        label_din = "Pies Cúbicos (ft³)" if f_tra == "Marítimo" else "Peso (Kilogramos)"
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            f_id = col1.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = col2.text_input("Nombre del Cliente")
            f_cor = col1.text_input("Correo del Cliente")
            f_pes = col2.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            f_reemp = st.checkbox("📦 ¿Solicita Reempaque Especial? (+$5.00)")
            if st.form_submit_button("REGISTRAR PAQUETE"):
                if f_id and f_cli and f_cor:
                    monto_calc = calcular_monto(f_pes, f_tra, f_reemp)
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto_calc, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Reempaque": f_reemp, "Abonado": 0.0, "Fecha_Registro": datetime.now(), "Historial_Pagos": []}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    registrar_notificacion(f_cor.lower().strip(), f"¡Hola! Hemos recibido tu paquete {f_id} en origen.")
                    st.session_state.id_actual = generar_id_unico()
                    st.rerun()

    with t_val:
        st.subheader("Validación de Carga")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Guía a validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.warning(f"Peso declarado por mensajero: {paq['Peso_Mensajero']}")
            valor_real = st.number_input("Peso/Dimensión Real en Almacén:", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR VALIDACIÓN"):
                paq['Peso_Almacen'] = valor_real
                paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(valor_real, paq['Tipo_Traslado'], paq.get('Reempaque', False))
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader("Gestión de Cobros")
        busq_cobro = st.text_input("🔍 Buscar por Cliente o ID:", key="sc")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        if busq_cobro:
            pendientes_p = [p for p in pendientes_p if busq_cobro.lower() in p['ID_Barra'].lower() or busq_cobro.lower() in p['Cliente'].lower()]
        for p in pendientes_p:
            rest = float(p['Monto_USD']) - float(p['Abonado'])
            with st.expander(f"💵 {p['Cliente']} - {p['ID_Barra']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto:", 0.0, float(rest), float(rest), key=f"c_{p['ID_Barra']}")
                if st.button("REGISTRAR ABONO", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] = float(p['Abonado']) + m_abono
                    if (float(p['Monto_USD']) - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("Actualizar Ubicación")
        if st.session_state.inventario:
            guia_est = st.selectbox("Seleccionar Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_est)
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS"):
                paq["Estado"] = n_st
                registrar_notificacion(paq['Correo'], f"Tu paquete {paq['ID_Barra']} se encuentra en: {n_st}")
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("Auditoría de Datos")
        busq_aud = st.text_input("🔍 Buscar en historial:", key="aud_s")
        df_aud = pd.DataFrame(st.session_state.inventario)
        if not df_aud.empty and busq_aud:
            df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq_aud, case=False)]
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader("Resumen de Almacén")
        busq_box = st.text_input("🔍 Localizar Caja:", key="res_s")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq_box and not df_res.empty:
            df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_box, case=False)]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("En Almacén", len(df_res[df_res['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"]) if not df_res.empty else 0)
        col2.metric("En Tránsito", len(df_res[df_res['Estado'] == "EN TRANSITO"]) if not df_res.empty else 0)
        col3.metric("Entregados", len(df_res[df_res['Estado'] == "ENTREGADO"]) if not df_res.empty else 0)

# --- 4. DASHBOARD CLIENTE (REESTABLECIMIENTO COMPLETO) ---

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    
    if not mis_p:
        st.info("Actualmente no tienes envíos activos.")
    else:
        busq_cli = st.text_input("🔍 Buscar paquete...", key="cli_s")
        if busq_cli:
            mis_p = [p for p in mis_p if busq_cli.lower() in p['ID_Barra'].lower() or busq_cli.lower() in p['Estado'].lower()]

        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot, abo = float(p.get('Monto_USD', 0.0)), float(p.get('Abonado', 0.0))
                perc = (abo / tot * 100) if tot > 0 else 0
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                st.markdown(f"""
                <div class="p-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#60a5fa; font-weight:800; font-size: 20px;">{icon} #{p['ID_Barra']}</span>
                        <span style="background:rgba(96,165,250,0.2); color:#60a5fa; padding: 4px 10px; border-radius:10px; font-size:11px;">{p['Estado']}</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <small style="opacity:0.7;">Total a pagar</small>
                        <div style="font-size: 26px; font-weight: 800; color:white;">${tot:.2f}</div>
                    </div>
                    <div style="width: 100%; background-color: rgba(239, 68, 68, 0.3); height: 8px; border-radius: 4px; margin-top: 15px;">
                        <div style="width: {perc}%; background: #22c55e; height: 100%; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 5px;">
                        <span>Pagado: ${abo:.2f}</span>
                        <span>Faltan: ${tot-abo:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. LÓGICA DE ACCESO (LOGIN RECUPERADO) ---

def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        u = st.session_state.usuario_identificado
        target = 'admin' if u['rol'] == 'admin' else u['correo']
        mías = [n for n in st.session_state.notificaciones if n['para'] == target]
        with st.popover("🔔"):
            if mías:
                for n in mías[:5]: st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
            else: st.write("Sin avisos nuevos.")
    with col_s:
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:100px;">IACargo.io</h1><p style="font-size:20px; opacity:0.8;">"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        st.write("")
        col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
        if col_b2.button("INGRESAR AL SISTEMA"): 
            st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🔐 Entrar", "📝 Registro"])
            with t1:
                with st.form("login"):
                    le = st.text_input("Correo")
                    lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("ACCEDER"):
                        if le == "admin" and lp == "admin123": 
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
                        else: st.error("Credenciales incorrectas")
            with t2:
                with st.form("signup"):
                    n = st.text_input("Nombre Completo")
                    e = st.text_input("Email")
                    p = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("CREAR CUENTA"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Registrado!"); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
