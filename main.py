import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .p-card {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3); padding: 25px; border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); margin-bottom: 20px;
    }
    .welcome-text { color: #1e3a8a; font-weight: 900; font-size: 35px; margin-bottom: 5px; }
    .info-msg { 
        background: rgba(255, 255, 255, 0.5); padding: 15px; border-radius: 12px;
        border-left: 5px solid #0080ff; color: #1e3a8a; font-size: 16px; margin-bottom: 25px;
    }
    .state-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0080ff 100%);
        color: white; padding: 15px 25px; border-radius: 15px; margin: 20px 0;
    }
    .stButton>button { border-radius: 12px; height: 3em; font-weight: 700; text-transform: uppercase; }
    .btn-eliminar button { background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_KG = 5.0

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
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ DE ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro Inicial")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            if st.form_submit_button("Registrar en Sistema"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes*5, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success(f"✅ Guía {f_id} registrada.")

    with t_aud:
        col_a1, col_a2 = st.columns([3, 1])
        with col_a1: st.subheader("Historial y Edición")
        with col_a2: ver_papelera = st.checkbox("🗑️ Ver Papelera")

        if ver_papelera:
            if st.session_state.papelera:
                st.dataframe(pd.DataFrame(st.session_state.papelera), use_container_width=True)
                guia_res = st.selectbox("Restaurar ID:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("♻️ Restaurar Paquete"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
            else: st.info("Papelera vacía.")
        else:
            busq = st.text_input("🔍 Buscar:", key="aud_search")
            df_aud = pd.DataFrame(st.session_state.inventario)
            if busq: df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            
            st.write("---")
            st.markdown("### 🛠️ Panel de Edición y Anulación")
            guia_edit = st.selectbox("ID a editar:", [p["ID_Barra"] for p in st.session_state.inventario], key="edit_box")
            paq_edit = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_edit), None)
            if paq_edit:
                c1, c2 = st.columns(2)
                with c1:
                    new_id = st.text_input("ID", value=paq_edit['ID_Barra'])
                    new_cli = st.text_input("Cliente", value=paq_edit['Cliente'])
                with c2:
                    new_pes = st.number_input("Peso", value=float(paq_edit['Peso_Almacen']))
                    new_pago = st.selectbox("Pago", ["PENDIENTE", "PAGADO"], index=0 if paq_edit['Pago']=="PENDIENTE" else 1)
                
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾 Guardar"):
                        paq_edit.update({'ID_Barra': new_id, 'Cliente': new_cli, 'Peso_Almacen': new_pes, 'Pago': new_pago})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Guardado."); st.rerun()
                with b2:
                    st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar Paquete"):
                        st.session_state.papelera.append(paq_edit)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_edit]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # Las demás pestañas (t_val, t_cob, t_est, t_res) siguen su lógica habitual de gestión.

# --- 5. PANEL DEL CLIENTE (ACTUALIZADO CON TU MENSAJE) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    # LÓGICA DEL MENSAJE PARA CUENTAS VACÍAS
    if not mis_p:
        st.markdown("""
            <div class="info-msg">
                Por el momento no tienes paquetes asociados a tu perfil, si tu paquete fue recibido recientemente por nuestro equipo de trabajo pronto te reflejaremos de acuerdo a lo entregado
            </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("📋 Mis Envíos")
        for p in mis_p:
            fecha_p = str(p.get('Fecha_Registro', 'N/A'))[:10]
            st.markdown(f"""
                <div class="p-card">
                    <h3 style='margin:0; color:#1e3a8a;'>Guía: {p.get('ID_Barra')}</h3>
                    <p style='margin:5px 0;'>Estado: <b>{p.get('Estado')}</b></p>
                    <p style='margin:0; font-size:14px; color:#666;'>Fecha: {fecha_p}</p>
                </div>
            """, unsafe_allow_html=True)

# --- 6. ACCESO ---
else:
    t_l, t_s = st.tabs(["Ingresar", "Registro"])
    with t_s:
        with st.form("signup"):
            n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
            if st.form_submit_button("Crear Cuenta"):
                st.session_state.usuarios.append({"nombre": n, "correo": e.lower(), "password": hash_password(p), "rol": "cliente"})
                guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Listo.")
    with t_l:
        le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
        if st.button("Iniciar Sesión"):
            if le == "admin" and lp == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            usr = next((u for u in st.session_state.usuarios if u['correo'] == le.lower() and u['password'] == hash_password(lp)), None)
            if usr: st.session_state.usuario_identificado = usr; st.rerun()
            else: st.error("No se encontró el usuario.")
