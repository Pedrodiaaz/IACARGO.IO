import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

TARIFA_AEREO_KG = 6.0    
TARIFA_MARITIMO_FT3 = 15.0  

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* POPUPS Y NOTIFICACIONES */
    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important; border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 15px !important; padding: 10px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stPopoverContent"] p, div[data-testid="stPopoverContent"] small, 
    div[data-testid="stPopoverContent"] span, div[data-testid="stPopoverContent"] b {
        color: #1e293b !important;
    }

    /* BOTONES PRIMARIOS */
    .stButton > button { border-radius: 12px !important; transition: all 0.3s ease !important; }
    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #2563eb !important; color: white !important;
        border: none !important; font-weight: bold !important;
        width: 100% !important; padding: 10px 20px !important;
    }

    /* LOGO Y TEXTOS */
    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }

    /* MEJORA DE EXPANDERS (CRISTAL) */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
    }
    details[data-testid="stExpander"] summary {
        color: #60a5fa !important; font-weight: 700 !important;
    }

    /* INPUTS */
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
ARCHIVO_NOTIF = "notificaciones_iac.csv"

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            # Convertir strings de listas a listas reales para el historial
            if 'Historial_Pagos' in df.columns:
                df['Historial_Pagos'] = df['Historial_Pagos'].apply(lambda x: eval(x) if isinstance(x, str) else [])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

def registrar_notificacion(para, msg):
    nueva = {"hora": datetime.now().strftime("%H:%M"), "para": para, "msg": msg}
    st.session_state.notificaciones.insert(0, nueva)
    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF)

def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
def obtener_icono_transporte(tipo): return {"Aéreo": "✈️", "Marítimo": "🚢", "Envio Nacional": "🚚"}.get(tipo, "📦")

# --- Session State ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = cargar_datos(ARCHIVO_NOTIF)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. DASHBOARDS ---

def render_admin_dashboard():
    st.title(" Consola de Control Logístico")
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos (ft³)" if f_tra == "Marítimo" else "Peso (Kilogramos)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary"):
                if f_id and f_cli and f_cor:
                    monto_calc = calcular_monto(f_pes, f_tra)
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": monto_calc, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, 
                        "Abonado": 0.0, "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Historial_Pagos": [] # Iniciamos historial vacío
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.rerun()

    with t_val:
        st.subheader(" Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            label_val = "Pies Cúbicos Reales" if paq['Tipo_Traslado'] == "Marítimo" else "Peso Real (Kg)"
            valor_real = st.number_input(label_val, min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR Y VALIDAR", type="primary"):
                paq['Peso_Almacen'] = valor_real
                paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(valor_real, paq['Tipo_Traslado'])
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Validado"); st.rerun()

    with t_cob:
        col_t, col_btn = st.columns([3, 1])
        with col_t: st.subheader(" Gestión de Cobros")
        
        # --- LÓGICA DE EXPORTACIÓN ---
        historial_total = []
        for p in st.session_state.inventario:
            for pago in p.get('Historial_Pagos', []):
                historial_total.append({
                    "Fecha_Pago": pago['fecha'],
                    "ID_Guia": p['ID_Barra'],
                    "Cliente": p['Cliente'],
                    "Monto_Abonado": pago['monto'],
                    "Tipo": p['Tipo_Traslado']
                })
        
        if historial_total:
            df_hist = pd.DataFrame(historial_total)
            csv = df_hist.to_csv(index=False).encode('utf-8')
            with col_btn:
                st.download_button(
                    label="📊 EXPORTAR HISTORIAL PAGOS",
                    data=csv,
                    file_name=f"Pagos_IACargo_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

        busq_cobro = st.text_input("🔍 Buscar paquete o cliente:", key="search_cobros")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        if busq_cobro:
            pendientes_p = [p for p in pendientes_p if busq_cobro.lower() in p['ID_Barra'].lower() or busq_cobro.lower() in p['Cliente'].lower()]

        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f"📦 {p['ID_Barra']} — {p['Cliente']} (Debe: ${rest:.2f})"):
                m_abono = st.number_input("Cantidad a pagar:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"REGISTRAR PAGO", key=f"bp_{p['ID_Barra']}", type="primary"):
                    # Registro en historial
                    p.setdefault('Historial_Pagos', []).append({
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "monto": m_abono
                    })
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    registrar_notificacion(p['Correo'], f"Abono de ${m_abono:.2f} recibido para guía {p['ID_Barra']}")
                    st.rerun()

    with t_est:
        st.subheader(" Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="status_sel")
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == sel_e)
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS", type="primary"):
                paq["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                registrar_notificacion(paq["Correo"], f"Guía {sel_e} actualizada a: {n_st}")
                st.rerun()

    with t_aud:
        st.subheader(" Auditoría y Edición")
        busq_aud = st.text_input(" Buscar por Guía:", key="aud_search_input")
        df_aud = pd.DataFrame(st.session_state.inventario)
        if not df_aud.empty and busq_aud: 
            df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq_aud, case=False)]
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader(" Resumen General")
        df_res = pd.DataFrame(st.session_state.inventario)
        for est_k, est_l in [("RECIBIDO ALMACEN PRINCIPAL", " EN ALMACÉN"), ("EN TRANSITO", " EN TRÁNSITO"), ("ENTREGADO", " ENTREGADO")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                    st.markdown(f'<div class="resumen-row"><div>{icon} <b>{r["ID_Barra"]}</b> - {r["Cliente"]}</div><div style="font-weight:700;">${float(r["Abonado"]):.2f} / ${float(r["Monto_USD"]):.2f}</div></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    if not mis_p: st.info("No tienes paquetes registrados.")
    else:
        for p in mis_p:
            tot, abo = float(p.get('Monto_USD', 0.0)), float(p.get('Abonado', 0.0))
            perc = (abo / tot * 100) if tot > 0 else 0
            st.markdown(f"""<div style="background:rgba(255,255,255,0.07); padding:20px; border-radius:20px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.1);">
                <h3 style="margin:0;">📦 {p['ID_Barra']} | {p['Estado']}</h3>
                <p>Monto Total: ${tot:.2f} | Pagado: ${abo:.2f}</p>
                <div style="width:100%; background:#334155; height:10px; border-radius:5px;"><div style="width:{perc}%; background:#22c55e; height:10px; border-radius:5px;"></div></div>
                </div>""", unsafe_allow_html=True)

def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        mías = [n for n in st.session_state.notificaciones if n['para'] in [st.session_state.usuario_identificado['correo'], 'admin']]
        with st.popover("🔔"):
            if mías:
                for n in mías[:5]: st.write(f"**{n['hora']}**: {n['msg']}")
            else: st.write("Sin notificaciones.")
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- LOGIN (SIMPLIFICADO PARA FLUJO) ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div style="text-align:center; margin-top:50px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Entrar", type="primary", use_container_width=True):
                if le == "admin": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
                else: 
                    st.session_state.usuario_identificado = {"nombre": "Cliente Test", "rol": "cliente", "correo": le}; st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
