import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    /* Fondo Global */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] { display: none; }
    
    /* Estilo de Botones de Acción (AZUL RESALTADO) */
    .stButton > button {
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    /* Clase específica para botones de ACCIÓN PRINCIPAL */
    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #3b82f6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
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

    /* Visibilidad de Inputs */
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    div[data-baseweb="select"] > div { background-color: #f8fafc !important; color: #000000 !important; }

    .metric-container { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); }
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: #10b981; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    .badge-debt { background: #f87171; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []
def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

def obtener_icono_transporte(tipo):
    if tipo == "Aéreo": return "✈️"
    elif tipo == "Marítimo": return "🚢"
    elif tipo == "Envio Nacional": return "🚚"
    return "📦"

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. FUNCIONES DE DASHBOARD ---
def render_admin_dashboard():
    st.title(" Consola de Control Logístico")
    tabs = st.tabs([" REGISTRO", " VALIDACIÓN", " COBROS", " ESTADOS", " AUDITORÍA/EDICIÓN", " RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos" if f_tra == "Marítimo" else "Peso (Kg / Lbs)"
        with st.form("reg_form", clear_on_submit=True):
            st.info(f"ID sugerido: **{st.session_state.id_actual}**")
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            
            # BOTÓN AZUL (PRIMARY) - REGISTRAR EN SISTEMA
            if st.form_submit_button("REGISTRAR EN SISTEMA", type="primary", use_container_width=True):
                if f_id and f_cli and f_cor:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.success(f"Guía {f_id} registrada."); st.rerun()

    with t_val:
        st.subheader(" Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Reportado por mensajero: {paq['Peso_Mensajero']}")
            peso_real = st.number_input(f"Peso Real en Almacén", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR Y VALIDAR", type="primary"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_UNIDAD
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Validado correctamente."); st.rerun()
        else: st.info("No hay paquetes por validar.")

    with t_cob:
        st.subheader(" Gestión de Cobros")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f" {p['ID_Barra']} - {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto a abonar:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button(f"REGISTRAR PAGO", key=f"bp_{p['ID_Barra']}", type="primary"):
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader(" Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="status_sel")
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("ACTUALIZAR ESTATUS", type="primary"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

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
            else: st.info("La papelera está vacía.")
        else:
            busq_aud = st.text_input(" Buscar por Guía en Auditoría:", key="aud_search_input")
            df_aud = pd.DataFrame(st.session_state.inventario)
            if not df_aud.empty and busq_aud: 
                df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq_aud, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            
            if st.session_state.inventario:
                st.write("---")
                st.markdown("### Modificar o Eliminar Registro")
                guia_ed = st.selectbox("Seleccione ID para gestionar:", [p["ID_Barra"] for p in st.session_state.inventario], key="ed_sel")
                paq_ed = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed)
                
                c1, c2, c3 = st.columns(3)
                n_cli = c1.text_input("Cliente", value=paq_ed['Cliente'], key=f"nc_{paq_ed['ID_Barra']}")
                n_pes = c2.number_input("Peso/Pies", value=float(paq_ed['Peso_Almacen']), key=f"np_{paq_ed['ID_Barra']}")
                n_tra = c3.selectbox("Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], index=["Aéreo", "Marítimo", "Envio Nacional"].index(paq_ed.get('Tipo_Traslado', 'Aéreo')), key=f"nt_{paq_ed['ID_Barra']}")
                
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    if st.button("💾 GUARDAR CAMBIOS", use_container_width=True, type="primary"):
                        paq_ed.update({'Cliente': n_cli, 'Peso_Almacen': n_pes, 'Tipo_Traslado': n_tra, 'Monto_USD': n_pes * PRECIO_POR_UNIDAD})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Cambios guardados"); st.rerun()
                with btn_col2:
                    if st.button("🗑️ ELIMINAR REGISTRO", use_container_width=True, type="primary"):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.warning(f"Guía {guia_ed} movida a papelera."); st.rerun()

    with t_res:
        st.subheader(" Resumen General de Carga")
        df_full = pd.DataFrame(st.session_state.inventario)
        c_alm = len(df_full[df_full['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"]) if not df_full.empty else 0
        c_tra = len(df_full[df_full['Estado'] == "EN TRANSITO"]) if not df_full.empty else 0
        c_ent = len(df_full[df_full['Estado'] == "ENTREGADO"]) if not df_full.empty else 0
        
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-container"><small> EN ALMACÉN</small><br><b style="font-size:25px;">{c_alm}</b></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-container"><small> EN TRÁNSITO</small><br><b style="font-size:25px;">{c_tra}</b></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-container"><small> ENTREGADO</small><br><b style="font-size:25px;">{c_ent}</b></div>', unsafe_allow_html=True)
        st.write("---")
        busq_res = st.text_input(" Buscar caja por código:", key="res_search_admin")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq_res and not df_res.empty: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
        for est_k, est_l, _ in [("RECIBIDO ALMACEN PRINCIPAL", " EN ALMACÉN", "Almacén"), ("EN TRANSITO", " EN TRÁNSITO", "Tránsito"), ("ENTREGADO", " ENTREGADO", "Entregado")]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est_l} ({len(df_f)})", expanded=False):
                for _, r in df_f.iterrows():
                    icon = obtener_icono_transporte(r.get('Tipo_Traslado'))
                    st.markdown(f'<div class="resumen-row"><div style="color:#2563eb; font-weight:800;">{icon} {r["ID_Barra"]}</div><div style="color:#1e293b; flex-grow:1; margin-left:15px;">{r["Cliente"]}</div><div style="color:#475569; font-weight:700;">${float(r["Abonado"]):.2f}</div></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    busq_cli = st.text_input(" Buscar mis paquetes por código de barra:", key="cli_search_input")
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if busq_cli: mis_p = [p for p in mis_p if busq_cli.lower() in str(p.get('ID_Barra')).lower()]
    if not mis_p:
        st.info("Actualmente no tienes envíos registrados en el sistema.")
    else:
        st.write(f"Has registrado **{len(mis_p)}** paquete(s):")
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = tot - abo
                porc = (abo / tot * 100) if tot > 0 else 0
                badge_class = "badge-paid" if p.get('Pago') == "PAGADO" else "badge-debt"
                icon = obtener_icono_transporte(p.get('Tipo_Traslado'))
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                            <span style="color:#60a5fa; font-weight:800; font-size:1.3em;">{icon} #{p['ID_Barra']}</span>
                            <span class="{badge_class}">{p.get('Pago')}</span>
                        </div>
                        <div style="font-size:1em; margin-bottom:15px;">
                             <b>Estado actual:</b> {p['Estado']}<br>
                             <b>Modalidad:</b> {p.get('Modalidad', 'N/A')}
                        </div>
                        <div style="background: rgba(255,255,255,0.08); border-radius:12px; padding:15px;">
                            <div style="display:flex; justify-content:space-between; font-size:0.9em; margin-bottom:8px;">
                                <span>Progreso de Pago</span><b>{porc:.1f}%</b>
                            </div>
                """, unsafe_allow_html=True)
                st.progress(abo/tot if tot > 0 else 0)
                st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; margin-top:10px; font-weight:bold; font-size:0.95em;">
                                <div style="color:#10b981;">Pagado: ${abo:.2f}</div>
                                <div style="color:#f87171;">Pendiente: ${rest:.2f}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style="text-align:center;">
                    <h1 class="logo-animado" style="font-size:80px; margin-bottom:0px;">IACargo.io</h1>
                    <p style="font-size:22px; color:#94a3b8; font-style:italic;">"La existencia es un milagro"</p>
                    <div style="height:40px;"></div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
                st.session_state.landing_vista = False; st.rerun()
            st.markdown("<br><p style='text-align:center; opacity:0.6;'>No eres herramienta, eres evolución.</p>", unsafe_allow_html=True)
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login_form"):
                    le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
                        else: st.error("Credenciales incorrectas")
            with t2:
                with st.form("signup_form"):
                    n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta", type="primary", use_container_width=True):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Cuenta creada."); st.rerun()
            if st.button(" Volver", type="primary", use_container_width=True):
                st.session_state.landing_vista = True; st.rerun()

else:
    st.markdown(f"""
        <div class="logout-container">
            <span style="color:#60a5fa; font-weight:bold; font-size:0.9em;">Socio: {st.session_state.usuario_identificado['nombre']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        cols = st.columns([7, 2])
        with cols[1]:
            # BOTÓN AZUL (PRIMARY) - CERRAR SESIÓN
            if st.button("CERRAR SESIÓN", type="primary", use_container_width=True):
                st.session_state.usuario_identificado = None
                st.session_state.landing_vista = True
                st.rerun()

    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
