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
    menu = ["🏠 Inicio", "📦 Rastreo de Carga", "👥 Gestión de Clientes", "🚢 Inventario/Flota", "🔐 Administración"]
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
    
    st.write("### Operaciones Recientes")
    st.info("Utilice el panel lateral para navegar entre las funciones del sistema.")

elif choice == "📦 Rastreo de Carga":
    st.header("Seguimiento en Tiempo Real")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        guia = st.text_input("Introduce el Número de Guía o Tracking ID")
    with col_b:
        st.write("##")
        boton = st.button("Rastrear Mercancía")
        
    if boton and guia:
        st.success(f"Buscando información para la guía: {guia}")
        st.progress(65)
        st.markdown("""
        * **Estado:** En tránsito
        * **Ubicación:** Aduana de destino (Puerto Cabello / Maiquetía)
        * **ETA Estimado:** 48 horas
        """)

elif choice == "👥 Gestión de Clientes":
    st.header("Base de Datos de Clientes")
    with st.expander("➕ Registrar Nuevo Cliente"):
        nombre = st.text_input("Nombre de la Empresa / Particular")
        correo = st.text_input("Correo Electrónico")
        if st.button("Guardar en Sistema"):
            st.success("Cliente registrado con éxito.")

    # Tabla de ejemplo de lo que será tu base de datos
    df_clientes = pd.DataFrame({
        'Cliente': ['Empresa A', 'Distribuidora B', 'Exportadora C'],
        'País': ['Venezuela', 'Panamá', 'España'],
        'Cargas Mes': [15, 8, 22],
        'Estado': ['Activo', 'Pendiente', 'Activo']
    })
    st.dataframe(df_clientes, use_container_width=True)

elif choice == "🚢 Inventario/Flota":
    st.header("Control de Unidades y Almacén")
    tab1, tab2, tab3 = st.tabs(["✈️ Aéreo", "🚢 Marítimo", "📦 Almacén"])
    with tab1:
        st.write("Disponibilidad de carga aérea inmediata.")
    with tab2:
        st.write("Seguimiento de contenedores en ruta transatlántica.")
    with tab3:
        st.write("Espacio disponible en depósitos.")

elif choice == "🔐 Administración":
    st.header("Acceso de Seguridad")
    col_c, col_d = st.columns(2)
    with col_c:
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Acceder"):
            if usuario == "admin" and clave == "1234":
                st.success("Bienvenido al núcleo del sistema.")
                st.balloons()
            else:
                st.error("Credenciales no válidas.")
