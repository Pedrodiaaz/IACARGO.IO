import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (RESTAURADA) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    .logo-animado { font-style: italic !important; font-family: 'Georgia', serif; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; animation: pulse 2.5s infinite; font-weight: 800; margin-bottom: 5px; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }
    .stTabs, .stForm, [data-testid="stExpander"], .p-card { background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px !important; padding: 20px; margin-bottom: 15px; color: white !important; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-pending { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .state-header { background: rgba(255, 255, 255, 0.1); border-left: 5px solid #3b82f6; color: #60a5fa !important; padding: 12px; border-radius: 8px; margin: 20px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .stButton>button { border-radius: 12px !important; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important; color: white !important; border: none !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100% !important; }
    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"

TARIFA_AEREO_KG = 5.0
TARIFA_MARITIMO_FT3 = 18.0

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

def calcular_monto(valor, tipo):
    return valor * (TARIFA_AEREO_KG if tipo == "Aéreo" else TARIFA_MARITIMO_FT3)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL (LOGO RECUPERADO) ---
with st.sidebar:
    st.markdown('<h1 class="logo-animado" style="font-size: 35px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre')}")
        if st.button("Cerrar Sesión", use_container_width=True): 
            st.session_state.usuario_identificado = None; st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMIN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # --- TAB AUDITORÍA/EDICIÓN (RESTAURADA) ---
    with t_aud:
        col_aud1, col_aud2 = st.columns([3, 1])
        with col_aud1: st.subheader("Buscador y Editor de Inventario")
        with col_aud2: ver_papelera = st.checkbox("🗑️ Papelera")

        if ver_papelera:
            if st.session_state.papelera:
                guia_res = st.selectbox("Restaurar Guía:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("♻️ Reintegrar al Inventario"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
            else: st.info("Sin registros en papelera.")
        else:
            busq_admin = st.text_input("🔍 Filtrar por ID o Cliente:", placeholder="Escribe para buscar...")
            df_full = pd.DataFrame(st.session_state.inventario)
            if busq_admin:
                df_full = df_full[df_full['ID_Barra'].astype(str).str.contains(busq_admin, case=False) | df_full['Cliente'].str.contains(busq_admin, case=False)]
            st.dataframe(df_full, use_container_width=True)

            if st.session_state.inventario:
                st.write("---")
                guia_ed = st.selectbox("Seleccionar para modificar:", [p["ID_Barra"] for p in st.session_state.inventario])
                paq_ed = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed), None)
                if paq_ed:
                    c1, c2, c3 = st.columns(3)
                    with c1: n_nom = st.text_input("Nombre", value=paq_ed['Cliente'])
                    with c2: n_pes = st.number_input("Peso/Medida", value=float(paq_ed['Peso_Almacen']))
                    with c3: n_tra = st.selectbox("Tipo", ["Aéreo", "Marítimo"], index=0 if paq_ed['Tipo_Traslado']=="Aéreo" else 1)
                    
                    if st.button("💾 Actualizar Registro"):
                        paq_ed.update({'Cliente': n_nom, 'Peso_Almacen': n_pes, 'Tipo_Traslado': n_tra, 'Monto_USD': calcular_monto(n_pes, n_tra)})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Cambios guardados."); st.rerun()
                    
                    st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar permanentemente"):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB RESUMEN (RESTAURADA CON BÚSQUEDA Y SECCIONES) ---
    with t_res:
        st.subheader("Estado Maestro de Mercancía")
        if st.session_state.inventario:
            busq_res = st.text_input("🔍 Buscar caja en resumen:", key="bus_res")
            df_res = pd.DataFrame(st.session_state.inventario)
            if busq_res:
                df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]

            for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                df_f = df_res[df_res['Estado'] == est]
                st.markdown(f'<div class="state-header"> {est} ({len(df_f)})</div>', unsafe_allow_html=True)
                if not df_f.empty:
                    st.table(df_f[['ID_Barra', 'Cliente', 'Tipo_Traslado', 'Peso_Almacen', 'Pago']])

    # (Las demás pestañas como Registro, Validación y Cobros mantienen su lógica de la versión anterior)
    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo")
            f_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo"])
            f_val_ini = st.number_input("Medida Inicial", min_value=0.0)
            f_mod = st.selectbox("Modalidad", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_val_ini, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": calcular_monto(f_val_ini, f_tra), "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo); guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Medida Real en Almacén", value=float(paq['Peso_Mensajero']))
            if st.button("⚖️ Confirmar Validación"):
                paq.update({'Peso_Almacen': v_real, 'Validado': True, 'Monto_USD': calcular_monto(v_real, paq['Tipo_Traslado'])})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        for p in [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']:
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                m_abono = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"cob_{p['ID_Barra']}")
                if st.button("Registrar Abono", key=f"btn_cob_{p['ID_Barra']}"):
                    p['Abonado'] += m_abono
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado:
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo')).lower() == str(u.get('correo')).lower()]
    busq_id = st.text_input("🔍 Localizar por ID / Tracking:")
    if busq_id: mis_p = [p for p in mis_p if busq_id.lower() in str(p['ID_Barra']).lower()]
    
    for p in mis_p:
        icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
        p_status = p.get('Pago', 'PENDIENTE')
        badge = "badge-paid" if p_status == "PAGADO" else "badge-pending"
        st.markdown(f'<div class="p-card"><span class="{badge}">{p_status}</span><br><b>{icon} #{p["ID_Barra"]}</b><br>Estado: {p["Estado"]}<br>Deuda: ${(p["Monto_USD"]-p["Abonado"]):.2f}</div>', unsafe_allow_html=True)
        if p['Monto_USD'] > 0: st.progress(min(p['Abonado']/p['Monto_USD'], 1.0))

# --- 6. ACCESO / LOGIN (RESTAURADO) ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.8, 1])
    with col_l2:
        st.markdown('<div style="text-align: center;"><div class="logo-animado" style="font-size: 80px;">IACargo.io</div><p style="color: #a78bfa !important;">“Evolución Logística a tu Alcance”</p></div>', unsafe_allow_html=True)
        t_login, t_sign = st.tabs(["Ingresar", "Registro"])
        with t_login:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Iniciar Sesión", use_container_width=True):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Acceso denegado.")
        with t_sign:
            with st.form("signup_restored"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear mi cuenta"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Cuenta lista!"); st.rerun()
