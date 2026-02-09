import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IACargo.io | Sistema Logístico", layout="wide", page_icon="🚀")

# Intentar cargar el logo (Asegúrate de tener logo.png en GitHub)
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    st.caption("“La existencia es un milagro”")

# --- MOTOR DE DATOS (Tu lógica original) ---
PRECIO_POR_KG = 5.0
ARCHIVO_DB = "inventario_logistica.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        return pd.read_csv(ARCHIVO_DB).to_dict('records')
    return []

def guardar_datos(datos):
    df = pd.DataFrame(datos)
    df.to_csv(ARCHIVO_DB, index=False)

# Inicializar inventario en la sesión de Streamlit
if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos()

# --- MENÚ DE NAVEGACIÓN ---
menu = ["🏠 Inicio", "📦 Rastreo (Clientes)", "🔐 Panel Administrativo"]
choice = st.sidebar.selectbox("Seleccione Portal", menu)

# --- PORTAL DE CLIENTE (RASTREO) ---
if choice == "📦 Rastreo (Clientes)":
    st.header("🔍 Rastreo de Paquete")
    id_buscar = st.text_input("Ingrese su ID de paquete:")
    if st.button("Buscar"):
        encontrado = False
        for p in st.session_state.inventario:
            if str(p["ID_Barra"]) == id_buscar:
                st.success(f"¡Paquete Localizado!")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Cliente:** {p['Cliente']}")
                    st.write(f"**Estado:** {p['Estado']}")
                    st.write(f"**Descripción:** {p['Descripcion']}")
                with col2:
                    st.write(f"**Monto:** ${p['Monto_USD']:.2f}")
                    st.write(f"**Estatus Pago:** {p['Pago']}")
                    st.write(f"**Fecha Registro:** {p['Fecha_Registro']}")
                encontrado = True
        if not encontrado:
            st.error("ID no encontrado. Verifique sus datos.")

# --- PANEL ADMINISTRATIVO ---
elif choice == "🔐 Panel Administrativo":
    st.header("⚙️ Gestión de Operaciones")
    
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Acceder"):
            if user == "admin" and pw == "admin123":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    else:
        if st.sidebar.button("🔒 Cerrar Sesión"):
            st.session_state.admin_auth = False
            st.rerun()

        tab1, tab2, tab3, tab4 = st.tabs(["📦 Registro", "⚖️ Pesaje", "💰 Cobros", "📋 Reporte"])

        with tab1:
            st.subheader("Nuevo Registro")
            c1, c2 = st.columns(2)
            id_p = c1.text_input("ID Único")
            cli = c1.text_input("Cliente")
            cor = c2.text_input("Correo")
            des = c2.text_area("Contenido")
            peso = st.number_input("Peso en báscula (kg)", min_value=0.0)
            
            if st.button("Registrar y Cotizar"):
                monto = peso * PRECIO_POR_KG
                nuevo = {
                    "ID_Barra": id_p, "Cliente": cli, "Correo": cor,
                    "Descripcion": des, "Peso_Origen": peso, "Peso_Almacen": 0.0,
                    "Monto_USD": monto, "Estado": "Recogido en casa", "Pago": "PENDIENTE",
                    "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario)
                st.success(f"✅ Registrado. Cotización: ${monto}")

        with tab2:
            st.subheader("Validación de Peso")
            id_v = st.selectbox("Paquete a pesar", [p["ID_Barra"] for p in st.session_state.inventario])
            p_real = st.number_input("Peso en almacén (kg)", min_value=0.0)
            if st.button("Validar Diferencia"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == id_v:
                        p["Peso_Almacen"] = p_real
                        diff = abs(p_real - p["Peso_Origen"])
                        if diff > (p["Peso_Origen"] * 0.05):
                            p["Estado"] = "🔴 RETENIDO: DISCREPANCIA"
                            st.error(f"Alerta: Diferencia de {diff:.2f} kg detectada.")
                        else:
                            p["Estado"] = "🟢 VERIFICADO"
                            st.success("Peso dentro del rango permitido.")
                        guardar_datos(st.session_state.inventario)

        with tab3:
            st.subheader("Gestión de Pagos")
            id_pago = st.selectbox("Paquete para cobrar", [p["ID_Barra"] for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"])
            if st.button("Confirmar Pago"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == id_pago:
                        p["Pago"] = "PAGADO"
                        st.balloons()
                guardar_datos(st.session_state.inventario)

        with tab4:
            st.subheader("Reporte de Auditoría")
            if st.session_state.inventario:
                st.dataframe(pd.DataFrame(st.session_state.inventario))
            else:
                st.write("No hay datos.")

# --- PANTALLA DE INICIO ---
else:
    st.markdown("<h1 style='text-align: center;'>Bienvenido a IACargo.io</h1>", unsafe_allow_html=True)
    st.write("---")
    st.info("Utilice el menú lateral para acceder al portal de clientes o administración.")
    st.image("https://images.unsplash.com/photo-1566232392379-afd9298e6a46?auto=format&fit=crop&q=80&w=1000")
