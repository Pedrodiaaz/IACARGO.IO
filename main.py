import streamlit as st
import pandas as pd

# Configuración profesional de la página
st.set_page_config(page_title="IACargo.io | Logística Inteligente", layout="wide", page_icon="🚀")

# --- BARRA LATERAL (SIDEBAR) ---
# RECUERDA: Cambia 'TU_USUARIO_GITHUB' por tu nombre real de usuario de GitHub
url_logo = "https://raw.githubusercontent.com/Pedrodiaaz/iacargo/main/logo.png"

with st.sidebar:
    try:
        st.image(url_logo, width=200)
    except:
        st.title("🚀 IACargo.io")
    
    st.write("---")
    st.title("Menú Principal")
    # Agregamos "Validación de Documentos" al menú
    menu = ["🏠 Inicio", "📦 Rastreo de Carga", "📄 Validación de Documentos", "👥 Gestión de Clientes", "🚢 Inventario/Flota", "🔐 Administración"]
    choice = st.selectbox("Navegación", menu)
    st.write("---")
    st.caption("Evolución en Logística v1.0")

# --- SECCIONES DEL MENÚ ---

if choice == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center; color: #0080FF;'>Bienvenido a IACargo.io</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px;'>La existencia es un milagro, la eficiencia es nuestra meta.</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Envíos Activos", "24", "+2")
    with col2:
        st.metric("Nuevas Solicitudes", "7", "-1")
    with col3:
        st.metric("Entregados hoy", "12", "+5")

elif choice == "📦 Rastreo de Carga":
    st.header("Seguimiento en Tiempo Real")
    guia = st.text_input("Introduce el Número de Guía o Tracking ID")
    if st.button("Rastrear Mercancía"):
        if guia:
            st.success(f"Buscando información para la guía: {guia}")
            st.info("📍 **Estado:** En tránsito | **Ubicación:** Hub Internacional")
        else:
            st.warning("Por favor, introduce un número válido.")

elif choice == "📄 Validación de Documentos":
    st.header("Centro de Validación Documental")
    st.write("Cargue los documentos para su verificación previa (Facturas, Packing List, BL).")
    
    uploaded_file = st.file_uploader("Seleccione el archivo (PDF, JPG, PNG)", type=["pdf", "jpg", "png"])
    tipo_doc = st.selectbox("Tipo de documento", ["Factura Comercial", "Packing List", "Certificado de Origen", "Otro"])
    
    if st.button("Enviar para Validación"):
        if uploaded_file is not None:
            st.success(f"El documento '{tipo_doc}' ha sido recibido. Nuestro equipo lo validará en breve.")
        else:
            st.error("Por favor, suba un archivo antes de enviar.")

elif choice == "👥 Gestión de Clientes":
    st.header("Base de Datos de Clientes")
    df_clientes = pd.DataFrame({
        'Cliente': ['Empresa A', 'Distribuidora B', 'Exportadora C'],
        'País': ['Venezuela', 'Panamá', 'España'],
        'Estado': ['Activo', 'Pendiente', 'Activo']
    })
    st.dataframe(df_clientes, use_container_width=True)

elif choice == "🚢 Inventario/Flota":
    st.header("Control de Unidades")
    st.write("Gestión de contenedores y espacios aéreos disponibles.")

elif choice == "🔐 Administración":
    st.header("Acceso de Seguridad")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if usuario == "admin" and clave == "1234":
            st.success("Acceso concedido.")
            st.balloons()
        else:
            st.error("Credenciales incorrectas.")
