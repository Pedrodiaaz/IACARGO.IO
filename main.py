import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (LOGO REFORZADO) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    /* Estilo del Logo Principal */
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
        text-align: center;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }
    
    /* Contenedores de Interfaz */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
    }

    .badge-paid { background: #10b981; color: white; padding: 4px 10px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    .badge-debt { background: #ef4444; color: white; padding: 4px 10px; border-radius: 10px; font-size: 10px; font-weight: bold; }

    /* Botón de Registro Estático Azul */
    div[data-testid="stForm"] button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: 1px solid #60a5fa !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"

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

# --- 3. BARRA LATERAL (IDENTIDAD) ---
with st.sidebar:
    st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado['nombre']}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None; st.rerun()
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“Hablamos desde la igualdad”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. LÓGICA DE INTERFACES CONECTADAS ---

if st.session_state.usuario_identificado:
    rol = st.session_state.usuario_identificado.get('rol')

    # A. INTERFAZ ADMINISTRADOR (REALIZA LOS PROCESOS)
    if rol == "admin":
        st.title("⚙️ Consola de Administración")
        t_admin = st.tabs(["📝 Registro", "⚖️ Validación", "💰 Cobros", "📊 Resumen"])
        
        with t_admin[0]: # REGISTRO
            with st.form("reg_admin"):
                f_id = st.text_input("Tracking ID")
                f_cli = st.text_input("Cliente")
                f_cor = st.text_input("Correo")
                f_pes = st.number_input("Peso Inicial (Kg)", min_value=0.0)
                f_mod = st.selectbox("Pago", ["Pago en Cuotas", "Pago Completo"])
                if st.form_submit_button("Registrar Paquete"):
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                             "Peso_Almacen": f_pes, "Monto_USD": f_pes*5.0, "Abonado": 0.0,
                             "Estado": "RECIBIDO EN ALMACEN", "Pago": "PENDIENTE", "Modalidad": f_mod}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Registrado")

    # B. INTERFAZ USUARIO (REFLEJA LOS PROCESOS)
    elif rol == "cliente":
        u = st.session_state.usuario_identificado
        st.markdown(f'<h1 class="logo-animado" style="font-size: 40px;">IACargo.io</h1>', unsafe_allow_html=True)
        st.subheader(f"Bienvenido, {u['nombre']}")
        
        mis_envios = [p for p in st.session_state.inventario if p['Correo'] == u['correo']]
        
        if not mis_envios:
            st.info("No tienes paquetes registrados aún.")
        else:
            busq = st.text_input("🔍 Buscar mi paquete por ID:")
            for p in mis_envios:
                if not busq or busq.lower() in p['ID_Barra'].lower():
                    with st.container():
                        st.markdown(f"""
                        <div class="p-card">
                            <div style="display:flex; justify-content:space-between;">
                                <b>📦 #{p['ID_Barra']}</b>
                                <span class="{'badge-paid' if p['Pago']=='PAGADO' else 'badge-debt'}">{p['Pago']}</span>
                            </div>
                            <p>Estatus: {p['Estado']}</p>
                        """, unsafe_allow_html=True)
                        
                        # BARRA DE PROGRESO DE PAGOS
                        total, abonado = float(p['Monto_USD']), float(p['Abonado'])
                        progreso = (abonado / total) if total > 0 else 0
                        st.progress(min(progreso, 1.0))
                        st.write(f"Pagado: ${abonado:.2f} / Resta: ${(total-abonado):.2f}")
                        st.markdown("</div>", unsafe_allow_html=True)

# --- 5. PÁGINA PRINCIPAL / LOGIN ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align:center;"><h1 class="logo-animado" style="font-size: 70px;">IACargo.io</h1></div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#a78bfa;">“Conectando el milagro de tu existencia con el mundo”</p>', unsafe_allow_html=True)
        
        menu = st.tabs(["Ingresar", "Registro"])
        with menu[0]:
            e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
            if st.button("Entrar", use_container_width=True):
                if e == "admin" and p == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                user = next((u for u in st.session_state.usuarios if u['correo'] == e.lower().strip() and u['password'] == hash_password(p)), None)
                if user: st.session_state.usuario_identificado = user; st.rerun()
                else: st.error("Acceso incorrecto")
