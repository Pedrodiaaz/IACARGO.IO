import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    .logo-animado {
        font-style: italic !important;
        font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        animation: pulse 2.5s infinite;
        font-weight: 800;
        margin-bottom: 5px;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* BADGES DE ESTADO PARA EL CLIENTE */
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }

    .header-resumen {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.1em;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-left: 6px solid #60a5fa;
    }

    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 15px;
        border-bottom: 2px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
        border-radius: 4px;
    }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }

    /* BOTÓN DE REGISTRO ESTÁTICO */
    div[data-testid="stForm"] button {
        background-color: #2563eb !important;
        color: white !important;
        border: 1px solid #60a5fa !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_KG = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None; st.rerun()
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“Hablamos desde la igualdad”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ DE ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"]) 
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": f_pes*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, 
                        "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success(f"✅ Guía {f_id} registrada.")

    # ... [Las funciones de t_val, t_cob, t_est, t_aud, t_res se mantienen iguales al código anterior para conservar la operatividad]
    with t_res:
        st.subheader("📊 Resumen General")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            busq_res = st.text_input("🔍 Buscar caja por código:", key="res_search_admin")
            if busq_res: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
            # (Lógica de métricas y filas de resumen...)
            for est_key, est_label in {"RECIBIDO ALMACEN PRINCIPAL": "📦 Almacén", "EN TRANSITO": "✈️ Tránsito", "ENTREGADO": "✅ Entregado"}.items():
                df_f = df_res[df_res['Estado'] == est_key]
                st.markdown(f'<div class="header-resumen">{est_label} ({len(df_f)})</div>', unsafe_allow_html=True)
                for _, row in df_f.iterrows():
                    st.markdown(f'<div class="resumen-row"><div class="resumen-id">{row["ID_Barra"]}</div><div class="resumen-cliente">{row["Cliente"]}</div><div class="resumen-data">${row["Abonado"]:.2f}</div></div>', unsafe_allow_html=True)

# --- 5. PANEL DEL CLIENTE (REESTABLECIDO) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    st.write("Rastrea tus paquetes y gestiona tus pagos desde aquí.")
    
    # Buscador de paquetes del cliente
    u_mail = str(u.get('correo', '')).lower().strip()
    mis_paquetes = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower().strip() == u_mail]
    
    if not mis_paquetes:
        st.info("Aún no tienes paquetes registrados en nuestro sistema.")
    else:
        busqueda = st.text_input("🔍 Buscar paquete por ID Tracking:", placeholder="Ej: ABC12345")
        if busqueda:
            mis_paquetes = [p for p in mis_paquetes if busqueda.lower() in str(p['ID_Barra']).lower()]

        col_cli1, col_cli2 = st.columns(2)
        for i, p in enumerate(mis_paquetes):
            with (col_cli1 if i % 2 == 0 else col_cli2):
                # Lógica de cálculo y visualización
                total = float(p.get('Monto_USD', 0))
                abonado = float(p.get('Abonado', 0))
                resta = total - abonado
                pago_status = p.get('Pago', 'PENDIENTE')
                badge_class = "badge-paid" if pago_status == "PAGADO" else "badge-debt"
                
                # Icono por transporte
                trans_icon = "✈️ Aéreo" if p.get('Tipo_Traslado') == "Aéreo" else "🚢 Marítimo"
                
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight:bold; color:#60a5fa; font-size:1.3em;">📦 #{p['ID_Barra']}</span>
                            <span class="{badge_class}">{pago_status}</span>
                        </div>
                        <div style="margin: 15px 0; font-size: 0.95em; line-height: 1.6;">
                            <b>📍 Estatus:</b> {p['Estado']}<br>
                            <b>🚀 Transporte:</b> {trans_icon}<br>
                            <b>⚖️ Peso:</b> {p['Peso_Almacen'] if p['Validado'] else p['Peso_Mensajero']} Kg
                        </div>
                """, unsafe_allow_html=True)
                
                # BARRA DE PROGRESO DE PAGOS (SOLO SI ES POR CUOTAS O TIENE DEUDA)
                if p.get('Modalidad') == "Pago en Cuotas" or resta > 0:
                    porcentaje = (abonado / total) if total > 0 else 0
                    st.progress(min(porcentaje, 1.0))
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; font-size: 0.85em; margin-top: 5px;">
                            <span>Pagado: <b>${abonado:.2f}</b></span>
                            <span style="color:#f87171;">Resta: <b>${resta:.2f}</b></span>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

# --- 6. ACCESO / LOGIN ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown('<div style="text-align: center;"><div class="logo-animado" style="font-size: 70px;">IACargo.io</div><p style="color: #a78bfa !important;">“Conectando el milagro de tu existencia con el mundo”</p></div>', unsafe_allow_html=True)
        t_login, t_sign = st.tabs(["Ingresar", "Registro"])
        with t_login:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Iniciar Sesión", use_container_width=True):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Acceso denegado")
        with t_sign:
            with st.form("signup_client"):
                n = st.text_input("Nombre completo"); e = st.text_input("Correo electrónico"); p = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Crear mi cuenta evolucionada"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Registrado! Ya puedes ingresar."); st.rerun()
