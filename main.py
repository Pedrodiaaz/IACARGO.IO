import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .p-card {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.3); padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 12px;
    }
    .welcome-text { color: #1e3a8a; font-weight: 900; font-size: 32px; margin-bottom: 10px; }
    .badge-paid { background-color: #d4edda; color: #155724; padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 11px; }
    .badge-debt { background-color: #f8d7da; color: #721c24; padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 11px; }
    .state-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0080ff 100%);
        color: white; padding: 10px 18px; border-radius: 10px; margin: 15px 0; font-weight: 700;
    }
    .btn-eliminar button { background-color: #ff4b4b !important; color: white !important; }
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
    else: st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
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
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
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

    # E. AUDITORÍA / PAPELERA (RESTAURADO COMPLETO)
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

    # F. RESUMEN (CORREGIDO AL FORMATO ORIGINAL)
    with t_res:
        st.subheader("Resumen General de Operaciones")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            m1, m2, m3 = st.columns(3)
            m1.metric("Kg Totales", f"{df_res['Peso_Almacen'].sum():.1f}")
            m2.metric("Paquetes", len(df_res))
            m3.metric("Caja (Abonos)", f"${df_res['Abonado'].sum():.2f}")
            
            for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                df_f = df_res[df_res['Estado'] == est]
                st.markdown(f'<div class="state-header">📦 {est} ({len(df_f)})</div>', unsafe_allow_html=True)
                if not df_f.empty:
                    st.table(df_f[['ID_Barra', 'Cliente', 'Peso_Almacen', 'Pago', 'Monto_USD', 'Abonado']])

# --- 5. PANEL DEL CLIENTE (VISTA COMPACTA Y DISTINGUIBLE) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if not mis_p:
        st.info("No hay paquetes asociados.")
    else:
        st.subheader("📋 Mis Envíos")
        # Usamos columnas para que las tarjetas no ocupen tanto espacio vertical
        col_paq1, col_paq2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (col_paq1 if i % 2 == 0 else col_paq2):
                total = p['Monto_USD']
                abonado = p.get('Abonado', 0.0)
                pago_s = p.get('Pago', 'PENDIENTE')
                badge = "badge-paid" if pago_s == "PAGADO" else "badge-debt"
                
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight:bold; color:#1e3a8a;">#{p['ID_Barra']}</span>
                            <span class="{badge}">{pago_s}</span>
                        </div>
                        <div style="font-size: 0.85em; margin: 8px 0;">
                            📍 <b>{p['Estado']}</b><br>
                            ⚖️ {p['Peso_Almacen'] if p['Validado'] else p['Peso_Mensajero']:.1f} Kg | 💳 {p.get('Modalidad')}
                        </div>
                """, unsafe_allow_html=True)
                # Barra de progreso compacta
                st.progress(abonado/total if total > 0 else 0)
                st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; font-size: 0.8em; margin-top: 5px;">
                            <span>Abonado: <b>${abonado:.2f}</b></span>
                            <span style="color:red;">Resta: <b>${(total-abonado):.2f}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# --- 6. ACCESO ---
else:
    t1, t2 = st.tabs(["Ingresar", "Registro"])
    with t1:
        le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
        if st.button("Iniciar Sesión", use_container_width=True):
            if le == "admin" and lp == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
            if u: st.session_state.usuario_identificado = u; st.rerun()
    with t2:
        with st.form("signup"):
            n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
            if st.form_submit_button("Crear Cuenta"):
                st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Registrado.")
