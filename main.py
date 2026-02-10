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
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    .fuente-cursiva {
        font-family: 'Dancing Script', cursive !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700; text-align: center;
    }
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px; margin-bottom: 15px; color: white !important;
    }
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .state-header { background: rgba(255, 255, 255, 0.1); border-left: 5px solid #3b82f6; color: #60a5fa !important; padding: 12px; border-radius: 8px; margin: 20px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .stButton>button { border-radius: 12px !important; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important; color: white !important; border: none !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100% !important; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"

# Constantes de Precios
PRECIO_AEREO_KG = 5.0
PRECIO_MARITIMO_FT3 = 18.0

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
            col1, col2 = st.columns(2)
            with col1:
                f_id = st.text_input("ID Tracking / Guía")
                f_cli = st.text_input("Nombre del Cliente")
                f_cor = st.text_input("Correo del Cliente")
            with col2:
                f_tipo = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
                f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            
            st.write("---")
            monto_calculado = 0.0
            unidad_medida = ""
            valor_medida = 0.0

            if f_tipo == "Aéreo":
                f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
                monto_calculado = f_pes * PRECIO_AEREO_KG
                unidad_medida = "Kg"
                valor_medida = f_pes
            else:
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1: largo = st.number_input("Largo (pulg)", min_value=0.0)
                with col_m2: ancho = st.number_input("Ancho (pulg)", min_value=0.0)
                with col_m3: alto = st.number_input("Alto (pulg)", min_value=0.0)
                # Cálculo: (L*A*A)/1728 para convertir pulgadas cúbicas a pies cúbicos
                ft3 = (largo * ancho * alto) / 1728
                st.info(f"Volumen estimado: {ft3:.2f} ft³")
                monto_calculado = ft3 * PRECIO_MARITIMO_FT3
                unidad_medida = "ft³"
                valor_medida = ft3

            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Tipo": f_tipo, "Medida_Inicial": valor_medida, "Unidad": unidad_medida,
                        "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": monto_calculado, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_tipo} {f_id} registrada.")

    with t_val:
        st.subheader("Báscula y Medición de Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para Validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Cliente: {paq['Cliente']} | Tipo: {paq['Tipo']} | Inicial: {paq.get('Medida_Inicial', 0):.2f} {paq.get('Unidad', '')}")
            
            if paq['Tipo'] == "Aéreo":
                val_real = st.number_input("Peso Real Almacén (Kg)", min_value=0.0, value=float(paq.get('Medida_Inicial', 0)), step=0.1)
                monto_final = val_real * PRECIO_AEREO_KG
            else:
                c_l, c_an, c_al = st.columns(3)
                l_v = c_l.number_input("Largo Real (pulg)", min_value=0.0)
                an_v = c_an.number_input("Ancho Real (pulg)", min_value=0.0)
                al_v = c_al.number_input("Alto Real (pulg)", min_value=0.0)
                val_real = (l_v * an_v * al_v) / 1728
                st.write(f"Volumen Final: **{val_real:.2f} ft³**")
                monto_final = val_real * PRECIO_MARITIMO_FT3

            if st.button("⚖️ Validar Medidas"):
                paq['Peso_Almacen'] = val_real # Guardamos en este campo para no romper compatibilidad
                paq['Validado'] = True
                paq['Monto_USD'] = monto_final
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Validado."); st.rerun()
        else: st.info("Sin pendientes.")

    # Las pestañas t_cob, t_est, t_aud y t_res siguen funcionando igual con el nuevo cálculo
    with t_cob:
        st.subheader("Gestión de Cobros")
        pendientes_pago = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_pago:
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']} ({p.get('Tipo', 'Aéreo')})"):
                resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                st.write(f"Total: **${p['Monto_USD']:.2f}** | Pendiente: **${resta:.2f}**")
                monto_abono = st.number_input(f"Abonar a {p['ID_Barra']}", min_value=0.0, max_value=float(resta), key=f"c_{p['ID_Barra']}")
                if st.button(f"Registrar Pago", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] = p.get('Abonado', 0.0) + monto_abono
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
        st.subheader("Auditoría")
        st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True)

    with t_res:
        st.subheader("Resumen de Operaciones")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            m1, m2, m3 = st.columns(3)
            m1.metric("Ingresos Totales", f"${df_res['Monto_USD'].sum():.2f}")
            m2.metric("Paquetes", len(df_res))
            m3.metric("Aéreo vs Marítimo", f"{len(df_res[df_res['Tipo']=='Aéreo'])} / {len(df_res[df_res['Tipo']=='Marítimo'])}")

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    if mis_p:
        st.subheader("📋 Mis Envíos")
        for p in mis_p:
            with st.container():
                st.markdown(f"""
                    <div class="p-card">
                        <span style="color:#60a5fa; font-weight:bold;">#{p['ID_Barra']} ({p.get('Tipo', 'Aéreo')})</span><br>
                        📍 Estado: {p['Estado']}<br>
                        💰 Total: ${p['Monto_USD']:.2f} | Resta: ${p['Monto_USD']-p['Abonado']:.2f}
                    </div>
                """, unsafe_allow_html=True)
    else: st.info("No hay paquetes asociados.")

# --- 6. ACCESO ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <div class="fuente-cursiva" style="font-size: 95px; margin-bottom: 10px; line-height: 1;">IACargo.io</div>
                <p class="fuente-cursiva" style="font-size: 20px; color: #a78bfa !important; white-space: nowrap; margin-top: 0px;">
                    “Trabajamos para conectarte en todas partes del mundo”
                </p>
            </div>
        """, unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registro"])
        with t1:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Iniciar Sesión", use_container_width=True):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Credenciales incorrectas")
        with t2:
            with st.form("signup"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Registrado.")
