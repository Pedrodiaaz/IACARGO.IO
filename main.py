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
    
    .bell-container { position: relative; display: inline-block; font-size: 26px; }
    .red-dot {
        position: absolute; top: -2px; right: -2px; height: 12px; width: 12px;
        background-color: #ef4444; border-radius: 50%; border: 2px solid #0f172a; z-index: 10;
    }

    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important; border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 15px !important; padding: 10px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }

    div[data-testid="stPopoverContent"] p, div[data-testid="stPopoverContent"] small, 
    div[data-testid="stPopoverContent"] span, div[data-testid="stPopoverContent"] b {
        color: #1e293b !important;
    }

    .notif-item {
        background: #f1f5f9; border-left: 4px solid #2563eb;
        padding: 10px; margin-bottom: 8px; border-radius: 8px; font-size: 0.9em; color: #1e293b !important;
    }

    .stButton > button { border-radius: 12px !important; transition: all 0.3s ease !important; }
    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #2563eb !important; color: white !important;
        border: none !important; font-weight: bold !important;
        width: 100% !important; padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }
    
    div.stButton > button[kind="primary"]:hover, .stForm div.stButton > button:hover {
        background-color: #3b82f6 !important; transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
        margin-bottom: 5px;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }

    .stTabs, .stForm, [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px; color: white !important;
    }

    .p-card {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px; transition: transform 0.3s ease;
    }
    .p-card:hover { transform: translateY(-5px); border-color: #60a5fa; }

    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
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

def registrar_notificacion(para, msg):
    nueva = {"hora": datetime.now().strftime("%H:%M"), "para": para, "msg": msg}
    st.session_state.notificaciones.insert(0, nueva)
    pd.DataFrame(st.session_state.notificaciones).to_csv(ARCHIVO_NOTIF, index=False)

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            if 'Historial_Pagos' in df.columns:
                df['Historial_Pagos'] = df['Historial_Pagos'].apply(lambda x: eval(x) if isinstance(x, str) else [])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)
