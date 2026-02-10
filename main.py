import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTRICTA) ---
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

# --- 3. INTERFAZ ADMINISTRADOR (CIRUGÍA FUNCIONAL) ---
def render_admin_dashboard():
    st.markdown('<h1 class="logo-animado">Consola de Control Logístico</h1>', unsafe_allow_html=True)
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # 📝 REGISTRO: Captura de peso inicial
    with t_reg:
        st.subheader("Entrada de Mercancía")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
        label_din = "Pies Cúbicos iniciales" if f_tra == "Marítimo" else "Peso Mensajero inicial (Kg)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_UNITARIO, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Registrado."); st.rerun()

    # ⚖️ VALIDACIÓN: Re-pesaje y Alarma de variación
    with t_val:
        st.subheader("⚖️ Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Guía para pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Reportado por mensajero: {paq['Peso_Mensajero']}")
            peso_real = st.number_input("Peso Real detectado:", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if abs(peso_real - paq['Peso_Mensajero']) > 0.5:
                st.error(f"🚨 ALARMA: Diferencia de {abs(peso_real - paq['Peso_Mensajero']):.2f} unidades.")
            if st.button("⚖️ Validar y Actualizar Peso"):
                paq.update({"Peso_Almacen": peso_real, "Validado": True, "Monto_USD": peso_real * PRECIO_UNITARIO})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Peso validado."); st.rerun()
        else: st.info("No hay paquetes pendientes de validación.")

    # 💰 COBROS: Pagados, Pendientes y Atrasados (>15 días)
    with t_cob:
        st.subheader("💰 Gestión Financiera")
        inv = st.session_state.inventario
        limite = datetime.now() - timedelta(days=15)
        
        pagados = [p for p in inv if p['Pago'] == 'PAGADO']
        atrasados = [p for p in inv if p['Pago'] != 'PAGADO' and pd.to_datetime(p['Fecha_Registro']) < limite]
        pendientes = [p for p in inv if p['Pago'] == 'PENDIENTE' and p not in atrasados]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Pagados", len(pagados))
        c2.metric("Pendientes", len(pendientes))
        c3.metric("Atrasados (+15d)", len(atrasados), delta_color="inverse")
        
        sel = st.selectbox("Ver listado de:", ["Pendientes", "Atrasados", "Pagados"])
        lista_cobro = atrasados if sel == "Atrasados" else pagados if sel == "Pagados" else pendientes
        
        for p in lista_cobro:
            with st.expander(f"📦 {p['ID_Barra']} - {p['Cliente']}"):
                falta = p['Monto_USD'] - p['Abonado']
                st.write(f"Total: ${p['Monto_USD']:.2f} | Abonado: ${p['Abonado']:.2f}")
                if p['Pago'] != 'PAGADO':
                    monto = st.number_input("Abonar:", 0.0, float(falta), key=f"c_{p['ID_Barra']}")
                    if st.button("Registrar Pago", key=f"btn_{p['ID_Barra']}"):
                        p['Abonado'] += monto
                        if p['Abonado'] >= p['Monto_USD'] - 0.01: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    # ✈️ ESTADOS: Ciclo de vida
    with t_est:
        st.subheader("✈️ Actualizar Estatus")
        if inv:
            guia_st = st.selectbox("Guía:", [p["ID_Barra"] for p in inv], key="st_sel")
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Confirmar Cambio de Estatus"):
                for p in inv:
                    if p["ID_Barra"] == guia_st: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Estatus actualizado."); st.rerun()

    # 🔍 AUDITORÍA/EDICIÓN: Búsqueda y Papelera
    with t_aud:
        st.subheader("🔍 Auditoría")
        df_inv = pd.DataFrame(inv)
        st.dataframe(df_inv, use_container_width=True)
        if inv:
            guia_ed = st.selectbox("Seleccione ID para Acción:", [p["ID_Barra"] for p in inv])
            if st.button("🗑️ Enviar a Papelera"):
                paq = next(p for p in inv if p["ID_Barra"] == guia_ed)
                st.session_state.papelera.append(paq)
                st.session_state.inventario = [p for p in inv if p["ID_Barra"] != guia_ed]
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()

    # 📊 RESUMEN: Seccionado por los 3 tipos de estado
    with t_res:
        st.subheader("📊 Resumen General")
        busq_res = st.text_input("🔍 Buscar caja por código:", key="res_search_box")
        for est_k, est_l in [("RECIBIDO ALMACEN PRINCIPAL", "📦 EN ALMACÉN"), ("EN TRANSITO", "✈️ EN TRÁNSITO"), ("ENTREGADO", "✅ ENTREGADO")]:
            items = [p for p in st.session_state.inventario if p['Estado'] == est_k]
            if busq_res: items = [p for p in items if busq_res.lower() in p['ID_Barra'].lower()]
            with st.expander(f"{est_l} ({len(items)})", expanded=True):
                for r in items:
                    icon = "✈️" if r.get('Tipo_Traslado') == "Aéreo" else "🚢"
                    st.markdown(f'<div class="resumen-row"><b>{icon} {r["ID_Barra"]}</b><span>{r["Cliente"]}</span><b>${r["Abonado"]:.2f}</b></div>', unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE (RESTAURADA) ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    
    if not mis_p: st.info("No hay paquetes asociados a tu cuenta.")
    else:
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                tot = float(p.get('Monto_USD', 1.0)); abo = float(p.get('Abonado', 0.0))
                badge = "badge-paid" if p.get('Pago') == "PAGADO" else "badge-debt"
                st.markdown(f'<div class="p-card"><div style="display:flex; justify-content:space-between;">'
                            f'<span style="color:#60a5fa; font-weight:800; font-size:1.3em;">📦 #{p["ID_Barra"]}</span>'
                            f'<span class="{badge}">{p.get("Pago")}</span></div>'
                            f'<div style="margin:10px 0;">📍 <b>Estado:</b> {p["Estado"]}</div>', unsafe_allow_html=True)
                st.progress(min(abo/tot, 1.0)) # BARRA DE PAGO RECUPERADA
                st.markdown(f'<div style="display:flex; justify-content:space-between; margin-top:8px; font-weight:bold;">'
                            f'<div style="color:#10b981;">Pagado: ${abo:.2f}</div><div style="color:#f87171;">Total: ${tot:.2f}</div></div></div>', unsafe_allow_html=True)

# --- 5. LOGO Y LOGIN ---
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
                le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    if le == "admin" and lp == "admin123":
                        st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                    u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                    if u: st.session_state.usuario_identificado = u; st.rerun()
                    else: st.error("Acceso denegado.")
        with t_up:
            with st.form("s_f"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Registrado."); st.rerun()
else:
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
