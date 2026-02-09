import streamlit as st
import pandas as pd
import os
import smtplib
import random
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IACargo.io | Full Evolution", layout="wide", page_icon="🚀")

# Estilos UI/UX
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .p-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-active { background: #0080FF; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e9ecef; color: #adb5bd; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# --- 2. MOTOR DE FUNCIONES ---

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

# Inicialización
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL (LOGO RESTAURADO) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")

# --- 4. PANEL CLIENTE (CON LÍNEA DE TIEMPO) ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mi Centro de Seguimiento")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Estado: <b>{p["Estado"]}</b></p></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                est = p['Estado']
                if "RECIBIDO" in est or "TRANSITO" in est or "ENTREGADO" in est:
                    c1.markdown('<div class="status-active">1. RECIBIDO</div>', unsafe_allow_html=True)
                else: c1.markdown('<div class="status-inactive">1. RECIBIDO</div>', unsafe_allow_html=True)
                if "TRANSITO" in est or "ENTREGADO" in est:
                    c2.markdown('<div class="status-active">2. EN TRÁNSITO</div>', unsafe_allow_html=True)
                else: c2.markdown('<div class="status-inactive">2. EN TRÁNSITO</div>', unsafe_allow_html=True)
                if "ENTREGADO" in est:
                    c3.markdown('<div class="status-active">3. ENTREGADO</div>', unsafe_allow_html=True)
                else: c3.markdown('<div class="status-inactive">3. ENTREGADO</div>', unsafe_allow_html=True)
    else: st.info("No hay paquetes asociados.")

# --- 5. PANEL ADMINISTRACIÓN (DASHBOARD COMPLETO) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola Administrativa")
    t_res, t_reg, t_est, t_cob, t_aud = st.tabs(["📊 RESUMEN", "📝 REGISTRO", "⚖️ ESTADOS", "💰 COBROS", "🔍 AUDITORÍA"])

    with t_res:
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            c1, c2, c3 = st.columns(3)
            c1.metric("Kilos Totales", f"{df['Peso_Origen'].sum()} Kg")
            c2.metric("Guías Activas", len(df))
            c3.metric("Recaudación", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum()}")
            st.bar_chart(df.groupby(df['Fecha_Registro'].dt.date).size())

    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking")
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Guardar"):
                st.session_state.inventario.append({
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor, "Peso_Origen": f_pes,
                    "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                })
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Registrado.")

    with t_est:
        if st.session_state.inventario:
            sel = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            nuevo_e = st.selectbox("Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel:
                        p["Estado"] = nuevo_e
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.success("✅ Actualizado.")
                        st.rerun()

    with t_cob:
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        for idx, p in enumerate(pendientes):
            col_a, col_b = st.columns([3, 1])
            col_a.warning(f"{p['ID_Barra']} - ${p['Monto_USD']}")
            if col_b.button("Cobrar", key=f"pay_{idx}"):
                p["Pago"] = "PAGADO"
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_aud:
        st.subheader("Auditoría de Inventario")
        if st.session_state.inventario:
            df_aud = pd.DataFrame(st.session_state.inventario)
            busqueda = st.text_input("🔍 Buscar por Código de Barra / Guía")
            if busqueda:
                df_aud = df_aud[df_aud['ID_Barra'].str.contains(busqueda, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            
            st.download_button(
                label="📥 Descargar Inventario Completo (CSV)",
                data=df_aud.to_csv(index=False).encode('utf-8'),
                file_name=f"Auditoria_IACargo_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# --- 6. ACCESO ---
elif rol_vista == "🔑 Portal Clientes":
    st.subheader("Portal Clientes")
    lc, lp = st.text_input("Correo"), st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if lc == "test@test.com": # Ajustar a tu lógica de usuarios
            st.session_state.usuario_identificado = {"correo": lc, "rol": "cliente"}
            st.rerun()

elif rol_vista == "🔐 Administración":
    au, ap = st.text_input("Admin User"), st.text_input("Admin Pass", type="password")
    if st.button("Acceder Admin"):
        if au == "admin" and ap == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
            st.rerun()
