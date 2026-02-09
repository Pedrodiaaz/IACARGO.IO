import streamlit as st

# Configuración inicial
st.set_page_config(page_title="IACargo.io", layout="wide")

# Interfaz de Usuario
st.title("🚀 IACargo.io")
st.subheader("Logística Inteligente | Evolución en Movimiento")

# Barra Lateral (Sidebar)
st.sidebar.image("https://raw.githubusercontent.com/tu-usuario/iacargo/main/logo.png", width=200) # Preparado para el logo
st.sidebar.title("Navegación")
opcion = st.sidebar.selectbox("Ir a:", ["Inicio", "Rastreo de Carga", "Panel Admin"])

if opcion == "Inicio":
    st.write("### Bienvenido a la nueva era del transporte.")
    st.info("Estamos configurando los últimos detalles de tu flota.")

elif opcion == "Rastreo de Carga":
    id_carga = st.text_input("Introduce el ID de tu carga:")
    if st.button("Buscar"):
        st.warning(f"Buscando carga {id_carga}... (Simulación)")

elif opcion == "Panel Admin":
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if user == "admin" and clave == "1234":
            st.success("Acceso concedido")
        else:
            st.error("Credenciales incorrectas")
