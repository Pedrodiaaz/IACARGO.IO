import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IACargo.io | Evolution", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .p-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-active { background: #0080FF; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e9ecef; color: #adb5bd; padding: 10px; border-radius: 8px; text-align: center; }
    .welcome-text { color: #0080FF; font-weight: bold; font-size: 24px; margin-bottom: 10px; }
    .state-header { background: #0080FF; color: white; padding: 10px; border-radius: 8px; margin-top: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# --- 2. MOTOR DE SEGURIDAD Y DATOS ---

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns:
                df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Usuario: {st.session_state.usuario_identificado.get('nombre', 'Admin')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“Hablamos desde la igualdad”")

# --- 4. PANEL ADMINISTRACIÓN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola Administrativa")
    t_reg, t_val, t_est, t_cob, t_aud, t_res = st.tabs([
        "📝 REGISTRO", "⚖️ VALIDACIÓN PESO", "✈️ ESTADOS", "💰 COBROS", "🔍 AUDITORÍA", "📊 RESUMEN"
    ])

    # [Pestañas de Registro, Validación, Estados, Cobros y Auditoría omitidas para brevedad, se mantienen igual]
    # ... (Mismas funciones anteriores para t_reg, t_val, t_est, t_cob, t_aud) ...
    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Inicial (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar Paquete"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Origen": f_pes, "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo); guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Guía registrada.")

    with t_res:
        st.subheader("Análisis de Operaciones por Estado")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            
            # Métricas Generales
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Kilos", f"{df['Peso_Origen'].sum():.1f} Kg")
            c2.metric("Total Paquetes", len(df))
            c3.metric("Pagado", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

            st.write("---")
            
            # SECCIÓN DETALLADA POR ESTADOS (Tu segunda petición)
            estados = ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]
            iconos = ["📦", "✈️", "🏠"]
            
            for i, est in enumerate(estados):
                df_filtrado = df[df['Estado'] == est]
                st.markdown(f'<div class="state-header">{iconos[i]} {est} ({len(df_filtrado)})</div>', unsafe_allow_html=True)
                if not df_filtrado.empty:
                    st.dataframe(df_filtrado[['ID_Barra', 'Cliente', 'Correo', 'Peso_Origen', 'Pago']], use_container_width=True)
                else:
                    st.info(f"No hay mercancía en estado: {est}")

# --- 5. PANEL CLIENTE (CON BUSCADOR) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u_data = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido nuevamente, {u_data["nombre"]}</div>', unsafe_allow_html=True)
    
    # BUSCADOR A LA DERECHA (Tu primera petición)
    col_t, col_b = st.columns([2, 1])
    col_t.subheader("📦 Mis Paquetes")
    busqueda_id = col_b.text_input("🔍 Buscar por ID de Guía", placeholder="Ej: TRK-1234")

    u_mail = u_data['correo']
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    # Filtrar si hay búsqueda
    if busqueda_id:
        mis_p = [p for p in mis_p if busqueda_id.lower() in str(p.get('ID_Barra', '')).lower()]

    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Estado actual: <b>{p["Estado"]}</b></p></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                est = p['Estado']
                c1.markdown(f'<div class="{"status-active" if any(x in est for x in ["RECIBIDO", "TRANSITO", "ENTREGADO"]) else "status-inactive"}">1. RECIBIDO</div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="{"status-active" if any(x in est for x in ["TRANSITO", "ENTREGADO"]) else "status-inactive"}">2. EN TRÁNSITO</div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="{"status-active" if "ENTREGADO" in est else "status-inactive"}">3. ENTREGADO</div>', unsafe_allow_html=True)
    else:
        st.info("No se encontraron paquetes con ese ID o no tienes paquetes asignados.")

# --- LOGIN Y REGISTRO (Se mantiene igual que antes) ---
elif not st.session_state.usuario_identificado:
    if rol_vista == "🔑 Portal Clientes":
        t_log, t_sig = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
        with t_sig:
            with st.form("signup_form"):
                s_nom = st.text_input("Nombre y Apellido"); s_doc = st.text_input("Documento ID"); s_ema = st.text_input("Correo"); s_pas = st.text_input("Clave", type="password")
                if st.form_submit_button("Registrarme"):
                    st.session_state.usuarios.append({"nombre": s_nom, "documento": s_doc, "correo": s_ema.lower().strip(), "password": hash_password(s_pas), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("✅ Cuenta creada.")
        with t_log:
            l_ema = st.text_input("Correo"); l_pas = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                user = next((u for u in st.session_state.usuarios if u['correo'] == l_ema.lower().strip() and u['password'] == hash_password(l_pas)), None)
                if user: st.session_state.usuario_identificado = user; st.rerun()
                else: st.error("Error de acceso.")
    else:
        ad_u = st.text_input("Admin"); ad_p = st.text_input("Pass", type="password")
        if st.button("Acceder Admin"):
            if ad_u == "admin" and ad_p == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
