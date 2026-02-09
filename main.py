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
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .p-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-active { background: #0080FF; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e9ecef; color: #adb5bd; padding: 10px; border-radius: 8px; text-align: center; }
    .welcome-text { color: #0080FF; font-weight: bold; font-size: 24px; margin-bottom: 20px; }
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

# Inicialización
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

    with t_reg:
        st.subheader("Entrada de Mercancía")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente (Para vinculación)")
            f_pes = st.number_input("Peso Inicial (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar Paquete"):
                nuevo = {
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Origen": f_pes,
                    "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                }
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success(f"✅ Guía {f_id} registrada.")

    # [Resto de pestañas admin se mantienen igual que la versión anterior...]
    with t_val:
        st.subheader("Validación de Peso")
        if st.session_state.inventario:
            sel = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq = next((p for p in st.session_state.inventario if p["ID_Barra"] == sel), None)
            if paq:
                new_w = st.number_input("Peso Real (Kg)", value=float(paq['Peso_Origen']))
                if st.button("Actualizar Peso"):
                    paq['Peso_Origen'] = new_w
                    paq['Monto_USD'] = new_w * PRECIO_POR_KG
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("✅ Peso actualizado.")
                    st.rerun()

    with t_est:
        st.subheader("Fases de Traslado")
        if st.session_state.inventario:
            sel = st.selectbox("Actualizar Estatus:", [p["ID_Barra"] for p in st.session_state.inventario])
            new_e = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Confirmar Cambio"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel: p["Estado"] = new_e
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Estado actualizado.")
                st.rerun()

    with t_cob:
        st.subheader("Cobros")
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        for idx, p in enumerate(pendientes):
            c_a, c_b = st.columns([3, 1])
            c_a.warning(f"{p['ID_Barra']} - ${p['Monto_USD']}")
            if c_b.button("Pagar", key=f"cob_{idx}"):
                p["Pago"] = "PAGADO"
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_aud:
        st.subheader("Auditoría")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df, use_container_width=True)

    with t_res:
        st.subheader("Resumen")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            c1, c2, c3 = st.columns(3)
            c1.metric("Kilos", f"{df['Peso_Origen'].sum():.1f}")
            c2.metric("Guías", len(df))
            c3.metric("Recaudado", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

# --- 5. PANEL CLIENTE (CON REGISTRO DETALLADO) ---
elif not st.session_state.usuario_identificado and rol_vista == "🔑 Portal Clientes":
    st.title("📦 Acceso Portal Clientes")
    t_log, t_sig = st.tabs(["Iniciar Sesión", "Crear Cuenta"])

    with t_sig:
        st.subheader("Formulario de Registro")
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            s_nom = col1.text_input("Nombre y Apellido")
            s_doc = col1.text_input("Documento de Identidad")
            s_fec = col2.date_input("Fecha de Nacimiento", min_value=datetime(1940, 1, 1))
            s_dir = col2.text_input("Dirección de Domicilio")
            s_ema = st.text_input("Correo Electrónico")
            s_pas = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Registrarme"):
                if s_nom and s_ema and s_pas:
                    if any(u['correo'] == s_ema.lower().strip() for u in st.session_state.usuarios):
                        st.error("Este correo ya existe.")
                    else:
                        nuevo_u = {
                            "nombre": s_nom, "documento": s_doc, "nacimiento": str(s_fec),
                            "direccion": s_dir, "correo": s_ema.lower().strip(),
                            "password": hash_password(s_pas), "rol": "cliente"
                        }
                        st.session_state.usuarios.append(nuevo_u)
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                        st.success("✅ Cuenta creada. Ya puedes iniciar sesión.")
                else:
                    st.error("Nombre, correo y clave son obligatorios.")

    with t_log:
        st.subheader("Ingreso al Portal")
        l_ema = st.text_input("Correo")
        l_pas = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            user = next((u for u in st.session_state.usuarios if u['correo'] == l_ema.lower().strip() and u['password'] == hash_password(l_pas)), None)
            if user:
                st.session_state.usuario_identificado = user
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

# VISTA DEL CLIENTE LOGUEADO
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u_data = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido nuevamente {u_data["nombre"]}</div>', unsafe_allow_html=True)
    
    st.subheader("📦 Seguimiento de mis Paquetes")
    u_mail = u_data['correo']
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
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
        st.info("No hay paquetes asignados a tu correo todavía.")

# --- 6. ACCESO ADMIN ---
elif not st.session_state.usuario_identificado and rol_vista == "🔐 Administración":
    st.subheader("Consola Privada")
    ad_u = st.text_input("Admin User")
    ad_p = st.text_input("Admin Pass", type="password")
    if st.button("Acceder"):
        if ad_u == "admin" and ad_p == "admin123":
            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}
            st.rerun()
        else:
            st.error("No autorizado.")
