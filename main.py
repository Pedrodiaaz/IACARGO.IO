import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta

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
    div[data-testid="stForm"]  button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }
    .header-resumen {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        margin: 10px 0;
        border-left: 6px solid #60a5fa;
    }
    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 15px;
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
        font-weight: 800; font-size: 38px; 
    }
    .badge-paid { background: #059669; color: white; padding: 4px 10px; border-radius: 10px; font-size: 10px; }
    .badge-debt { background: #dc2626; color: white; padding: 4px 10px; border-radius: 10px; font-size: 10px; }
    .stButton>button { border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: 
                df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
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
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None; st.rerun()
    else: st.info("Inicie sesión para continuar")
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
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
        label_dinamico = "Pies Cúbicos" if f_tra == "Marítimo" else "Peso Mensajero (Kg)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_dinamico, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                nuevo = {
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                    "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                    "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                    "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, 
                    "Abonado": 0.0, "Fecha_Registro": datetime.now()
                }
                st.session_state.inventario.append(nuevo); guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_val:
        st.subheader("⚖️ Validación de Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            u_medida = "Pies Cúbicos" if paq.get('Tipo_Traslado') == "Marítimo" else "Kg"
            peso_real = st.number_input(f"Medida Real ({u_medida})", value=float(paq['Peso_Mensajero']))
            if st.button("⚖️ Validar"):
                paq['Peso_Almacen'] = peso_real; paq['Validado'] = True; paq['Monto_USD'] = peso_real * PRECIO_POR_UNIDAD
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else: st.info("Sin pendientes.")

    with t_cob:
        st.subheader("💰 Gestión de Cobros")
        hoy = datetime.now()
        # Clasificación
        pagados = [p for p in st.session_state.inventario if p['Pago'] == 'PAGADO']
        pendientes = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE' and (hoy - p['Fecha_Registro']).days <= 15]
        atrasados = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE' and (hoy - p['Fecha_Registro']).days > 15]
        
        c1, c2, c3 = st.tabs(["🔴 ATRASADOS (>15 días)", "🟡 PENDIENTES", "🟢 PAGADOS"])
        
        with c1:
            for p in atrasados:
                with st.expander(f"🚨 {p['ID_Barra']} - {p['Cliente']} (Atrasado)"):
                    resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                    monto = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"atr_{p['ID_Barra']}")
                    if st.button("Registrar Abono", key=f"btn_atr_{p['ID_Barra']}"):
                        p['Abonado'] = p.get('Abonado', 0.0) + monto
                        if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

        with c2:
            for p in pendientes:
                with st.expander(f"📦 {p['ID_Barra']} - {p['Cliente']}"):
                    resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                    monto = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"pen_{p['ID_Barra']}")
                    if st.button("Registrar Abono", key=f"btn_pen_{p['ID_Barra']}"):
                        p['Abonado'] = p.get('Abonado', 0.0) + monto
                        if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        with c3:
            for p in pagados: st.success(f"✅ {p['ID_Barra']} - {p['Cliente']} (Total: ${p['Monto_USD']:.2f})")

    with t_est:
        st.subheader("✈️ Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("🔍 Auditoría")
        df_aud = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader("📊 Resumen General")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            busq_res = st.text_input("🔍 Buscar caja por código:", key="res_search")
            if busq_res: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
            
            estados = {"RECIBIDO ALMACEN PRINCIPAL": "📦 Almacén", "EN TRANSITO": "✈️ Tránsito", "ENTREGADO": "✅ Entregado"}
            for est_key, est_label in estados.items():
                df_f = df_res[df_res['Estado'] == est_key].copy()
                st.markdown(f'<div class="header-resumen">{est_label} ({len(df_f)})</div>', unsafe_allow_html=True)
                for _, row in df_f.iterrows():
                    icon = "✈️" if row.get('Tipo_Traslado') == "Aéreo" else "🚢"
                    u_r = "Pies" if row.get('Tipo_Traslado') == "Marítimo" else "Kg"
                    st.markdown(f'<div class="resumen-row"><div>{icon} <b>{row["ID_Barra"]}</b> - {row["Cliente"]}</div><div>{row["Peso_Almacen"]:.1f} {u_r} | ${row["Abonado"]:.2f}</div></div>', unsafe_allow_html=True)

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    for p in mis_p:
        with st.container():
            tot = p['Monto_USD']; abo = p.get('Abonado', 0.0); uni = "Pies" if p.get('Tipo_Traslado') == "Marítimo" else "Kg"
            icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
            st.markdown(f"### {icon} Guía #{p['ID_Barra']}")
            st.write(f"Estado: **{p['Estado']}** | Medida: **{p['Peso_Almacen']:.1f} {uni}**")
            st.progress(abo/tot if tot > 0 else 0)
            st.write(f"Abonado: ${abo:.2f} / Total: ${tot:.2f}")

# --- 6. LOGIN ---
else:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<h1 class="logo-animado" style="font-size: 50px; text-align:center;">IACargo.io</h1>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registrarse"])
        with t1:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Entrar", use_container_width=True):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
