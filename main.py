import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

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

    /* BOTÓN DE REGISTRO AZUL PERMANENTE */
    div[data-testid="stForm"]  button {
        background-color: #2563eb !important;
        background-image: none !important;
        color: white !important;
        border: 1px solid #60a5fa !important;
        opacity: 1 !important;
        transition: none !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }

    .header-resumen {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.1em;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-left: 6px solid #60a5fa;
    }

    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 15px;
        border-bottom: 2px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
        border-radius: 4px;
    }
    .resumen-id { font-weight: 800; color: #2563eb; width: 150px; }
    .resumen-cliente { flex-grow: 1; font-weight: 500; font-size: 1.1em; }
    .resumen-data { font-weight: 700; color: #475569; text-align: right; }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-debt { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
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
    else: st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None; st.rerun()
    else: rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
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
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": f_pes * PRECIO_POR_UNIDAD, 
                        "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", 
                        "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success(f"✅ Guía {f_id} registrada."); st.rerun()

    with t_val:
        st.subheader("⚖️ Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            u_medida = "Pies Cúbicos" if paq.get('Tipo_Traslado') == "Marítimo" else "Kg"
            st.info(f"Cliente: {paq['Cliente']} | Reportado: {paq['Peso_Mensajero']} {u_medida}")
            
            peso_real = st.number_input(f"Medida Real en Almacén ({u_medida})", min_value=0.0, value=float(paq['Peso_Mensajero']), step=0.1)
            
            if st.button("⚖️ Confirmar y Validar"):
                paq['Peso_Almacen'] = peso_real; paq['Validado'] = True; paq['Monto_USD'] = peso_real * PRECIO_POR_UNIDAD
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Validado exitosamente."); st.rerun()
        else: st.info("No hay paquetes pendientes de validación.")

    with t_cob:
        st.subheader("💰 Gestión de Cobros")
        pendientes_pago = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_pago:
            with st.expander(f"💵 {p['ID_Barra']} - {p['Cliente']}"):
                resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                st.write(f"Modalidad: **{p.get('Modalidad')}** | Restante: **${resta:.2f}**")
                monto_abono = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"c_{p['ID_Barra']}")
                if st.button(f"Registrar Pago", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] = p.get('Abonado', 0.0) + monto_abono
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("✈️ Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Estatus actualizado."); st.rerun()

    with t_aud:
        col_a1, col_a2 = st.columns([3, 1])
        with col_a1: st.subheader("🔍 Auditoría")
        with col_a2: ver_p = st.checkbox("🗑️ Ver Papelera")
        
        if ver_p:
            if st.session_state.papelera:
                guia_res = st.selectbox("Restaurar ID:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("♻️ Restaurar Guía"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
        else:
            busq = st.text_input("🔍 Buscar por Guía:")
            df_aud = pd.DataFrame(st.session_state.inventario)
            if busq: df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            
            if st.session_state.inventario:
                guia_ed = st.selectbox("Editar ID:", [p["ID_Barra"] for p in st.session_state.inventario])
                paq_ed = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed), None)
                if paq_ed:
                    c1, c2, c3 = st.columns(3)
                    label_ed = "Pies Cúbicos" if paq_ed.get('Tipo_Traslado') == "Marítimo" else "Peso (Kg)"
                    with c1: n_cli = st.text_input("Cliente", value=paq_ed['Cliente'])
                    with c2: n_pes = st.number_input(label_ed, value=float(paq_ed['Peso_Almacen']))
                    with c3: n_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo"], index=0 if paq_ed.get('Tipo_Traslado')=="Aéreo" else 1)
                    if st.button("💾 Guardar"):
                        paq_ed.update({'Cliente': n_cli, 'Peso_Almacen': n_pes, 'Tipo_Traslado': n_tra, 'Monto_USD': n_pes*PRECIO_POR_UNIDAD})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
                    st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar"):
                        st.session_state.papelera.append(paq_ed)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with t_res:
        st.subheader("📊 Resumen General")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            busq_res = st.text_input("🔍 Buscar caja:", key="res_search")
            if busq_res: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
            
            estados = {"RECIBIDO ALMACEN PRINCIPAL": "📦 Almacén", "EN TRANSITO": "✈️ Tránsito", "ENTREGADO": "✅ Entregado"}
            
            for est_key, est_label in estados.items():
                df_f = df_res[df_res['Estado'] == est_key].copy()
                st.markdown(f'<div class="header-resumen">{est_label} ({len(df_f)})</div>', unsafe_allow_html=True)
                for _, row in df_f.iterrows():
                    # --- ICONO DINÁMICO EN RESUMEN ---
                    icon = "✈️" if row.get('Tipo_Traslado') == "Aéreo" else "🚢"
                    u_r = "Pies" if row.get('Tipo_Traslado') == "Marítimo" else "Kg"
                    st.markdown(f"""
                        <div class="resumen-row">
                            <div class="resumen-id">{icon} {row['ID_Barra']}</div>
                            <div class="resumen-cliente">{row['Cliente']}</div>
                            <div class="resumen-data">{row['Peso_Almacen']:.1f} {u_r} | {row['Pago']} | ${row['Abonado']:.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if not mis_p: st.info("No tienes envíos registrados.")
    else:
        col_p1, col_p2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (col_p1 if i % 2 == 0 else col_p2):
                tot = p['Monto_USD']; abo = p.get('Abonado', 0.0); uni = "Pies" if p.get('Tipo_Traslado') == "Marítimo" else "Kg"
                badge = "badge-paid" if p.get('Pago') == "PAGADO" else "badge-debt"
                # --- ICONO DINÁMICO EN PANEL CLIENTE ---
                icon_cli = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#60a5fa; font-weight:bold; font-size:1.2em;">{icon_cli} #{p['ID_Barra']}</span>
                            <span class="{badge}">{p.get('Pago')}</span>
                        </div>
                        <div style="font-size:0.9em; margin:10px 0;">
                            📍 <b>Estado:</b> {p['Estado']}<br>
                            ⚖️ <b>Medida:</b> {p['Peso_Almacen'] if p['Validado'] else p['Peso_Mensajero']:.1f} {uni}
                        </div>
                """, unsafe_allow_html=True)
                st.progress(abo/tot if tot > 0 else 0)
                st.markdown(f"""<div style="display:flex; justify-content:space-between; font-size:0.85em;">
                            <span>Abonado: <b>${abo:.2f}</b></span>
                            <span style="color:#f87171;">Resta: <b>${(tot-abo):.2f}</b></span>
                        </div></div>""", unsafe_allow_html=True)

# --- 6. LOGIN ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registrarse"])
        with t1:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Entrar", use_container_width=True):
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
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Cuenta creada."); st.rerun()
