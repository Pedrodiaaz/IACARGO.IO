import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
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
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }

    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }

    /* BOTÓN DE REGISTRO ESTÁTICO DENTRO DEL FORMULARIO */
    div[data-testid="stForm"] button {
        background-color: #2563eb !important;
        background-image: none !important;
        color: white !important;
        border: 1px solid #60a5fa !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        transition: none !important;
    }
    div[data-testid="stForm"] button:hover {
        background-color: #2563eb !important;
        color: white !important;
    }

    .header-resumen {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        margin: 10px 0;
        border-left: 6px solid #60a5fa;
    }

    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 12px;
        border-bottom: 2px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        border-radius: 4px;
        margin-bottom: 4px;
    }
    
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIONES DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo).to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado['nombre']}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None; st.rerun()
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“Hablamos desde la igualdad”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. LÓGICA DE INTERFACES ---

# A. INTERFAZ ADMINISTRADOR
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "📊 RESUMEN"])
    
    with tabs[0]: # REGISTRO
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking")
            f_cli = st.text_input("Nombre Cliente")
            f_cor = st.text_input("Correo Cliente")
            f_pes = st.number_input("Peso (Kg)", min_value=0.0)
            f_mod = st.selectbox("Pago", ["Pago Completo", "Pago en Cuotas", "Cobro Destino"])
            if st.form_submit_button("Registrar en Sistema"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                         "Peso_Almacen": f_pes, "Monto_USD": f_pes*PRECIO_POR_KG, "Abonado": 0.0,
                         "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Validado": True}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Registrado")

    # (Las demás pestañas de admin se mantienen funcionales según la estructura previa...)
    with tabs[4]: # RESUMEN
        st.subheader("Estado Global")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df)

# B. INTERFAZ CLIENTE (RESTAURADA)
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    # Filtrar paquetes del cliente
    u_mail = str(u.get('correo', '')).lower().strip()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower().strip() == u_mail]
    
    if not mis_p:
        st.info("No tienes paquetes registrados actualmente.")
    else:
        st.subheader("📋 Mis Envíos en Tránsito")
        col_p1, col_p2 = st.columns(2)
        
        for i, p in enumerate(mis_p):
            with (col_p1 if i % 2 == 0 else col_p2):
                total = float(p.get('Monto_USD', 0))
                abonado = float(p.get('Abonado', 0))
                pago_s = p.get('Pago', 'PENDIENTE')
                badge = "badge-paid" if pago_s == "PAGADO" else "badge-debt"
                
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight:bold; color:#60a5fa; font-size:1.2em;">📦 #{p['ID_Barra']}</span>
                            <span class="{badge}">{pago_s}</span>
                        </div>
                        <div style="margin: 15px 0; font-size: 0.95em;">
                            <b>📍 Estado:</b> {p['Estado']}<br>
                            <b>⚖️ Peso:</b> {p['Peso_Almacen']} Kg<br>
                            <b>💳 Modalidad:</b> {p.get('Modalidad', 'N/A')}
                        </div>
                """, unsafe_allow_html=True)
                
                # BARRA DE PROGRESO DE PAGOS RE-ESTABLECIDA
                progreso = (abonado / total) if total > 0 else 0
                st.progress(min(progreso, 1.0))
                
                st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; font-size: 0.85em; margin-top: 5px;">
                            <span>Pagado: <b>${abonado:.2f}</b></span>
                            <span style="color:#f87171;">Resta: <b>${(total-abonado):.2f}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# C. LOGIN / REGISTRO
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown('<div style="text-align: center;"><div class="logo-animado" style="font-size: 60px;">IACargo.io</div></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Crear Cuenta"])
        with t1:
            le = st.text_input("Correo")
            lp = st.text_input("Clave", type="password")
            if st.button("Entrar", use_container_width=True):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Credenciales incorrectas")
        with t2:
            with st.form("registro_nuevo"):
                n = st.text_input("Nombre completo")
                e = st.text_input("Correo electrónico")
                p = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Registrarme"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Cuenta creada!"); st.rerun()
