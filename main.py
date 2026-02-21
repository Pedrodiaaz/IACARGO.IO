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
    
    /* CAMPANA Y NOTIFICACIONES */
    .bell-container { position: relative; display: inline-block; font-size: 26px; }
    .bell-icon { color: #facc15; }
    .red-dot {
        position: absolute; top: -2px; right: -2px; height: 12px; width: 12px;
        background-color: #ef4444; border-radius: 50%; border: 2px solid #0f172a; z-index: 10;
    }

    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important;
        border-radius: 15px !important;
        padding: 10px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }

    .notif-item {
        background: #f1f5f9; border-left: 4px solid #2563eb;
        padding: 10px; margin-bottom: 8px; border-radius: 8px;
        font-size: 0.9em; color: #1e293b !important;
    }

    /* ESTILOS DE LOGO Y BOTONES */
    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    .stButton > button[kind="primary"] {
        background-color: #2563eb !important; color: white !important; border-radius: 12px !important;
        font-weight: bold !important; width: 100% !important; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }

    .p-card {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px;
    }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS Y NOTIFICACIONES INTELIGENTES ---
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []

def agregar_notificacion(mensaje, destino="admin", correo_cliente=None):
    hora = datetime.now().strftime("%H:%M")
    st.session_state.notificaciones.insert(0, {
        "msg": mensaje, 
        "hora": hora, 
        "destino": destino, 
        "correo": correo_cliente, 
        "leida": False
    })

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

# (Funciones de soporte iguales...)
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
def obtener_icono_transporte(tipo): return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")

# Inicialización
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos("inventario_logistica.csv")
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos("usuarios_iacargo.csv")
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. COMPONENTES ---

def render_header():
    u = st.session_state.usuario_identificado
    col_l, col_n, col_s = st.columns([7, 1, 2])
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        # Filtrar notificaciones según rol
        if u['rol'] == 'admin':
            mis_notif = [n for n in st.session_state.notificaciones if n['destino'] == 'admin']
        else:
            mis_notif = [n for n in st.session_state.notificaciones if n['correo'] == u['correo']]
        
        has_unread = any(not n['leida'] for n in mis_notif)
        
        with st.popover("🔔"):
            st.markdown('<div class="bell-container"><span class="bell-icon">🔔</span>' + ('<div class="red-dot"></div>' if has_unread else '') + '</div>', unsafe_allow_html=True)
            if not mis_notif: st.write("No hay notificaciones.")
            for n in mis_notif:
                st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b>: {n["msg"]}</div>', unsafe_allow_html=True)
                n['leida'] = True
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

def render_admin_dashboard():
    st.title("Consola de Control Logístico")
    tabs = st.tabs(["REGISTRO", "VALIDACIÓN", "COBROS", "ESTADOS", "AUDITORÍA", "RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking", value=generar_id_unico())
            f_cli = st.text_input("Nombre Cliente")
            f_cor = st.text_input("Correo Cliente")
            f_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
            f_pes = st.number_input("Peso/Medida Inicial", min_value=0.0)
            if st.form_submit_button("REGISTRAR", type="primary"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": calcular_monto(f_pes, f_tra), "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                agregar_notificacion(f"📦 Nuevo paquete registrado: {f_id}", "admin")
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Validar Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Peso/Medida Real", value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR PESAJE", type="primary"):
                paq['Peso_Almacen'] = v_real; paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(v_real, paq['Tipo_Traslado'])
                agregar_notificacion(f"⚖️ Tu paquete {paq['ID_Barra']} ha sido verificado con {v_real} unidades.", "cliente", paq['Correo'])
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    with t_est:
        sel_e = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
        n_st = st.selectbox("Estado:", ["EN TRANSITO", "RECIBIDO EN DESTINO", "ENTREGADO"])
        if st.button("ACTUALIZAR ESTATUS", type="primary"):
            for p in st.session_state.inventario:
                if p["ID_Barra"] == sel_e: 
                    p["Estado"] = n_st
                    agregar_notificacion(f"🚚 Movimiento: Tu paquete {sel_e} cambió a {n_st}", "cliente", p['Correo'])
            guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    # (Resto de pestañas admin similares al código anterior...)
    with t_res:
        df_res = pd.DataFrame(st.session_state.inventario)
        for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
            df_f = df_res[df_res['Estado'] == est] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    st.markdown(f'<div class="resumen-row"><b>{r["ID_Barra"]}</b> <span>{r["Cliente"]}</span></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if p.get('Correo') == u['correo']]
    
    if not mis_p: st.info("No tienes paquetes registrados.")
    for p in mis_p:
        with st.container():
            icon = obtener_icono_transporte(p['Tipo_Traslado'])
            val_status = "✅ Verificado" if p['Validado'] else "⏳ Pendiente"
            color_v = "#4ade80" if p['Validado'] else "#facc15"
            
            st.markdown(f"""
            <div class="p-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size:20px; font-weight:800;">{icon} #{p['ID_Barra']}</span>
                    <span style="color:{color_v}; font-weight:bold;">{val_status}</span>
                </div>
                <div style="margin: 15px 0;">
                    <small>Estatus actual:</small>
                    <div style="font-size:18px; color:#60a5fa;">{p['Estado']}</div>
                </div>
                <div style="display: flex; gap: 20px; font-size: 13px; opacity: 0.8;">
                    <span>Peso Inicial: {p['Peso_Mensajero']}</span>
                    <span>Peso Almacén: {p['Peso_Almacen'] if p['Validado'] else '---'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(float(p['Abonado'])/float(p['Monto_USD']), 1.0) if float(p['Monto_USD']) > 0 else 0)

# --- LOGIN ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t2:
                with st.form("signup"):
                    n, e, p = st.text_input("Nombre"), st.text_input("Correo"), st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta", type="primary"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        agregar_notificacion(f"👤 Nuevo usuario registrado: {n}", "admin")
                        guardar_datos(st.session_state.usuarios, "usuarios_iacargo.csv"); st.rerun()
            with t1:
                with st.form("login"):
                    le, lp = st.text_input("Correo"), st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary"):
                        if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
