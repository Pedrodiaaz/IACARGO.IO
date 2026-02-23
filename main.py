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
    
    /* ESTILO ESPECÍFICO DE LA CAMPANA Y PUNTO ROJO */
    .bell-container {
        position: relative;
        display: inline-block;
        font-size: 28px;
        cursor: pointer;
    }
    .bell-icon { color: #facc15; }
    
    .red-dot {
        position: absolute;
        top: 2px;
        right: 0px;
        height: 10px;
        width: 10px;
        background-color: #ef4444;
        border-radius: 50%;
        border: 1.5px solid #0f172a;
        z-index: 10;
    }

    /* Ocultar el botón estándar del popover para que solo se vea la campana */
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        color: transparent !important;
        width: 40px !important;
        height: 40px !important;
    }

    /* --- FONDO BLANCO PARA NOTIFICACIONES --- */
    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
        min-width: 300px !important;
    }

    .notif-item {
        background: #f1f5f9;
        border-left: 4px solid #2563eb;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 8px;
        font-size: 0.85em;
        color: #1e293b !important;
    }

    /* BOTONES PRIMARIOS */
    .stButton > button {
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
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
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }

    .stTabs, .stForm, [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
    }

    .p-card {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    .p-card:hover { transform: translateY(-5px); border-color: #60a5fa; }

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

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    else: return valor * 5.0

if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []

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
    return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")

# --- Inicialización ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. FUNCIONES DE DASHBOARD ---

def render_admin_dashboard():
    st.title(" Consola de Control Logístico")
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos (ft³)" if f_tra == "Marítimo" else "Peso (Kilogramos)"
        with st.form("reg_form", clear_on_submit=True):
            st.info(f"ID sugerido: **{st.session_state.id_actual}**")
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary"):
                if f_id and f_cli and f_cor:
                    monto_calculado = calcular_monto(f_pes, f_tra)
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto_calculado, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.success(f"Guía {f_id} registrada."); st.rerun()

    with t_est:
        st.subheader(" Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="status_sel")
            paq_obj = next(p for p in st.session_state.inventario if p["ID_Barra"] == sel_e)
            estado_actual = paq_obj["Estado"]
            
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"], index=["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"].index(estado_actual))
            
            if st.button("ACTUALIZAR ESTATUS", type="primary"):
                if n_st != estado_actual:
                    # Registrar Notificación con Flecha
                    nueva_notif = {
                        "hora": datetime.now().strftime("%H:%M"),
                        "paquete": f"Guía {sel_e}",
                        "estado_ant": estado_actual,
                        "estado_nuevo": n_st
                    }
                    st.session_state.notificaciones.insert(0, nueva_notif)
                    paq_obj["Estado"] = n_st
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("Estado actualizado y notificado."); st.rerun()

    # (Las demás pestañas t_val, t_cob, t_aud, t_res se mantienen igual a tu código original)
    with t_val:
        st.subheader(" Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            label_val = "Pies Cúbicos Reales" if paq['Tipo_Traslado'] == "Marítimo" else "Peso Real (Kg)"
            valor_real = st.number_input(label_val, min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR Y VALIDAR", type="primary"):
                paq['Peso_Almacen'] = valor_real
                paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(valor_real, paq['Tipo_Traslado'])
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader(" Gestión de Cobros")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f"📦 {p['ID_Barra']} — {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"REGISTRAR PAGO", key=f"bp_{p['ID_Barra']}", type="primary"):
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader(" Auditoría y Edición")
        busq_aud = st.text_input(" Buscar por Guía:", key="aud_search_input")
        df_aud = pd.DataFrame(st.session_state.inventario)
        if not df_aud.empty and busq_aud: 
            df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq_aud, case=False)]
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader(" Resumen General")
        df_res = pd.DataFrame(st.session_state.inventario)
        for est_k, est_l, _ in [("RECIBIDO ALMACEN PRINCIPAL", " EN ALMACÉN", "Alm"), ("EN TRANSITO", " EN TRÁNSITO", "Tra"), ("ENTREGADO", " ENTREGADO", "Ent")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})", expanded=False):
                for _, r in df_f.iterrows():
                    icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                    st.markdown(f'<div class="resumen-row"><div style="color:#2563eb; font-weight:800;">{icon} {r["ID_Barra"]}</div><div style="color:#1e293b; flex-grow:1; margin-left:15px;">{r["Cliente"]}</div><div style="color:#475569; font-weight:700;">${float(r["Abonado"]):.2f}</div></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if not mis_p: st.info("Sin envíos activos.")
    else:
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0))
                perc = (abo / tot * 100) if tot > 0 else 0
                st.markdown(f'<div class="p-card"><span style="color:#60a5fa; font-weight:800;">{obtener_icono_transporte(p["Tipo_Traslado"])} #{p["ID_Barra"]}</span><br><small>{p["Estado"]}</small><br><b>Total: ${tot:.2f}</b><br>Pagado: ${abo:.2f}<div style="width: 100%; background:#ef4444; height:8px; border-radius:4px; margin-top:10px;"><div style="width:{perc}%; background:#22c55e; height:100%; border-radius:4px;"></div></div></div>', unsafe_allow_html=True)

def render_header():
    col_l, col_n, col_s = st.columns([7, 0.8, 2.2])
    with col_l: 
        st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    
    with col_n:
        # Lógica de Campana Minimalista
        hay_notif = len(st.session_state.notificaciones) > 0
        red_dot = '<div class="red-dot"></div>' if hay_notif else ""
        
        # El Label del popover es solo el HTML de la campana
        with st.popover(" "):
            # Este div simula la campana que flota sobre el botón invisible del popover
            st.markdown(f'''
                <div style="position: absolute; top: -35px; left: 5px; pointer-events: none;">
                    <div class="bell-container">
                        <span class="bell-icon">🔔</span>
                        {red_dot}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown("<h4 style='color:#1e293b; margin-top:0;'>Historial de Cambios</h4>", unsafe_allow_html=True)
            if not st.session_state.notificaciones:
                st.write("No hay cambios nuevos.")
            else:
                for n in st.session_state.notificaciones:
                    st.markdown(f'''
                        <div class="notif-item">
                            <small style="color:#64748b;">{n["hora"]}</small><br>
                            <b style="font-size:1.1em;">{n["paquete"]}</b><br>
                            <div style="margin-top:5px;">
                                <span style="color:#ef4444;">{n["estado_ant"]}</span> 
                                <b style="color:#1e293b;"> ➔ </b> 
                                <span style="color:#22c55e;">{n["estado_nuevo"]}</span>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                if st.button("Limpiar Notificaciones", use_container_width=True):
                    st.session_state.notificaciones = []
                    st.rerun()

    with col_s:
        if st.button("CERRAR SESIÓN", type="primary", use_container_width=True):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- LÓGICA DE LOGIN (Simplificada para el ejemplo) ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        with st.form("login"):
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
