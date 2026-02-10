import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }

    .fuente-cursiva {
        font-family: 'Dancing Script', cursive !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        text-align: center;
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

    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }

    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }

    .state-header {
        background: rgba(255, 255, 255, 0.1);
        border-left: 5px solid #3b82f6;
        color: #60a5fa !important; padding: 12px; border-radius: 8px; margin: 20px 0; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px;
    }

    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }

    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_KG = 5.0

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns:
                df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown('<h1 class="fuente-cursiva" style="font-size: 35px; text-align: left;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.markdown('<p class="fuente-cursiva" style="font-size: 16px; text-align: left; color: #a78bfa;">“Trabajamos para conectarte en todas partes del mundo”</p>', unsafe_allow_html=True)
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
            f_tipo = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Tipo": f_tipo,
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": f_pes*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_id} registrada.")

    with t_val:
        st.subheader("Báscula de Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para Pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Cliente: {paq['Cliente']} | Peso Reportado: {paq['Peso_Mensajero']} Kg")
            peso_real = st.number_input("Peso Real en Báscula (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']), step=0.1)
            if st.button("⚖️ Validar Peso"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Peso validado."); st.rerun()
        else: st.info("Sin pendientes.")

    with t_cob:
        st.subheader("Gestión de Cobros")
        if st.session_state.inventario:
            pendientes_pago = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
            for p in pendientes_pago:
                with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                    total = p['Monto_USD']
                    abonado = p.get('Abonado', 0.0)
                    resta = total - abonado
                    st.write(f"Modalidad: **{p.get('Modalidad')}** | Resta: **${resta:.2f}**")
                    monto_abono = st.number_input(f"Abonar a {p['ID_Barra']}", min_value=0.0, max_value=float(resta), key=f"c_{p['ID_Barra']}")
                    if st.button(f"Registrar Pago", key=f"b_{p['ID_Barra']}"):
                        p['Abonado'] = abonado + monto_abono
                        if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("Logística de Envío")
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        col_a1, col_a2 = st.columns([3, 1])
        with col_a1: st.subheader("Auditoría y Edición")
        with col_a2: ver_p = st.checkbox("🗑️ Papelera")
        if ver_p:
            if st.session_state.papelera:
                st.dataframe(pd.DataFrame(st.session_state.papelera), use_container_width=True)
                guia_res = st.selectbox("Restaurar ID:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("♻️ Restaurar"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
            else: st.info("Papelera vacía.")
        else:
            busq = st.text_input("🔍 Buscar por Guía:")
            df_aud = pd.DataFrame(st.session_state.inventario)
            if busq: df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            st.write("---")
            guia_ed = st.selectbox("Editar/Eliminar ID:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq_ed = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed), None)
            if paq_ed:
                c1, c2, c3 = st.columns(3)
                with c1: new_cli = st.text_input("Cliente", value=paq_ed['Cliente'])
                with c2: new_pes = st.number_input("Peso Almacén", value=float(paq_ed['Peso_Almacen']))
                with c3: new_pago = st.selectbox("Estado Pago", ["PENDIENTE", "PAGADO"], index=0 if paq_ed['Pago']=="PENDIENTE" else 1)
                b_save, b_del = st.columns(2)
                with b_save:
                    if st.button("💾 Guardar Cambios"):
                        paq_ed.update({'Cliente': new_cli, 'Peso_Almacen': new_pes, 'Pago': new_pago, 'Monto_USD': new_pes*PRECIO_POR_KG})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
                with b_del:
                    st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                    if st.button("🗑️ Enviar a Papelera"):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with t_res:
        st.subheader("📊 Resumen de Operaciones")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            
            # Métricas superiores
            m1, m2, m3 = st.columns(3)
            m1.metric("Kg Totales", f"{df_res['Peso_Almacen'].sum():.1f}")
            m2.metric("Paquetes", len(df_res))
            m3.metric("Caja (Abonos)", f"${df_res['Abonado'].sum():.2f}")
            
            st.write("---")
            # --- BUSCADOR POR CÓDIGO ---
            busq_id = st.text_input("🔍 Buscar caja por código de guía:", key="busq_resumen")
            if busq_id:
                df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_id, case=False)]

            # --- SECCIONES POR ESTADO ---
            st.markdown('<div class="state-header">📥 EN ALMACÉN</div>', unsafe_allow_html=True)
            df_almacen = df_res[df_res['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"]
            if not df_almacen.empty: st.dataframe(df_almacen, use_container_width=True)
            else: st.caption("No hay mercancía en almacén.")

            st.markdown('<div class="state-header">✈️ EN TRÁNSITO</div>', unsafe_allow_html=True)
            df_transito = df_res[df_res['Estado'] == "EN TRANSITO"]
            if not df_transito.empty: st.dataframe(df_transito, use_container_width=True)
            else: st.caption("No hay mercancía en tránsito.")

            st.markdown('<div class="state-header">📦 ENTREGADO</div>', unsafe_allow_html=True)
            df_entregado = df_res[df_res['Estado'] == "ENTREGADO"]
            if not df_entregado.empty: st.dataframe(df_entregado, use_container_width=True)
            else: st.caption("No hay mercancía entregada.")

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario
