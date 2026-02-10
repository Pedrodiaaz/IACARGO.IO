import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite; font-weight: 800;
    }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }
    
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px;
    }

    div[data-testid="stForm"] button {
        background-color: #2563eb !important; color: white !important;
        border-radius: 12px !important; font-weight: 700 !important;
        text-transform: uppercase !important; border: none !important; padding: 10px 20px !important;
    }

    .resumen-row {
        background-color: #ffffff !important; color: #1e293b !important;
        padding: 12px; border-bottom: 1px solid #cbd5e1;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 5px; border-radius: 8px;
    }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }
    
    .badge-paid { background: #059669; color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: #dc2626; color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_UNITARIO = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def cargar_datos(archivo):
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
        return df.to_dict('records')
    return []
def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. INTERFAZ ADMINISTRADOR ---
def render_admin_dashboard():
    st.markdown('<h1 class="logo-animado">Consola de Control Logístico</h1>', unsafe_allow_html=True)
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # [RESTO DE PESTAÑAS MANTIENEN SU LÓGICA RESTAURADA...]
    with t_reg:
        st.subheader("Entrada de Mercancía")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso/Pies inicial", min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_UNITARIO, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Registrado."); st.rerun()

    with t_val:
        st.subheader("⚖️ Validación")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            peso_real = st.number_input("Peso Real detectado:", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if abs(peso_real - paq['Peso_Mensajero']) > 0.5: st.error("🚨 Alarma: Variación de peso.")
            if st.button("⚖️ Confirmar Validación"):
                paq.update({"Peso_Almacen": peso_real, "Validado": True, "Monto_USD": peso_real * PRECIO_UNITARIO})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        st.subheader("💰 Cobros")
        limite = datetime.now() - timedelta(days=15)
        for p in st.session_state.inventario:
            if p['Pago'] != 'PAGADO':
                atrasado = pd.to_datetime(p['Fecha_Registro']) < limite
                label_a = " [ATRASADO]" if atrasado else ""
                with st.expander(f"{p['ID_Barra']} - {p['Cliente']}{label_a}"):
                    monto = st.number_input("Abonar:", 0.0, float(p['Monto_USD']-p['Abonado']), key=f"c_{p['ID_Barra']}")
                    if st.button("Pagar", key=f"btn_{p['ID_Barra']}"):
                        p['Abonado'] += monto
                        if p['Abonado'] >= p['Monto_USD']-0.01: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("✈️ Estados")
        if st.session_state.inventario:
            g_st = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="st_sel")
            e_st = st.selectbox("Estatus:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == g_st: p["Estado"] = e_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    # 🔍 PESTAÑA AUDITORÍA/EDICIÓN (CIRUGÍA AQUÍ)
    with t_aud:
        st.subheader("🔍 Auditoría y Edición Manual")
        busqueda = st.text_input("🔍 Filtrar por ID o Nombre de Cliente:", key="aud_search")
        df_aud = pd.DataFrame(st.session_state.inventario)
        
        if busqueda and not df_aud.empty:
            df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busqueda, case=False) | 
                            df_aud['Cliente'].astype(str).str.contains(busqueda, case=False)]
        
        st.dataframe(df_aud, use_container_width=True)
        
        if not df_aud.empty:
            st.markdown("---")
            st.write("### ✏️ Editor de Registro")
            guia_a_editar = st.selectbox("Seleccione la Guía para modificar o eliminar:", df_aud['ID_Barra'].tolist())
            paq_edit = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_a_editar)
            
            c1, c2, c3 = st.columns(3)
            new_cli = c1.text_input("Nombre Cliente", value=paq_edit['Cliente'])
            new_pes = c2.number_input("Peso/Pies Final", value=float(paq_edit['Peso_Almacen'] if paq_edit['Validado'] else paq_edit['Peso_Mensajero']))
            new_tra = c3.selectbox("Tipo Traslado", ["Aéreo", "Marítimo"], index=0 if paq_edit['Tipo_Traslado']=="Aéreo" else 1)
            
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("💾 Guardar Cambios Manuales", use_container_width=True):
                paq_edit.update({
                    'Cliente': new_cli,
                    'Peso_Almacen': new_pes if paq_edit['Validado'] else 0.0,
                    'Peso_Mensajero': new_pes if not paq_edit['Validado'] else paq_edit['Peso_Mensajero'],
                    'Tipo_Traslado': new_tra,
                    'Monto_USD': new_pes * PRECIO_UNITARIO
                })
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Registro actualizado y monto recalculado."); st.rerun()
            
            if col_b2.button("🗑️ Enviar a Papelera de Seguridad", use_container_width=True):
                st.session_state.papelera.append(paq_edit)
                st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_a_editar]
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA)
                st.warning("Registro movido a la papelera."); st.rerun()

    with t_res:
        st.subheader("📊 Resumen")
        b_res = st.text_input("Código de caja:", key="res_box")
        for k, l in [("RECIBIDO ALMACEN PRINCIPAL", "📦 ALMACÉN"), ("EN TRANSITO", "✈️ TRÁNSITO"), ("ENTREGADO", "✅ ENTREGADO")]:
            items = [p for p in st.session_state.inventario if p['Estado'] == k]
            if b_res: items = [p for p in items if b_res.lower() in p['ID_Barra'].lower()]
            with st.expander(f"{l} ({len(items)})"):
                for r in items:
                    st.markdown(f'<div class="resumen-row"><b>{r["ID_Barra"]}</b><span>{r["Cliente"]}</span><b>${r["Abonado"]:.2f}</b></div>', unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if not mis_p: st.info("Sin paquetes.")
    else:
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f'<div class="p-card"><b>📦 #{p["ID_Barra"]}</b> | {p["Estado"]}', unsafe_allow_html=True)
                st.progress(min(p['Abonado']/p['Monto_USD'], 1.0) if p['Monto_USD']>0 else 0)
                st.write(f"Pago: {p['Pago']} (${p['Abonado']} de ${p['Monto_USD']})")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 5. SIDEBAR Y LOGIN ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown('<h1 class="logo-animado" style="font-size:30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado['nombre']}")
        if st.button("Cerrar Sesión"): st.session_state.usuario_identificado = None; st.rerun()
    st.caption("“La existencia es un milagro”")

if st.session_state.usuario_identificado is None:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
        t_in, t_up = st.tabs(["Ingresar", "Registrarse"])
        with t_in:
            with st.form("l_f"):
                le, lp = st.text_input("Correo"), st.text_input("Clave", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    if le == "admin" and lp == "admin123": st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                    u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                    if u: st.session_state.usuario_identificado = u; st.rerun()
                    else: st.error("Error.")
        with t_up:
            with st.form("s_f"):
                n, e, p = st.text_input("Nombre"), st.text_input("Correo"), st.text_input("Clave", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Listo."); st.rerun()
else:
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