def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
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
            st.info(f"ID sugerido: **{st.session_state.id_actual}**")
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary"):
                if f_id and f_cli and f_cor:
                    monto_calc = calcular_monto(f_pes, f_tra)
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": monto_calc, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now(), "Historial_Pagos": []}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    registrar_notificacion("admin", f"Nuevo registro creado: {f_id} ({f_cli})")
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
        st.subheader(" Gestión de Cobros")
        busq_cobro = st.text_input("🔍 Buscar paquete o cobro:", key="search_cobros_admin")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        if busq_cobro:
            pendientes_p = [p for p in pendientes_p if busq_cobro.lower() in p['ID_Barra'].lower() or busq_cobro.lower() in p['Cliente'].lower()]

        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f"📦 {p['ID_Barra']} — {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"REGISTRAR PAGO", key=f"bp_{p['ID_Barra']}", type="primary"):
                    p.setdefault('Historial_Pagos', []).append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "monto": m_abono})
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    registrar_notificacion(p['Correo'], f"Pago registrado: ${m_abono:.2f} para la guía {p['ID_Barra']}")
                    st.rerun()

    with t_est:
        st.subheader(" Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="status_sel")
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == sel_e)
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS", type="primary"):
                old_st = paq["Estado"]
                paq["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                registrar_notificacion(paq["Correo"], f"Guía {sel_e}: {old_st} ➔ {n_st}")
                st.rerun()

    with t_aud:
        st.subheader(" Auditoría y Edición")
        if st.checkbox(" Ver Papelera"):
            if st.session_state.papelera:
                guia_res = st.selectbox("Restaurar ID:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("Restaurar Guía", type="primary"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
        else:
            busq_aud = st.text_input(" Buscar por Guía:", key="aud_search_input")
            df_aud = pd.DataFrame(st.session_state.inventario)
            if not df_aud.empty and busq_aud: 
                df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq_aud, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            if st.session_state.inventario:
                st.write("---")
                guia_ed = st.selectbox("Seleccione ID para gestionar:", [p["ID_Barra"] for p in st.session_state.inventario], key="ed_sel")
                paq_ed = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed)
                c1, c2, c3 = st.columns(3)
                n_cli = c1.text_input("Cliente", value=paq_ed['Cliente'], key=f"nc_{paq_ed['ID_Barra']}")
                n_val = c2.number_input("Valor", value=float(paq_ed['Peso_Almacen']), key=f"np_{paq_ed['ID_Barra']}")
                n_tra = c3.selectbox("Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], index=["Aéreo", "Marítimo", "Envio Nacional"].index(paq_ed.get('Tipo_Traslado', 'Aéreo')), key=f"nt_{paq_ed['ID_Barra']}")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 GUARDAR CAMBIOS", type="primary", use_container_width=True):
                        paq_ed.update({'Cliente': n_cli, 'Peso_Almacen': n_val, 'Tipo_Traslado': n_tra, 'Monto_USD': calcular_monto(n_val, n_tra)})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
                with col_btn2:
                    if st.button("🗑️ ELIMINAR REGISTRO", type="primary", use_container_width=True):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()

    with t_res:
        st.subheader(" Resumen General")
        df_res = pd.DataFrame(st.session_state.inventario)
        busq_box = st.text_input(" Buscar caja por código:", key="res_search_admin")
        
        if busq_box and not df_res.empty:
            df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_box, case=False)]
            
        for est_k, est_l, _ in [("RECIBIDO ALMACEN PRINCIPAL", " EN ALMACÉN", "Alm"), ("EN TRANSITO", " EN TRÁNSITO", "Tra"), ("ENTREGADO", " ENTREGADO", "Ent")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})", expanded=True if busq_box else False):
                for _, r in df_f.iterrows():
                    icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                    # Estructura del Resumen con Botón de Exportar Individual
                    c_info, c_hist, c_exp = st.columns([3, 2, 1])
                    with c_info:
                        st.markdown(f'<div class="resumen-row"><div style="color:#2563eb; font-weight:800;">{icon} {r["ID_Barra"]}</div><div style="color:#1e293b; flex-grow:1; margin-left:15px;">{r["Cliente"]}</div></div>', unsafe_allow_html=True)
                    with c_hist:
                        # Mostramos brevemente los abonos
                        abonos = r.get('Historial_Pagos', [])
                        if abonos:
                            txt_abono = f"Pagos: {len(abonos)} | Total: ${float(r['Abonado']):.2f}"
                            st.caption(txt_abono)
                        else:
                            st.caption("Sin pagos registrados.")
                    with c_exp:
                        # Botón para descargar reporte de ESTE paquete
                        if abonos:
                            df_h_ind = pd.DataFrame(abonos)
                            df_h_ind['Guía'] = r['ID_Barra']
                            csv_ind = df_h_ind.to_csv(index=False).encode('utf-8')
                            st.download_button(label="📥 Reporte", data=csv_ind, file_name=f"Pagos_{r['ID_Barra']}.csv", mime="text/csv", key=f"dl_{r['ID_Barra']}", use_container_width=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u['correo'].lower()]
    if not mis_p: st.info("Sin envíos activos.")
    else:
        busq_c = st.text_input("🔍 Buscar paquete por ID:", key="search_client_pkg")
        if busq_c: mis_p = [p for p in mis_p if busq_c.lower() in str(p.get('ID_Barra', '')).lower()]
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot, abo = float(p.get('Monto_USD', 0.0)), float(p.get('Abonado', 0.0))
                perc = (abo / tot * 100) if tot > 0 else 0
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                st.markdown(f"""<div class="p-card">
                    <div style="display: flex; justify-content: space-between;"><span style="color:#60a5fa; font-weight:800; font-size: 20px;">{icon} #{p['ID_Barra']}</span><span style="background:rgba(96,165,250,0.2); padding: 4px 10px; border-radius:10px; font-size:12px;">{p['Estado']}</span></div>
                    <div style="margin-top: 15px;"><small style="opacity:0.7;">Total a pagar</small><div style="font-size: 22px; font-weight: 700;">${tot:.2f}</div></div>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px;"><span>Pagado: <b style="color:#4ade80;">${abo:.2f}</b></span><span>Pendiente: <b style="color:#f87171;">${tot-abo:.2f}</b></span></div>
                    <div style="width: 100%; background-color: #ef4444; height: 12px; border-radius: 6px; margin-top: 15px; display: flex; overflow: hidden;"><div style="width: {perc}%; background-color: #22c55e; height: 100%;"></div></div>
                    </div>""", unsafe_allow_html=True)

def render_header():
    col_l, col_n, col_s = st.columns([7, 1, 2])
    u = st.session_state.usuario_identificado
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        target = u['rol'] if u['rol'] == 'admin' else u['correo']
        mías = [n for n in st.session_state.notificaciones if n['para'] == target]
        with st.popover("🔔"):
            if mías: st.markdown('<div class="red-dot"></div>', unsafe_allow_html=True)
            if not mías: st.write("Sin avisos.")
            else:
                for n in mías[:5]: st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b> - {n["msg"]}</div>', unsafe_allow_html=True)
                if st.button("Limpiar"):
                    st.session_state.notificaciones = [n for n in st.session_state.notificaciones if n['para'] != target]
                    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF); st.rerun()
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

# --- LOGIN ---
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
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary"):
                        if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            with t2:
                with st.form("signup"):
                    n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta", type="primary"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
