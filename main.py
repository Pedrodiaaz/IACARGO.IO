import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IACargo.io | Evolution", layout="wide", page_icon="🚀")

# Estilos UI/UX
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .p-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 6px solid #0080FF; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-active { background: #0080FF; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e9ecef; color: #adb5bd; padding: 10px; border-radius: 8px; text-align: center; }
    .summary-box { background: white; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# --- 2. MOTOR DE DATOS ---
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
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Conectado: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“Hablamos desde la igualdad”")

# --- 4. PANEL ADMINISTRACIÓN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola Administrativa")
    t_res, t_reg, t_val, t_est, t_cob, t_aud = st.tabs([
        "📊 RESUMEN", "📝 REGISTRO", "⚖️ VALIDACIÓN PESO", "✈️ ESTADOS", "💰 COBROS", "🔍 AUDITORÍA"
    ])

    # Pestaña Resumen (Detallado por estados)
    with t_res:
        st.subheader("General de Inventario y Traslados")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            
            # Métricas Principales
            c1, c2, c3 = st.columns(3)
            c1.metric("Kilos Totales", f"{df['Peso_Origen'].sum():.2f} Kg")
            c2.metric("Guías Registradas", len(df))
            c3.metric("Recaudación", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")
            
            st.write("---")
            st.subheader("📍 Detalle de Mercancía por Fase")
            
            # Conteo de estados
            recibidos = len(df[df['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"])
            transito = len(df[df['Estado'] == "EN TRANSITO"])
            entregados = len(df[df['Estado'] == "ENTREGADO"])

            # Mostrar bloques informativos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="summary-box">📦<br><b>RECIBIDOS</b><br><h2>{recibidos}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="summary-box">✈️<br><b>EN TRÁNSITO</b><br><h2>{transito}</h2></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="summary-box">🏠<br><b>ENTREGADOS</b><br><h2>{entregados}</h2></div>', unsafe_allow_html=True)
            
            # Tabla resumida de guías por fase
            st.write("### Listado por Estado")
            estado_filtro = st.selectbox("Filtrar tabla por fase:", ["Todos", "RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if estado_filtro == "Todos":
                st.dataframe(df[['ID_Barra', 'Cliente', 'Estado', 'Pago']], use_container_width=True)
            else:
                st.dataframe(df[df['Estado'] == estado_filtro][['ID_Barra', 'Cliente', 'Estado', 'Pago']], use_container_width=True)
        else:
            st.info("No hay datos registrados aún.")

    # Pestaña Registro
    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo Electrónico")
            f_pes = st.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Guardar Paquete"):
                nuevo = {
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(), "Peso_Origen": f_pes,
                    "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                }
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success(f"✅ Guía {f_id} registrada.")

    # Pestaña Validación de Peso
    with t_val:
        st.subheader("Báscula y Validación")
        if st.session_state.inventario:
            guia_v = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paquete_v = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_v), None)
            if paquete_v:
                st.write(f"**Cliente:** {paquete_v['Cliente']} | **Peso actual:** {paquete_v['Peso_Origen']} Kg")
                nuevo_p = st.number_input("Corregir Peso (Kg)", min_value=0.0, value=float(paquete_v['Peso_Origen']))
                if st.button("Validar Nuevo Peso"):
                    paquete_v['Peso_Origen'] = nuevo_p
                    paquete_v['Monto_USD'] = nuevo_p * PRECIO_POR_KG
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("✅ Peso y monto actualizados.")
                    st.rerun()

    # Pestaña Estados (Actualización de fase)
    with t_est:
        if st.session_state.inventario:
            sel = st.selectbox("Guía a mover:", [p["ID_Barra"] for p in st.session_state.inventario])
            nuevo_e = st.selectbox("Nueva Fase:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Fase"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel:
                        p["Estado"] = nuevo_e
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.success("✅ Estatus actualizado.")
                        st.rerun()

    # Pestaña Cobros
    with t_cob:
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        if pendientes:
            for idx, p in enumerate(pendientes):
                c_a, c_b = st.columns([3, 1])
                c_a.warning(f"Guía: {p['ID_Barra']} - ${p['Monto_USD']}")
                if c_b.button("Pagar", key=f"p_{idx}"):
                    p["Pago"] = "PAGADO"
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.rerun()
        else: st.success("Todo está al día.")

    # Pestaña Auditoría
    with t_aud:
        st.subheader("Historial Completo")
        if st.session_state.inventario:
            df_aud = pd.DataFrame(st.session_state.inventario)
            busq = st.text_input("🔍 Buscar guía o cliente")
            if busq:
                df_aud = df_aud[(df_aud['ID_Barra'].str.contains(busq, case=False)) | (df_aud['Cliente'].str.contains(busq, case=False))]
            st.dataframe(df_aud, use_container_width=True)
            st.download_button("📥 Descargar Inventario", df_aud.to_csv(index=False).encode('utf-8'), "IACargo_Inv.csv", "text/csv")

# --- 5. PANEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Seguimiento de Carga")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Fase actual: <b>{p["Estado"]}</b></p></div>', unsafe_allow_html=True)
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
    else: st.info("No tienes guías registradas.")

# --- 6. ACCESO ---
else:
    st.subheader("Identificación")
    u = st.text_input("Usuario / Correo")
    p = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if u == "admin" and p == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
            st.rerun()
        else:
            st.session_state.usuario_identificado = {"correo": u.lower(), "rol": "cliente"}
            st.rerun()
