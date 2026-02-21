import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (RESTAURADA) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

TARIFA_AEREO_KG = 6.0    
TARIFA_MARITIMO_FT3 = 15.0  

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    /* CAMPANA Y PUNTOS */
    .bell-container { position: relative; display: inline-block; font-size: 26px; }
    .bell-icon { color: #facc15; }
    .red-dot {
        position: absolute; top: -2px; right: -2px; height: 12px; width: 12px;
        background-color: #ef4444; border-radius: 50%; border: 2px solid #0f172a; z-index: 10;
    }

    /* POPOVER NOTIFICACIONES */
    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important; border-radius: 15px !important;
        padding: 10px !important; box-shadow: 0 10px 15px rgba(0,0,0,0.3);
    }
    .notif-item {
        background: #f1f5f9; border-left: 4px solid #2563eb;
        padding: 8px; margin-bottom: 5px; border-radius: 8px;
        font-size: 0.85em; color: #1e293b !important;
    }

    /* DISEÑO RESTAURADO */
    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px;
    }
    .p-card:hover { transform: translateY(-5px); border-color: #60a5fa; transition: 0.3s; }

    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #000000 !important; font-weight: 500 !important; }
    
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-radius: 8px; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE DATOS Y NOTIFICACIONES ---
def agregar_notificacion(mensaje, destino="admin", correo=None):
    hora = datetime.now().strftime("%H:%M")
    if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []
    st.session_state.notificaciones.insert(0, {"msg": mensaje, "hora": hora, "destino": destino, "correo": correo, "leida": False})

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

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

# Inicialización de Estados
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos("inventario_logistica.csv")
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos("papelera_iacargo.csv")
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos("usuarios_iacargo.csv")
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

# --- 3. INTERFAZ ---

def render_header():
    u = st.session_state.usuario_identificado
    col_l, col_n, col_s = st.columns([7, 1, 2])
    with col_l: st.markdown('<div class="logo-animado" style="font-size:40px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        # Lógica de Campana Solicitada
        if u['rol'] == 'admin':
            mis_notif = [n for n in st.session_state.notificaciones if n['destino'] == 'admin']
        else:
            mis_notif = [n for n in st.session_state.notificaciones if n['correo'] == u['correo']]
        
        has_unread = any(not n['leida'] for n in mis_notif)
        with st.popover("🔔"):
            st.markdown(f'<div class="bell-container"><span class="bell-icon">🔔</span>{"<div class=\"red-dot\"></div>" if has_unread else ""}</div>', unsafe_allow_html=True)
            for n in mis_notif:
                st.markdown(f'<div class="notif-item"><b>{n["hora"]}</b>: {n["msg"]}</div>', unsafe_allow_html=True)
                n['leida'] = True
    with col_s:
        if st.button("CERRAR SESIÓN", type="primary"):
            st.session_state.usuario_identificado = None; st.session_state.landing_vista = True; st.rerun()

def render_admin_dashboard():
    st.title("Consola de Control Logístico")
    tabs = st.tabs(["REGISTRO", "VALIDACIÓN", "COBROS", "ESTADOS", "AUDITORÍA/EDICIÓN", "RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        with st.form("reg_admin"):
            f_id = st.text_input("ID Tracking", value=generar_id_unico())
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input("Peso/Medida Inicial", min_value=0.0)
            if st.form_submit_button("REGISTRAR"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": calcular_monto(f_pes, f_tra), "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                agregar_notificacion(f"📦 Nuevo Paquete: {f_id} ({f_cli})", "admin")
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Validar Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Confirmar Peso/Medida Real", value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR Y NOTIFICAR AL CLIENTE"):
                paq['Peso_Almacen'] = v_real; paq['Validado'] = True
                paq['Monto_USD'] = calcular_monto(v_real, paq['Tipo_Traslado'])
                agregar_notificacion(f"⚖️ Peso Verificado: Su paquete {paq['ID_Barra']} fue validado con {v_real}.", "cliente", paq['Correo'])
                guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    with t_cob:
        busq_cob = st.text_input("🔍 Buscar cobros (ID o Cliente):")
        p_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        if busq_cob: p_p = [p for p in p_p if busq_cob.lower() in p['ID_Barra'].lower() or busq_cob.lower() in p['Cliente'].lower()]
        for p in p_p:
            rest = float(p['Monto_USD']) - float(p['Abonado'])
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']} (Debe: ${rest:.2f})"):
                m_abono = st.number_input("Registrar Pago:", 0.0, float(rest), float(rest), key=f"c_{p['ID_Barra']}")
                if st.button("COBRAR", key=f"bc_{p['ID_Barra']}"):
                    p['Abonado'] += m_abono
                    if (float(p['Monto_USD']) - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    agregar_notificacion(f"💵 Pago Recibido: Se registró un abono de ${m_abono} a su guía {p['ID_Barra']}.", "cliente", p['Correo'])
                    guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    with t_est:
        sel_e = st.selectbox("Cambiar Estatus:", [p["ID_Barra"] for p in st.session_state.inventario])
        n_st = st.selectbox("Nuevo Estado:", ["EN TRANSITO", "RECIBIDO EN DESTINO", "ENTREGADO"])
        if st.button("ACTUALIZAR"):
            for p in st.session_state.inventario:
                if p["ID_Barra"] == sel_e: 
                    p["Estado"] = n_st
                    agregar_notificacion(f"🚚 Actualización: Su paquete {sel_e} ahora está {n_st}.", "cliente", p['Correo'])
            guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); st.rerun()

    with t_aud:
        if st.checkbox("Ver Papelera de Reciclaje"):
            for p in st.session_state.papelera:
                st.write(f"🗑️ {p['ID_Barra']} - {p['Cliente']}")
                if st.button(f"Restaurar {p['ID_Barra']}"):
                    st.session_state.inventario.append(p)
                    st.session_state.papelera = [x for x in st.session_state.papelera if x['ID_Barra'] != p['ID_Barra']]
                    guardar_datos(st.session_state.inventario, "inventario_logistica.csv"); guardar_datos(st.session_state.papelera, "papelera_iacargo.csv"); st.rerun()
        else:
            busq_a = st.text_input("🔍 Buscar para editar:")
            df_a = pd.DataFrame(st.session_state.inventario)
            if busq_a and not df_a.empty: df_a = df_a[df_a['ID_Barra'].str.contains(busq_a, case=False)]
            st.dataframe(df_a, use_container_width=True)

    with t_res:
        busq_res = st.text_input("🔍 Buscar en Resumen:")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq_res and not df_res.empty: df_res = df_res[df_res['ID_Barra'].str.contains(busq_res, case=False)]
        for est_k in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
            df_f = df_res[df_res['Estado'] == est_k] if not df_res.empty else pd.DataFrame()
            with st.expander(f"📦 {est_k} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    st.markdown(f'<div class="resumen-row"><b>{r["ID_Barra"]}</b> <span>{r["Cliente"]}</span> <b>${float(r["Abonado"]):.2f}</b></div>', unsafe_allow_html=True)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if p.get('Correo') == u['correo']]
    
    if not mis_p: st.info("No tienes envíos activos.")
    else:
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot, abo = float(p['Monto_USD']), float(p['Abonado'])
                st.markdown(f"""
                <div class="p-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#60a5fa; font-weight:800; font-size: 20px;">📦 #{p["ID_Barra"]}</span>
                        <span style="background:rgba(96,165,250,0.2); padding: 4px 10px; border-radius:10px; font-size:12px;">{p["Estado"]}</span>
                    </div>
                    <div style="margin: 15px 0;">
                        <small>Peso Declarado: {p['Peso_Mensajero']}</small><br>
                        <small><b>Peso Verificado: {p['Peso_Almacen'] if p['Validado'] else 'Pendiente'}</b></small>
                    </div>
                    <div style="font-size: 22px; font-weight: 700;">${tot:.2f}</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px;">
                        <span>Abonado: ${abo:.2f}</span>
                        <span>Resta: ${(tot-abo):.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(abo/tot, 1.0) if tot > 0 else 0)

# --- LOGIN (ORIGINAL RESTAURADO) ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1 class="logo-animado" style="font-size:80px;">IACargo.io</h1><p>"La existencia es un milagro"</p></div>', unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", type="primary"): st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login"):
                    le, lp = st.text_input("Correo"), st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar", type="primary"):
                        if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            with t2:
                with st.form("signup"):
                    n, e, p = st.text_input("Nombre"), st.text_input("Correo"), st.text_input("Clave", type="password")
                    if st.form_submit_button("Crear Cuenta", type="primary"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        agregar_notificacion(f"👤 Nuevo Usuario: {n}", "admin")
                        guardar_datos(st.session_state.usuarios, "usuarios_iacargo.csv"); st.rerun()
else:
    render_header()
    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
