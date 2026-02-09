import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTILO WEB CONSOLIDADO) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Fondo y Tipografía */
    .main { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
    
    /* Estilo de Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border-radius: 8px 8px 0px 0px; padding: 12px 24px; border: 1px solid #e0e0e0;
        font-weight: 600; color: #4a5568;
    }
    .stTabs [aria-selected="true"] { background-color: #0080FF !important; color: white !important; border: 1px solid #0080FF !important; }

    /* Tarjetas de Métricas (Resumen) */
    .metric-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 5px solid #0080FF;
        text-align: center; margin-bottom: 20px;
    }
    .metric-card h3 { color: #0080FF; margin-top: 10px; font-size: 2em; }
    
    /* Cajas de Estado de Mercancía */
    .summary-box {
        background: #ffffff; border: 2px solid #edf2f7; padding: 20px;
        border-radius: 15px; text-align: center; transition: transform 0.2s;
    }
    .summary-box:hover { transform: translateY(-5px); border-color: #0080FF; }
    
    /* Diseño de Guías para Clientes */
    .p-card {
        background-color: #ffffff; padding: 30px; border-radius: 20px;
        border-left: 10px solid #0080FF; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.06);
    }
    
    /* Indicadores de Línea de Tiempo */
    .status-active { background: #0080FF; color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e2e8f0; color: #94a3b8; padding: 12px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
PRECIO_POR_KG = 5.0 # Puedes ajustar tu tarifa aquí

# --- 2. MOTOR DE PERSISTENCIA ---
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

# Inicializar inventario en sesión
if 'inventario' not in st.session_state: 
    st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuario_identificado' not in st.session_state: 
    st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL (BRANDING E IDENTIDAD) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación del Portal:", ["🔑 Acceso Clientes", "🔐 Administración"])
    
    st.write("---")
    st.info("“La existencia es un milagro”")
    st.info("“Hablamos desde la igualdad”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. PANEL ADMINISTRATIVO (JERARQUÍA SOLICITADA) ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola de Control Logístico")
    
    # Reordenamiento de pestañas para flujo de trabajo óptimo
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN PESO", "✈️ ESTADOS", "💰 COBROS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    t_reg, t_val, t_est, t_cob, t_aud, t_res = tabs

    # 1. REGISTRO DE MERCANCÍA
    with t_reg:
        st.subheader("Entrada de Nueva Carga")
        with st.form("registro_nuevo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_id = col1.text_input("Código de Barra / Tracking ID")
            f_cli = col1.text_input("Nombre Completo del Cliente")
            f_cor = col2.text_input("Correo Electrónico (para seguimiento)")
            f_pes = col2.number_input("Peso Inicial (Kg)", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Dar Entrada al Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo_p = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(), 
                        "Peso_Origen": f_pes, "Monto_USD": f_pes * PRECIO_POR_KG, 
                        "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", 
                        "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo_p)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"📦 ¡Excelente! Guía {f_id} registrada correctamente.")
                else:
                    st.error("Por favor completa los campos obligatorios.")

    # 2. VALIDACIÓN DE PESO
    with t_val:
        st.subheader("Validación y Corrección de Pesos")
        if st.session_state.inventario:
            guia_v = st.selectbox("Seleccione Guía para re-pesar:", [p["ID_Barra"] for p in st.session_state.inventario])
            paquete = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_v), None)
            
            if paquete:
                st.write(f"**Detalles:** {paquete['Cliente']} | Peso actual registrado: {paquete['Peso_Origen']} Kg")
                nuevo_p = st.number_input("Peso Real Validado (Kg)", min_value=0.0, value=float(paquete['Peso_Origen']))
                if st.button("Actualizar y Validar"):
                    paquete['Peso_Origen'] = nuevo_p
                    paquete['Monto_USD'] = nuevo_p * PRECIO_POR_KG
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("✅ Peso validado y cobro actualizado.")
                    st.rerun()

    # 3. ESTADOS DE TRASLADO
    with t_est:
        st.subheader("Actualización de Fase Logística")
        if st.session_state.inventario:
            sel_id = st.selectbox("Guía a mover:", [p["ID_Barra"] for p in st.session_state.inventario])
            nuevo_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Confirmar Movimiento"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_id:
                        p["Estado"] = nuevo_st
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.success(f"🚚 Guía {sel_id} ahora está: {nuevo_st}")
                        st.rerun()

    # 4. COBROS Y FACTURACIÓN
    with t_cob:
        st.subheader("Control de Pagos Pendientes")
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        if pendientes:
            for idx, p in enumerate(pendientes):
                c_a, c_b = st.columns([4, 1])
                c_a.warning(f"**Guía:** {p['ID_Barra']} | **Cliente:** {p['Cliente']} | **Monto:** ${p['Monto_USD']:.2f}")
                if c_b.button("Marcar Pagado", key=f"pay_{idx}"):
                    p["Pago"] = "PAGADO"
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.rerun()
        else:
            st.success("🎉 No hay cobros pendientes por el momento.")

    # 5. AUDITORÍA (BUSCADOR COMPLETO)
    with t_aud:
        st.subheader("Auditoría de Inventario Global")
        if st.session_state.inventario:
            df_aud = pd.DataFrame(st.session_state.inventario)
            query = st.text_input("🔍 Buscar por Guía, Cliente o Correo...")
            if query:
                df_aud = df_aud[df_aud.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)]
            st.dataframe(df_aud, use_container_width=True)
            st.download_button("📥 Exportar a CSV", df_aud.to_csv(index=False).encode('utf-8'), "IACargo_Auditoria.csv", "text/csv")

    # 6. RESUMEN (DASHBOARD FINAL)
    with t_res:
        st.subheader("Estado General de la Operación")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            # Métricas Superior
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metric-card">⚖️<br>Kilos Totales<br><h3>{df["Peso_Origen"].sum():.1f} Kg</h3></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card">📦<br>Total Guías<br><h3>{len(df)}</h3></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card">💰<br>Recaudación<br><h3>${df[df["Pago"]=="PAGADO"]["Monto_USD"].sum():.2f}</h3></div>', unsafe_allow_html=True)
            
            st.write("---")
            # Detalle por fase
            st.write("### Detalle por Fase de Traslado")
            c_rec = len(df[df['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"])
            c_tra = len(df[df['Estado'] == "EN TRANSITO"])
            c_ent = len(df[df['Estado'] == "ENTREGADO"])
            
            col1, col2, col3 = st.columns(3)
            col1.markdown(f'<div class="summary-box">📦 ALMACÉN<br><h2>{c_rec}</h2></div>', unsafe_allow_html=True)
            col2.markdown(f'<div class="summary-box">✈️ TRÁNSITO<br><h2>{c_tra}</h2></div>', unsafe_allow_html=True)
            col3.markdown(f'<div class="summary-box">🏠 ENTREGADO<br><h2>{c_ent}</h2></div>', unsafe_allow_html=True)

# --- 5. PANEL CLIENTE (INTERFAZ VISUAL) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Rastreador de Mi Mercancía")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Estatus Actual: <b>{p["Estado"]}</b></p></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                est = p['Estado']
                # Lógica de progreso
                c1.markdown(f'<div class="{"status-active" if any(x in est for x in ["RECIBIDO", "TRANSITO", "ENTREGADO"]) else "status-inactive"}">1. RECIBIDO</div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="{"status-active" if any(x in est for x in ["TRANSITO", "ENTREGADO"]) else "status-inactive"}">2. EN TRÁNSITO</div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="{"status-active" if "ENTREGADO" in est else "status-inactive"}">3. ENTREGADO</div>', unsafe_allow_html=True)
    else:
        st.info("Aún no tienes guías vinculadas a este correo electrónico.")

# --- 6. SISTEMA DE ACCESO ---
else:
    st.subheader("Bienvenido a IACargo.io")
    user_in = st.text_input("Usuario o Correo")
    pass_in = st.text_input("Contraseña", type="password")
    if st.button("Acceder al Portal", use_container_width=True):
        if user_in == "admin" and pass_in == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMINISTRADOR", "rol": "admin"}
            st.rerun()
        elif user_in:
            st.session_state.usuario_identificado = {"correo": user_in.lower(), "rol": "cliente"}
            st.rerun()
