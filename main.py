import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IACargo.io | Evolution", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .p-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-active { background: #0080FF; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e9ecef; color: #adb5bd; padding: 10px; border-radius: 8px; text-align: center; }
    .alarm { background-color: #ff4b4b; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    .state-header { background: #0080FF; color: white; padding: 10px; border-radius: 8px; margin-top: 20px; font-weight: bold; }
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
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado.get('nombre', 'Admin')}")
        if st.button("Cerrar Sesión"): st.session_state.usuario_identificado = None; st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")

# --- 4. PANEL ADMINISTRACIÓN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola Administrativa")
    t_reg, t_val, t_cob, t_est, t_aud, t_res = st.tabs([
        "📝 REGISTRO", "⚖️ VALIDACIÓN PESO", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"
    ])

    # Pestaña 1: Registro (Peso Mensajero)
    with t_reg:
        st.subheader("Entrada de Mercancía (Mensajería)")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar Entrada"):
                nuevo = {
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                    "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False,
                    "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                }
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success(f"✅ Guía {f_id} registrada con {f_pes}kg (Mensajero).")

    # Pestaña 2: Validación (Alarma de Peso)
    with t_val:
        st.subheader("Validación en Almacén")
        if st.session_state.inventario:
            pendientes_val = [p for p in st.session_state.inventario if not p.get('Validado', False)]
            if pendientes_val:
                guia_v = st.selectbox("Guía para validar:", [p["ID_Barra"] for p in pendientes_val])
                paq = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_v), None)
                if paq:
                    st.write(f"**Peso registrado por mensajero:** {paq['Peso_Mensajero']} Kg")
                    peso_real = st.number_input("Peso de Báscula en Almacén (Kg)", min_value=0.0)
                    if st.button("Validar y Pesaje"):
                        paq['Peso_Almacen'] = peso_real
                        paq['Validado'] = True
                        paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        if abs(peso_real - paq['Peso_Mensajero']) > 0.1:
                            st.error(f"⚠️ ¡ALARMA! Diferencia de peso detectada ({abs(peso_real - paq['Peso_Mensajero']):.2f} Kg)")
                        else:
                            st.success("✅ Peso validado correctamente.")
            else: st.info("No hay paquetes pendientes de validación.")

    # Pestaña 3: Cobros (Seccionados)
    with t_cob:
        st.subheader("Estado de Cuentas")
        df_c = pd.DataFrame(st.session_state.inventario)
        if not df_c.empty:
            hoy = datetime.now()
            # Lógica de Atrasados (>15 días sin pago)
            def clasificar_pago(row):
                if row['Pago'] == 'PAGADO': return 'PAGADO'
                fecha = pd.to_datetime(row['Fecha_Registro'])
                if (hoy - fecha).days > 15: return 'ATRASADO'
                return 'PENDIENTE'
            
            df_c['Estatus_Cobro'] = df_c.apply(clasificar_pago, axis=1)
            
            col_p, col_pn, col_at = st.columns(3)
            with col_p:
                st.write("✅ **PAGADOS**")
                st.dataframe(df_c[df_c['Estatus_Cobro'] == 'PAGADO'][['ID_Barra', 'Monto_USD']], hide_index=True)
            with col_pn:
                st.write("⏳ **PENDIENTES**")
                st.dataframe(df_c[df_c['Estatus_Cobro'] == 'PENDIENTE'][['ID_Barra', 'Monto_USD']], hide_index=True)
            with col_at:
                st.write("🚨 **ATRASADOS (>15 días)**")
                st.dataframe(df_c[df_c['Estatus_Cobro'] == 'ATRASADO'][['ID_Barra', 'Monto_USD']], hide_index=True)

    # Resto de pestañas...
    with t_est:
        st.subheader("Fases de Traslado")
        if st.session_state.inventario:
            sel_id = st.selectbox("Actualizar Estatus:", [p["ID_Barra"] for p in st.session_state.inventario])
            new_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Fase"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_id: p["Estado"] = new_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_aud:
        st.subheader("Auditoría Global")
        if st.session_state.inventario:
            st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True)

    with t_res:
        st.subheader("Resumen General")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            c1, c2, c3 = st.columns(3)
            c1.metric("Kg Totales (Validado)", f"{df['Peso_Almacen'].sum():.1f} Kg")
            c2.metric("Paquetes", len(df))
            c3.metric("Recaudado", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

# --- 5. PANEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u_data = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u_data["nombre"]}</div>', unsafe_allow_html=True)
    
    col_t, col_b = st.columns([2, 1])
    col_t.subheader("📦 Mis Paquetes")
    busqueda_id = col_b.text_input("🔍 Buscar Guía")

    u_mail = u_data['correo']
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if busqueda_id: mis_p = [p for p in mis_p if busqueda_id.lower() in str(p.get('ID_Barra', '')).lower()]

    for p in mis_p:
        with st.container():
            st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Estado: <b>{p["Estado"]}</b></p></div>', unsafe_allow_html=True)

# --- 6. ACCESO ---
else:
    if rol_vista == "🔑 Portal Clientes":
        t_l, t_s = st.tabs(["Login", "Registro"])
        with t_s:
            with st.form("signup"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Registrar"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Cuenta creada.")
        with t_l:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Error.")
    else:
        ad_u = st.text_input("Admin"); ad_p = st.text_input("Pass", type="password")
        if st.button("Acceso Admin"):
            if ad_u == "admin" and ad_p == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
