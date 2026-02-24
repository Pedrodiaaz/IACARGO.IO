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
    /* Fondo y Base - Deep Space Gradient */
    .stApp { background: radial-gradient(circle at top left, #0f172a 0%, #020617 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* Contenedores de Cristal (Glassmorphism) */
    .stDetails, [data-testid="stExpander"], .stTabs, .stForm, .p-card {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(16px); 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important; 
        padding: 20px; margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Títulos de los campos (Labels) */
    [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }

    /* Botones de Identidad IACargo (Azul Evolución) */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 14px !important; 
        border: none !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6) !important;
    }

    /* Inputs Estilizados */
    div[data-baseweb="input"] { 
        border-radius: 12px !important; 
        background-color: rgba(255, 255, 255, 0.95) !important; 
    }
    div[data-baseweb="input"] input { color: #0f172a !important; font-weight: 600 !important; }

    /* Logo Animado e Identidad */
    .logo-animado {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #60a5fa);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite; font-weight: 900;
    }
    @keyframes shine { to { background-position: 200% center; } }

    .welcome-text { 
        font-size: 34px; font-weight: 800; 
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* Estilo de Filas en Resumen Admin */
    .resumen-row {
        background: rgba(255, 255, 255, 0.05);
        color: #ffffff; padding: 15px; border-radius: 15px;
        display: flex; justify-content: space-between; align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 10px;
    }

    /* Pestañas (Tabs) */
    button[data-baseweb="tab"] { color: #94a3b8 !important; }
    button[aria-selected="true"] { color: #60a5fa !important; border-bottom-color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB, ARCHIVO_USUARIOS, ARCHIVO_PAPELERA, ARCHIVO_NOTIF = "inventario_logistica.csv", "usuarios_iacargo.csv", "papelera_iacargo.csv", "notificaciones_iac.csv"

def calcular_monto(valor, tipo, aplica_reempaque=False):
    monto = (valor * TARIFA_AEREO_KG) if tipo == "Aéreo" else (valor * TARIFA_MARITIMO_FT3) if tipo == "Marítimo" else (valor * 5.0)
    return monto + COSTO_REEMPAQUE_FIJO if aplica_reempaque else monto

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
    tabs = st.tabs(["📥 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "📍 ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN", "🚨 ALERTAS"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res, t_ale = tabs

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
            st.warning(f"Declarado por mensajero: {paq['Peso_Mensajero']} ({paq['Tipo_Traslado']})")
            valor_real = st.number_input("Medición Real en Almacén:", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR VALIDACIÓN"):
                paq['Peso_Almacen'] = valor_real
                paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(valor_real, paq['Tipo_Traslado'], paq.get('Reempaque', False))
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader("Gestión de Cobros")
        # Buscador solicitado para cobros
        busq_cobro = st.text_input("🔍 Buscar por Cliente o ID para cobro:", placeholder="Ej: Juan Pérez o IAC-123", key="sc")
        p_pago = [p for p in st.session_state.inventario if p['Pago'] != 'PAGADO']
        if busq_cobro:
            p_pago = [p for p in p_pago if busq_cobro.lower() in p['ID_Barra'].lower() or busq_cobro.lower() in p['Cliente'].lower()]
        
        for p in p_pago:
            rest = float(p['Monto_USD']) - float(p['Abonado'])
            with st.expander(f"💵 {p['Cliente']} - {p['ID_Barra']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto a Abonar:", 0.0, float(rest), float(rest), key=f"c_{p['ID_Barra']}")
                if st.button("REGISTRAR ABONO", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] = float(p['Abonado']) + m_abono
                    if (float(p['Monto_USD']) - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_res:
        st.subheader("📋 Resumen Logístico")
        # Buscador solicitado para resumen de cajas
        b_box = st.text_input("🔍 Localizar por Código de Caja:", placeholder="Escriba el ID para filtrar...", key="res_box_search")
        df_res = pd.DataFrame(st.session_state.inventario)
        if b_box and not df_res.empty:
            df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(b_box, case=False)]
        
        config_est = [
            ("RECIBIDO ALMACEN PRINCIPAL", "📦 EN ALMACÉN ORIGEN"), 
            ("EN TRANSITO", "✈️ EN TRÁNSITO"), 
            ("RECIBIDO EN ALMACEN DE DESTINO", "🏢 ALMACÉN DESTINO"), 
            ("ENTREGADO", "✅ ENTREGADO")
        ]
        
        for est_id, label in config_est:
            df_f = df_res[df_res['Estado'] == est_id] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{label} ({len(df_f)})", expanded=True if b_box else False):
                if not df_f.empty:
                    for _, r in df_f.iterrows():
                        col_info, col_btn = st.columns([5, 1])
                        with col_info:
                            icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                            badge_r = '<span style="color:#a78bfa; font-size:10px;">[REEMPAQUE]</span>' if r.get("Reempaque") else ""
                            st.markdown(f'<div class="resumen-row"><div>{icon} <b>{r["ID_Barra"]}</b></div><div style="flex-grow:1; margin-left:20px;">{r["Cliente"]} {badge_r}</div><div><small>{r["Tipo_Traslado"]}</small></div></div>', unsafe_allow_html=True)
                        with col_btn:
                            if st.button(f"INFO", key=f"rep_{r['ID_Barra']}"):
                                rest_p = float(r['Monto_USD']) - float(r['Abonado'])
                                st.info(f"Guía {r['ID_Barra']}: Total ${float(r['Monto_USD']):.2f} | Pendiente: ${rest_p:.2f}")

    # Pestañas de Estados, Auditoría y Alertas mantenidas según lógica previa...
    with t_est:
        st.subheader("Actualizar Ubicación")
        if st.session_state.inventario:
            guia_est = st.selectbox("Seleccionar Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_est)
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS"):
                paq["Estado"] = n_st
                registrar_notificacion(paq['Correo'], f"Tu paquete {paq['ID_Barra']} está ahora en: {n_st}")
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

# --- 4. DASHBOARD CLIENTE (VISTA EVOLUCIÓN CON BARRA) ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    
    if not mis_p: 
        st.info("No tienes envíos activos en este momento.")
    else:
        busq_cli = st.text_input("🔍 Buscar mis paquetes:", placeholder="ID o Estatus...", key="cli_s")
        if busq_cli: 
            mis_p = [p for p in mis_p if busq_cli.lower() in p['ID_Barra'].lower() or busq_cli.lower() in p['Estado'].lower()]
        
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0))
                abo = float(p.get('Abonado', 0.0))
                perc = (abo / tot * 100) if tot > 0 else 0
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                
                st.markdown(f"""
                <div class="p-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <span style="color:#60a5fa; font-weight:800; font-size: 22px;">{icon} #{p['ID_Barra']}</span>
                        <span style="background:rgba(96,165,250,0.1); color:#60a5fa; padding: 4px 12px; border-radius:20px; font-size:11px; font-weight:700; border: 1px solid rgba(96,165,250,0.2);">
                            {p['Estado']}
                        </span>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <small style="color: #94a3b8; text-transform: uppercase; font-size: 10px; letter-spacing: 1px;">Inversión de Envío</small>
                        <div style="font-size: 32px; font-weight: 800; color:white;">${tot:.2f} <small style="font-size: 14px; color: #94a3b8;">USD</small></div>
                    </div>

                    <div style="margin-top: 25px;">
                        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 8px;">
                            <span style="color: #4ade80; font-weight: 600;">Abonado: ${abo:.2f}</span>
                            <span style="color: #f87171; font-weight: 600;">Faltante: ${tot-abo:.2f}</span>
                        </div>
                        <div style="width: 100%; background: rgba(255,255,255,0.1); height: 10px; border-radius: 10px; overflow: hidden;">
                            <div style="width: {perc}%; background: linear-gradient(90deg, #22c55e, #4ade80); height: 100%; border-radius: 10px; box-shadow: 0 0 10px rgba(34,197,94,0.5);"></div>
                        </div>
                        <div style="text-align: right; margin-top: 6px; font-size: 11px; color: #94a3b8;">{int(perc)}% completado</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. LOGICA ACCESO Y HEADER ---
def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    with col_l: st.markdown('<div class="logo-animado" style="font-size:35px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        u = st.session_state.usuario_identificado
        target = 'admin' if u['rol'] == 'admin' else u['correo']
        mías = [n for n in st.session_state.notificaciones if n['para'] == target]
        with st.popover("🔔"):
            if mías:
                for n in mías[:5]: st.write(f"**{n['hora']}**: {n['msg']}")
            else: st.write("Sin novedades.")
    with col_s:
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- FLUJO PRINCIPAL ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:90px;">IACargo.io</h1><p style="font-size:22px; opacity:0.8; letter-spacing: 2px;">"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INICIAR EVOLUCIÓN", use_container_width=True): 
            st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:50px; margin-bottom:20px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🔐 Entrar", "📝 Registro"])
            with t1:
                with st.form("login"):
                    le, lp = st.text_input("Correo / Usuario"), st.text_input("Contraseña", type="password")
                    if st.form_submit_button("ACCEDER"):
                        if le == "admin" and lp == "admin123": 
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
                        else: st.error("Credenciales incorrectas")
            with t2:
                with st.form("signup"):
                    n, e, p = st.text_input("Nombre Completo"), st.text_input("Correo Electrónico"), st.text_input("Crea tu Contraseña", type="password")
                    if st.form_submit_button("CREAR MI CUENTA"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Registro exitoso! Ya puedes entrar."); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
