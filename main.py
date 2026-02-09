import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IACargo.io | Dashboard", layout="wide", page_icon="🚀")

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS ---
PRECIO_POR_KG = 5.0
ARCHIVO_DB = "inventario_logistica.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        return pd.read_csv(ARCHIVO_DB).to_dict('records')
    return []

def guardar_datos(datos):
    df = pd.DataFrame(datos)
    df.to_csv(ARCHIVO_DB, index=False)

if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos()

# --- SIDEBAR CON LOGO ---
with st.sidebar:
    # Intenta cargar el logo que ya tienes arriba
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    
    st.write("---")
    st.subheader("Navegación")
    rol = st.radio("Seleccione su Rol:", ["🌐 Portal Cliente", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")

# ==========================================
# INTERFAZ 1: PORTAL CLIENTE (RASTREO)
# ==========================================
if rol == "🌐 Portal Cliente":
    st.title("📦 Seguimiento de Envíos")
    st.markdown("Consulta el estado de tu carga en tiempo real.")
    
    with st.container():
        col_busqueda, _ = st.columns([2, 1])
        id_buscar = col_busqueda.text_input("Introduce tu ID de Tracking:", placeholder="Ej: IAC-12345")
        
        if st.button("Rastrear Paquete"):
            paquete = next((p for p in st.session_state.inventario if str(p["ID_Barra"]) == id_buscar), None)
            
            if paquete:
                st.success(f"Paquete Encontrado")
                c1, c2, c3 = st.columns(3)
                c1.metric("Estado Actual", paquete['Estado'])
                c2.metric("Monto a Pagar", f"${paquete['Monto_USD']:.2f}")
                c3.metric("Pago", paquete['Pago'])
                
                with st.expander("Ver Detalles Completos"):
                    st.write(f"**Cliente:** {paquete['Cliente']}")
                    st.write(f"**Descripción:** {paquete['Descripcion']}")
                    st.write(f"**Fecha de Registro:** {paquete['Fecha_Registro']}")
            else:
                st.error("No se encontró ningún paquete con ese ID. Por favor, verifique.")

# ==========================================
# INTERFAZ 2: PANEL ADMINISTRATIVO (ADMIN)
# ==========================================
else:
    st.title("⚙️ Gestión de Operaciones IACargo")
    
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        # Login de seguridad
        col_l, _ = st.columns([1, 2])
        user = col_l.text_input("Usuario Admin")
        pw = col_l.text_input("Contraseña", type="password")
        if col_l.button("Acceder al Sistema"):
            if user == "admin" and pw == "admin123":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Credenciales Incorrectas")
    else:
        if st.sidebar.button("🔒 Cerrar Sesión Admin"):
            st.session_state.admin_auth = False
            st.rerun()

        # Menú de acciones Admin organizado por pestañas
        tab_reg, tab_pes, tab_cob, tab_aud = st.tabs([
            "📝 Registro Nuevo", "⚖️ Validación de Peso", "💰 Gestión de Cobros", "📊 Auditoría"
        ])

        # --- TAREA: REGISTRO ---
        with tab_reg:
            st.subheader("Entrada de Mercancía")
            with st.form("form_registro"):
                c1, c2 = st.columns(2)
                id_p = c1.text_input("ID del Paquete")
                cli = c1.text_input("Nombre del Cliente")
                cor = c2.text_input("Correo Electrónico")
                des = c2.text_area("Descripción de Contenido")
                peso_origen = st.number_input("Peso Inicial (Kg)", min_value=0.0)
                
                if st.form_submit_button("Guardar y Generar Cotización"):
                    monto = peso_origen * PRECIO_POR_KG
                    nuevo = {
                        "ID_Barra": id_p, "Cliente": cli, "Correo": cor,
                        "Descripcion": des, "Peso_Origen": peso_origen, "Peso_Almacen": 0.0,
                        "Monto_USD": monto, "Estado": "Recogido / En Espera", "Pago": "PENDIENTE",
                        "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario)
                    st.success(f"✅ Registrado. Cotización: ${monto:.2f} USD")

        # --- TAREA: PESAJE REAL ---
        with tab_pes:
            st.subheader("Báscula de Almacén")
            ids_pendientes = [p["ID_Barra"] for p in st.session_state.inventario if p["Peso_Almacen"] == 0.0]
            
            if ids_pendientes:
                id_v = st.selectbox("Seleccione ID para Validar:", ids_pendientes)
                peso_almacen = st.number_input("Peso Real detectado (Kg):", min_value=0.0)
                
                if st.button("Confirmar Pesaje"):
                    for p in st.session_state.inventario:
                        if p["ID_Barra"] == id_v:
                            p["Peso_Almacen"] = peso_almacen
                            diff = abs(peso_almacen - p["Peso_Origen"])
                            if diff > (p["Peso_Origen"] * 0.05):
                                p["Estado"] = "🔴 RETENIDO: DISCREPANCIA"
                                st.warning(f"Diferencia de {diff:.2f} Kg detectada. Paquete bloqueado para revisión.")
                            else:
                                p["Estado"] = "🟢 LISTO PARA ENVÍO"
                                st.success("Peso verificado con éxito.")
                            guardar_datos(st.session_state.inventario)
            else:
                st.info("No hay paquetes pendientes por pesar.")

        # --- TAREA: COBROS ---
        with tab_cob:
            st.subheader("Caja y Facturación")
            pendientes_pago = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
            if pendientes_pago:
                for p in pendientes_pago:
                    col_p1, col_p2 = st.columns([3, 1])
                    col_p1.write(f"**ID:** {p['ID_Barra']} | **Cliente:** {p['Cliente']} | **Monto:** ${p['Monto_USD']:.2f}")
                    if col_p2.button(f"Confirmar Pago", key=p['ID_Barra']):
                        p["Pago"] = "PAGADO"
                        guardar_datos(st.session_state.inventario)
                        st.rerun()
            else:
                st.success("No hay pagos pendientes.")

        # --- TAREA: AUDITORÍA ---
        with tab_aud:
            st.subheader("Inventario General")
            if st.session_state.inventario:
                df = pd.DataFrame(st.session_state.inventario)
                st.dataframe(df, use_container_width=True)
                st.download_button("Descargar Reporte Excel/CSV", df.to_csv(), "reporte_iacargo.csv")
            else:
                st.write("Sin datos registrados.")
