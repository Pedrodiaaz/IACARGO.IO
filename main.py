import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="📦")

# --- TARIFAS ACTUALIZADAS ---
TARIFA_AEREO_KG = 6.0    # $6 por Kilogramo
TARIFA_MARITIMO_FT3 = 15.0  # $15 por Pie Cúbico

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    [data-testid="stSidebar"] { display: none; }
    
    /* Fondo para notificaciones */
    div[data-testid="stPopoverContent"] {
        background-color: #ffffff !important;
        border-radius: 15px !important;
        padding: 10px !important;
    }
    div[data-testid="stPopoverContent"] p, div[data-testid="stPopoverContent"] b { color: #1e293b !important; }

    /* Botones y tarjetas */
    .stButton > button { border-radius: 12px !important; }
    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: bold !important;
        width: 100% !important;
    }

    .logo-animado {
        font-style: italic !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        animation: pulse 2.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }

    /* Estilo de Expanders (Cobros y Resumen) */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        color: white !important;
    }
    [data-testid="stExpanderDetails"] { background-color: transparent !important; color: white !important; }
    [data-testid="stExpander"] p, [data-testid="stExpander"] label { color: white !important; }

    /* Inputs y Tablas */
    div[data-baseweb="input"] { background-color: #f8fafc !important; border-radius: 10px !important; }
    div[data-baseweb="input"] input { color: #000000 !important; }
    .resumen-row { background-color: #ffffff !important; color: #1e293b !important; padding: 12px; border-radius: 8px; margin-bottom: 5px; display: flex; justify-content: space-between; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"

def calcular_monto(valor, tipo):
    if tipo == "Aéreo": return valor * TARIFA_AEREO_KG
    elif tipo == "Marítimo": return valor * TARIFA_MARITIMO_FT3
    return valor * 5.0

if 'notificaciones' not in st.session_state: st.session_state.notificaciones = []

def agregar_notificacion(mensaje):
    hora = datetime.now().strftime("%H:%M")
    st.session_state.notificaciones.insert(0, {"msg": mensaje, "hora": hora})

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo).to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

# --- Session State ---
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()

# --- 3. DASHBOARD ADMINISTRADOR ---
def render_admin_dashboard():
    st.title("Consola de Control Logístico")
    tabs = st.tabs(["REGISTRO", "VALIDACIÓN", "COBROS", "ESTADOS", "AUDITORÍA/EDICIÓN", "RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        label_din = "ft³" if f_tra == "Marítimo" else "Kg"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking", value=st.session_state.id_actual)
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input(f"Valor inicial ({label_din})", min_value=0.0)
            if st.form_submit_button("REGISTRAR", type="primary"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": calcular_monto(f_pes, f_tra), "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Tipo_Traslado": f_tra, "Abonado": 0.0}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.session_state.id_actual = generar_id_unico()
                agregar_notificacion(f"Guía {f_id} creada")
                st.rerun()

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Validar Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Valor Real Almacén", value=float(paq['Peso_Mensajero']))
            if st.button("CONFIRMAR VALIDACIÓN", type="primary"):
                paq.update({'Peso_Almacen': v_real, 'Validado': True, 'Monto_USD': calcular_monto(v_real, paq['Tipo_Traslado'])})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        for p in [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']:
            rest = p['Monto_USD'] - p['Abonado']
            with st.expander(f"📦 {p['ID_Barra']} - {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Monto:", 0.0, float(rest), float(rest), key=f"c_{p['ID_Barra']}")
                if st.button("PAGAR", key=f"bc_{p['ID_Barra']}", type="primary"):
                    p['Abonado'] += m_abono
                    if (p['Monto_USD'] - p['Abonado']) <= 0.1: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        if st.session_state.inventario:
            sel_e = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="s_est")
            n_st = st.selectbox("Estatus:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("ACTUALIZAR", type="primary"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("Auditoría y Gestión de Registros")
        if st.checkbox("Ver Papelera (Registros Eliminados)"):
            if st.session_state.papelera:
                df_pap = pd.DataFrame(st.session_state.papelera)
                st.table(df_pap[['ID_Barra', 'Cliente', 'Estado']])
                if st.button("Vaciar Papelera"): 
                    st.session_state.papelera = []; guardar_datos([], ARCHIVO_PAPELERA); st.rerun()
            else: st.info("Papelera vacía.")
        else:
            df_aud = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df_aud, use_container_width=True)
            
            if st.session_state.inventario:
                st.markdown("---")
                guia_ed = st.selectbox("Seleccionar Guía para Editar/Eliminar:", [p["ID_Barra"] for p in st.session_state.inventario])
                paq_ed = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed)
                
                c1, c2, c3 = st.columns(3)
                n_cli = c1.text_input("Editar Cliente", value=paq_ed['Cliente'])
                n_val = c2.number_input("Editar Peso/Pies", value=float(paq_ed['Peso_Almacen']))
                n_tra = c3.selectbox("Editar Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], index=["Aéreo", "Marítimo", "Envio Nacional"].index(paq_ed['Tipo_Traslado']))
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 GUARDAR CAMBIOS", type="primary", use_container_width=True):
                        paq_ed.update({'Cliente': n_cli, 'Peso_Almacen': n_val, 'Tipo_Traslado': n_tra, 'Monto_USD': calcular_monto(n_val, n_tra)})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Actualizado"); st.rerun()
                with col_btn2:
                    if st.button("🗑️ ELIMINAR REGISTRO", use_container_width=True):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA)
                        agregar_notificacion(f"Guía {guia_ed} eliminada")
                        st.warning("Movido a papelera"); st.rerun()

    with t_res:
        st.subheader("Búsqueda y Resumen")
        busq = st.text_input("Código de caja:")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq and not df_res.empty: df_res = df_res[df_res['ID_Barra'].str.contains(busq, case=False)]
        
        for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
            df_f = df_res[df_res['Estado'] == est] if not df_res.empty else pd.DataFrame()
            with st.expander(f"{est} ({len(df_f)})"):
                for _, r in df_f.iterrows():
                    st.markdown(f'<div class="resumen-row"><b>{r["ID_Barra"]}</b> <span>{r["Cliente"]}</span> <b>${r["Abonado"]:.2f}</b></div>', unsafe_allow_html=True)

# --- 4. DASHBOARD CLIENTE ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<h1 class="logo-animado">Hola, {u["nombre"]}</h1>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if p['Correo'] == u['correo']]
    if not mis_p: st.info("Sin envíos registrados.")
    else:
        for p in mis_p:
            with st.container():
                st.write(f"📦 Guía: {p['ID_Barra']} | Estado: {p['Estado']}")
                st.progress(p['Abonado']/p['Monto_USD'] if p['Monto_USD'] > 0 else 0)

# --- LÓGICA DE LOGIN ---
if st.session_state.usuario_identificado is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<h1 class="logo-animado" style="text-align:center; font-size:60px;">IACargo.io</h1>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registro"])
        with t1:
            with st.form("l"):
                e = st.text_input("Email"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    if e == "admin" and p == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                    u = next((u for u in st.session_state.usuarios if u['correo'] == e.lower() and u['password'] == hash_password(p)), None)
                    if u: st.session_state.usuario_identificado = u; st.rerun()
        with t2:
            with st.form("s"):
                n = st.text_input("Nombre"); em = st.text_input("Email"); pw = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear"):
                    st.session_state.usuarios.append({"nombre": n, "correo": em.lower(), "password": hash_password(pw), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.rerun()
else:
    # Header
    col_l, col_n, col_s = st.columns([7, 1, 2])
    col_l.markdown('<div class="logo-animado" style="font-size:30px;">IACargo.io</div>', unsafe_allow_html=True)
    with col_n:
        with st.popover("🔔"):
            for n in st.session_state.notificaciones: st.write(f"**{n['hora']}**: {n['msg']}")
    if col_s.button("CERRAR SESIÓN"): st.session_state.usuario_identificado = None; st.rerun()

    if st.session_state.usuario_identificado['rol'] == "admin": render_admin_dashboard()
    else: render_client_dashboard()
