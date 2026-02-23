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
    
    .bell-container { position: relative; display: inline-block; font-size: 26px; }
    .red-dot {
        position: absolute; top: -2px; right: -2px; height: 12px; width: 12px;
        background-color: #ef4444; border-radius: 50%; border: 2px solid #0f172a; z-index: 10;
    }

    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important; border-radius: 15px !important;
        padding: 10px !important; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stPopoverContent"] p, div[data-testid="stPopoverContent"] b { color: #1e293b !important; }

    .notif-item {
        background: #f1f5f9; border-left: 4px solid #2563eb;
        padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9em; color: #1e293b !important;
    }

    .stButton > button { border-radius: 12px !important; transition: all 0.3s ease !important; }
    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important; color: white !important; font-weight: bold !important;
        width: 100% !important; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px;
    }
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    h1, h2, h3, p, span, label { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_NOTIF = "notificaciones.csv"

def agregar_notificacion(para, msg):
    nueva = {"fecha": datetime.now().strftime("%d/%m %H:%M"), "para": para, "msg": msg}
    st.session_state.notificaciones.insert(0, nueva)
    pd.DataFrame(st.session_state.notificaciones).to_csv(ARCHIVO_NOTIF, index=False)

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo).to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)
def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
def obtener_icono_transporte(tipo): return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")
def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

# Inicialización
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = cargar_datos(ARCHIVO_NOTIF)
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. FUNCIONES DASHBOARD ---

def render_admin_dashboard():
    st.title("Consola de Control Logístico")
    t_reg, t_val, t_cob, t_est, t_aud, t_res = st.tabs(["REGISTRO", "VALIDACIÓN", "COBROS", "ESTADOS", "AUDITORÍA", "RESUMEN"])

    with t_reg:
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo").lower().strip()
            f_pes = st.number_input("Peso/Volumen inicial", min_value=0.0)
            if st.form_submit_button("REGISTRAR", type="primary"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor, "Peso_Almacen": f_pes, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Monto_USD": calcular_monto(f_pes, f_tra), "Abonado": 0.0, "Pago": "PENDIENTE", "Tipo_Traslado": f_tra}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                # Notificación para el Admin
                agregar_notificacion("admin", f"📦 Nuevo registro: {f_id} para {f_cli}")
                st.session_state.id_actual = generar_id_unico()
                st.rerun()

    with t_est:
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == sel_e)
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS", type="primary"):
                old_st = paq["Estado"]
                paq["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                # Notificación para el Usuario
                agregar_notificacion(paq["Correo"], f"🚀 Actualización {sel_e}: {old_st} ➔ {n_st}")
                st.rerun()

    # (Las demás pestañas t_val, t_cob, t_aud, t_res mantienen su lógica original)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    
    if not mis_p: st.info("Sin envíos activos.")
    else:
        for p in mis_p:
            tot, abo = float(p.get('Monto_USD', 0)), float(p.get('Abonado', 0))
            perc = (abo / tot * 100) if tot > 0 else 0
            st.markdown(f"""<div class="p-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color:#60a5fa; font-weight:800;">{obtener_icono_transporte(p['Tipo_Traslado'])} #{p['ID_Barra']}</span>
                    <span style="background:rgba(96,165,250,0.2); padding: 4px 10px; border-radius:10px;">{p['Estado']}</span>
                </div>
                <div style="margin-top:10px;">Progreso de Pago: {perc:.1f}%</div>
                <div style="width:100%; background:#ef4444; height:8px; border-radius:4px; margin-top:5px;">
                    <div style="width:{perc}%; background:#22c55e; height:100%; border-radius:4px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    u = st.session_state.usuario_identificado
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    
    with col_n:
        # Filtrar notificaciones según quién está logueado
        mías = [n for n in st.session_state.notificaciones if n['para'] == (u['rol'] if u['rol'] == 'admin' else u['correo'])]
        has_notif = len(mías) > 0
        
        with st.popover("🔔"):
            if has_notif: st.markdown('<div class="red-dot"></div>', unsafe_allow_html=True)
            if not mías: st.write("No hay notificaciones.")
            else:
                for n in mías[:10]: # Mostrar las últimas 10
                    st.markdown(f'<div class="notif-item"><b>{n["fecha"]}</b><br>{n["msg"]}</div>', unsafe_allow_html=True)
                if st.button("Limpiar Notificaciones"):
                    st.session_state.notificaciones = [n for n in st.session_state.notificaciones if n['para'] != (u['rol'] if u['rol'] == 'admin' else u['correo'])]
                    pd.DataFrame(st.session_state.notificaciones).to_csv(ARCHIVO_NOTIF, index=False)
                    st.rerun()

    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None
            st.session_state.landing_vista = True
            st.rerun()

# --- LÓGICA DE ACCESO ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            t1, t2 = st.tabs(["Entrar", "Registrarse"])
            with t1:
                with st.form("login"):
                    le, lp = st.text_input("Correo"), st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary"):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}
                            st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            with t2:
                with st.form("signup"):
                    n, e, p = st.text_input("Nombre"), st.text_input("Correo"), st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Creado!"); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
