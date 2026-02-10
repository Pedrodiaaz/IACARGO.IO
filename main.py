import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
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
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .state-header { background: rgba(255, 255, 255, 0.1); border-left: 5px solid #3b82f6; color: #60a5fa !important; padding: 12px; border-radius: 8px; margin: 20px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .stButton>button { border-radius: 12px !important; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important; color: white !important; border: none !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100% !important; }
    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS Y TARIFAS ---
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
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    return valor * TARIFA_MARITIMO_FT3

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None; st.rerun()
    else: rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
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
            f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
            f_val_ini = st.number_input("Medida Inicial (Kg o ft³)", min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_val_ini, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": calcular_monto(f_val_ini, f_tra), "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra,
                        "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success(f"✅ Guía {f_id} registrada.")

    with t_val:
        st.subheader("Validación de Medidas")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para Validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            tipo = paq.get('Tipo_Traslado', 'Aéreo')
            medida = "Kg" if tipo == "Aéreo" else "ft³"
            valor_real = st.number_input(f"Medida Real ({medida})", min_value=0.0, value=float(paq['Peso_Mensajero']), step=0.1)
            if st.button("⚖️ Validar y Actualizar Monto"):
                paq['Peso_Almacen'] = valor_real; paq['Validado'] = True; paq['Monto_USD'] = calcular_monto(valor_real, tipo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Validado."); st.rerun()
        else: st.info("Sin pendientes.")

    with t_cob:
        st.subheader("Gestión de Cobros")
        pendientes_pago = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_pago:
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                st.write(f"Deuda Actual: **${resta:.2f}**")
                monto_abono = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"c_{p['ID_Barra']}")
                if st.button(f"Registrar Pago", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] = p.get('Abonado', 0.0) + monto_abono
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("Estatus Logístico")
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Estatus:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("Auditoría")
        df_aud = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader("📊 Resumen General de Operaciones")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            busq_res = st.text_input("🔍 Buscar por código:", key="res_search")
            if busq_res: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
            
            # --- CIRUGÍA: GANANCIA PROYECTADA ---
            df_res['Deuda'] = df_res['Monto_USD'] - df_res['Abonado']
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Kg (Aéreo)", f"{df_res[df_res['Tipo_Traslado']=='Aéreo']['Peso_Almacen'].sum():.1f}")
            m2.metric("ft³ (Marítimo)", f"{df_res[df_res['Tipo_Traslado']=='Marítimo']['Peso_Almacen'].sum():.1f}")
            m3.metric("Caja Real", f"${df_res['Abonado'].sum():.2f}")
            m4.metric("Ganancia Proyectada", f"${df_res['Deuda'].sum():.2f}", delta_color="normal", help="Total de dinero pendiente por cobrar")
            
            for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                df_f = df_res[df_res['Estado'] == est].copy()
                st.markdown(f'<div class="state-header"> {est} ({len(df_f)})</div>', unsafe_allow_html=True)
                if not df_f.empty:
                    df_f['Ref'] = df_f.apply(lambda x: f"{'✈️' if x.get('Tipo_Traslado') == 'Aéreo' else '🚢'} {x['ID_Barra']}", axis=1)
                    st.table(df_f[['Ref', 'Cliente', 'Peso_Almacen', 'Pago', 'Abonado', 'Deuda']])

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if not mis_p: st.info("No hay paquetes.")
    else:
        for p in mis_p:
            total = p['Monto_USD']; abonado = p.get('Abonado', 0.0)
            icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
            st.markdown(f"""<div class="p-card"><b>{icon} #{p['ID_Barra']}</b><br>Estado: {p['Estado']}<br>Falta: ${(total-abonado):.2f}</div>""", unsafe_allow_html=True)

# --- 6. ACCESO ---
else:
    col_l2 = st.columns([1, 1.5, 1])[1]
    with col_l2:
        st.markdown('<h1 class="logo-animado" style="font-size: 70px;">IACargo.io</h1>', unsafe_allow_html=True)
        le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
        if st.button("Ingresar", use_container_width=True):
            if le == "admin" and lp == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
            if u: st.session_state.usuario_identificado = u; st.rerun()
