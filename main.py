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
    t_reg, t_val, t_cob, t_est, t_aud, t_res = st.tabs([
        "📝 REGISTRO", "⚖️ VALIDACIÓN PESO", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"
    ])

    with t_reg:
        st.subheader("Entrada de Mercancía (Mensajería)")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            if st.form_submit_button("Registrar Entrada"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False,
                        "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                        "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_id} registrada con {f_pes}kg.")
                else: st.error("Completa todos los campos.")

    with t_val:
        st.subheader("Báscula y Validación")
        if st.session_state.inventario:
            pendientes_val = [p for p in st.session_state.inventario if not p.get('Validado', False)]
            if pendientes_val:
                guia_v = st.selectbox("Guía para validar:", [p["ID_Barra"] for p in pendientes_val])
                paq = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_v), None)
                if paq:
                    # FIX: Uso de .get() para evitar el KeyError
                    peso_m = paq.get('Peso_Mensajero', paq.get('Peso_Origen', 0.0))
                    st.info(f"Cliente: {paq.get('Cliente', 'N/A')}")
                    st.write(f"**Peso registrado por mensajero:** {peso_m} Kg")
                    
                    peso_real = st.number_input("Peso de Báscula en Almacén (Kg)", min_value=0.0, value=float(peso_m))
                    if st.button("Confirmar Pesaje en Almacén"):
                        paq['Peso_Almacen'] = peso_real
                        paq['Peso_Mensajero'] = peso_m
                        paq['Validado'] = True
                        paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        
                        dif = abs(peso_real - peso_m)
                        if dif > 0.1:
                            st.error(f"⚠️ ¡ALARMA! Variación de peso detectada: {dif:.2f} Kg")
                        else:
                            st.success("✅ Peso validado sin alteraciones.")
                        st.rerun()
            else: st.info("No hay paquetes pendientes de validación.")
        else: st.info("Inventario vacío.")

    with t_cob:
        st.subheader("Gestión de Cobros")
        if st.session_state.inventario:
            df_c = pd.DataFrame(st.session_state.inventario)
            hoy = datetime.now()
            
            def clasificar(row):
                if row.get('Pago') == 'PAGADO': return 'PAGADO'
                f_reg = pd.to_datetime(row.get('Fecha_Registro', hoy))
                if (hoy - f_reg).days > 15: return 'ATRASADO'
                return 'PENDIENTE'
            
            df_c['Estatus_Pago'] = df_c.apply(clasificar, axis=1)
            
            c_pag, c_pen, c_atr = st.columns(3)
            with c_pag:
                st.write("✅ **PAGADOS**")
                st.dataframe(df_c[df_c['Estatus_Pago'] == 'PAGADO'][['ID_Barra', 'Monto_USD']], hide_index=True)
            with c_pen:
                st.write("⏳ **PENDIENTES**")
                df_p = df_c[df_c['Estatus_Pago'] == 'PENDIENTE']
                st.dataframe(df_p[['ID_Barra', 'Monto_USD']], hide_index=True)
                for idx, r in df_p.iterrows():
                    if st.button(f"Cobrar {r['ID_Barra']}", key=f"btn_{idx}"):
                        st.session_state.inventario[idx]['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.rerun()
            with c_atr:
                st.write("🚨 **ATRASADOS (+15 días)**")
                st.dataframe(df_c[df_c['Estatus_Pago'] == 'ATRASADO'][['ID_Barra', 'Monto_USD']], hide_index=True)

    with t_est:
        st.subheader("Actualizar Estado de Tránsito")
        if st.session_state.inventario:
            sel = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_est = st.selectbox("Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel: p["Estado"] = n_est
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Estado actualizado.")
                st.rerun()

    with t_aud:
        st.subheader("Historial Completo")
        if st.session_state.inventario:
            st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True)

    with t_res:
        st.subheader("Resumen de Operación")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            c1, c2, c3 = st.columns(3)
            c1.metric("Kilos Validados", f"{df['Peso_Almacen'].sum():.1f} Kg")
            c2.metric("Paquetes", len(df))
            c3.metric("Recaudado USD", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

# --- 5. PANEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    c_izq, c_der = st.columns([2, 1])
    c_izq.subheader("📦 Mis Paquetes")
    busqueda = c_der.text_input("🔍 Buscar Guía")
    
    mis_p = [p for p in st.session_state.inventario if p.get('Correo', '').lower() == u['correo'].lower()]
    if busqueda:
        mis_p = [p for p in mis_p if busqueda.lower() in p['ID_Barra'].lower()]
        
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Estado: {p["Estado"]}</p></div>', unsafe_allow_html=True)
    else: st.info("No hay paquetes asignados.")

# --- 6. ACCESO ---
else:
    if rol_vista == "🔑 Portal Clientes":
        t_l, t_s = st.tabs(["Login", "Registro"])
        with t_s:
            with st.form("signup"):
                n = st.text_input("Nombre Completo"); d = st.text_input("Documento ID"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Registrar Cuenta"):
                    if n and e and p:
                        st.session_state.usuarios.append({"nombre": n, "documento": d, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Registrado! Ya puedes loguear.")
        with t_l:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Entrar"):
                usr = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if usr: st.session_state.usuario_identificado = usr; st.rerun()
                else: st.error("Credenciales incorrectas.")
    else:
        ad_u = st.text_input("Admin User"); ad_p = st.text_input("Admin Pass", type="password")
        if st.button("Acceso Admin"):
            if ad_u == "admin" and ad_p == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
