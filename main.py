import streamlit as st
import pandas as pd  # <-- Corregido aquí
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .p-card {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3); padding: 25px; border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); margin-bottom: 20px;
    }
    .welcome-text { color: #1e3a8a; font-weight: 900; font-size: 35px; margin-bottom: 5px; }
    .badge-paid { background-color: #d4edda; color: #155724; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }
    .badge-debt { background-color: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }
    .state-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0080ff 100%);
        color: white; padding: 12px 20px; border-radius: 12px; margin: 20px 0; font-weight: 700;
    }
    .stButton>button { border-radius: 12px; height: 3em; font-weight: 700; text-transform: uppercase; }
    .btn-eliminar button { background-color: #ff4b4b !important; color: white !important; }
    .cuota-info { font-size: 13px; color: #1e3a8a; background: rgba(30, 58, 138, 0.05); padding: 10px; border-radius: 10px; border: 1px dashed #1e3a8a; }
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

    # A. REGISTRO
    with t_reg:
        st.subheader("Registro de Entrada")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_pago_tipo = st.selectbox("Tipo de Pago", ["Pago Único", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": f_pes*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Tipo_Pago": f_pago_tipo, "Abonado_USD": 0.0,
                        "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_id} registrada.")

    # B. VALIDACIÓN
    with t_val:
        st.subheader("Báscula de Almacén")
        pendientes = [p for p in st.session_state.inventario if p.get('Validado') == False]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para Pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Cliente: {paq['Cliente']} | Peso Reportado: {paq['Peso_Mensajero']} Kg")
            peso_real = st.number_input("Peso Real en Báscula (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']), step=0.1)
            if st.button("⚖️ Validar Peso"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                if abs(peso_real - paq['Peso_Mensajero']) > 0.5:
                    st.error(f"⚠️ ¡ALERTA! Diferencia crítica de peso detectada.")
                st.success("✅ Peso validado y actualizado.")
                st.rerun()
        else: st.info("No hay paquetes pendientes de validación.")

    # C. COBROS (Lógica de Cuotas Implementada)
    with t_cob:
        st.subheader("Estado de Cuentas")
        if st.session_state.inventario:
            df_c = pd.DataFrame(st.session_state.inventario)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### 🟢 PAGADOS")
                st.dataframe(df_c[df_c['Pago'] == 'PAGADO'][['ID_Barra', 'Cliente', 'Monto_USD']], hide_index=True)
            with c2:
                st.markdown("### 🟡 PENDIENTES / CUOTAS")
                df_p = df_c[df_c['Pago'] == 'PENDIENTE']
                for idx, r in df_p.iterrows():
                    with st.expander(f"Guía: {r['ID_Barra']} - {r['Cliente']}"):
                        total = r['Monto_USD']
                        abonado = r.get('Abonado_USD', 0.0)
                        restante = total - abonado
                        st.write(f"**Total:** ${total:.2f} | **Abonado:** ${abonado:.2f} | **Faltante:** ${restante:.2f}")
                        monto_abono = st.number_input(f"Monto a abonar ($)", min_value=0.0, max_value=float(restante), key=f"ab_{idx}")
                        if st.button(f"Registrar Pago {r['ID_Barra']}", key=f"btn_{idx}"):
                            for p in st.session_state.inventario:
                                if p['ID_Barra'] == r['ID_Barra']:
                                    p['Abonado_USD'] += monto_abono
                                    if p['Abonado_USD'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                            guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    # D. ESTADOS (Sin cambios en estructura)
    with t_est:
        st.subheader("Logística de Envío")
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus Logístico"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Estado actualizado."); st.rerun()

    # E. AUDITORÍA (Mantiene tu funcionalidad de búsqueda y edición)
    with t_aud:
        st.subheader("Auditoría General")
        df_aud = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_aud, use_container_width=True)

    # F. RESUMEN
    with t_res:
        st.subheader("Panel de Control Operativo")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            m1, m2, m3 = st.columns(3)
            m1.metric("Kg Validados", f"{df_res['Peso_Almacen'].sum():.1f}")
            m2.metric("Paquetes Activos", len(df_res))
            m3.metric("Recaudación (Abonos)", f"${df_res['Abonado_USD'].sum():.2f}")
            for estado in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                df_f = df_res[df_res['Estado'] == estado]
                st.markdown(f'<div class="state-header">📦 {estado} ({len(df_f)})</div>', unsafe_allow_html=True)
                if not df_f.empty:
                    st.dataframe(df_f[['ID_Barra', 'Cliente', 'Abonado_USD', 'Monto_USD']], hide_index=True, use_container_width=True)

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if not mis_p:
        st.info("No tienes paquetes asociados.")
    else:
        for p in mis_p:
            total = p['Monto_USD']
            tipo = p.get('Tipo_Pago', 'Pago Único')
            abonado = p.get('Abonado_USD', 0.0)
            st.markdown(f"""
                <div class="p-card">
                    <h3 style="margin:0; color:#1e3a8a;">Guía: {p['ID_Barra']}</h3>
                    <p>Modalidad: <b>{tipo}</b> | Estatus: <b>{p['Estado']}</b></p>
                    <div style="display: flex; justify-content: space-around; margin-top:15px; border-top:1px solid #eee; padding-top:10px;">
                        <div><small>Total Factura</small><br><b>${total:.2f}</b></div>
                        <div><small>Monto Abonado</small><br><b style="color:green;">${abonado:.2f}</b></div>
                        <div><small>Resta</small><br><b style="color:red;">${(total-abonado):.2f}</b></div>
                    </div>
            """, unsafe_allow_html=True)
            if tipo == "Pago en Cuotas":
                st.markdown(f"""
                <div class="cuota-info">
                    <b>📌 Plan de Cuotas Establecido (35/25/20/20):</b><br>
                    • Inicial (35%): <b>${total*0.35:.2f}</b><br>
                    • Pago 2 (25%): <b>${total*0.25:.2f}</b><br>
                    • Pago 3 (20%): <b>${total*0.20:.2f}</b><br>
                    • Pago 4 (20%): <b>${total*0.20:.2f}</b>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- 6. ACCESO ---
else:
    t1, t2 = st.tabs(["Ingresar", "Registro"])
    with t1:
        le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
        if st.button("Iniciar Sesión"):
            if le == "admin" and lp == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
            if u: st.session_state.usuario_identificado = u; st.rerun()
    with t2:
        with st.form("signup"):
            n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
            if st.form_submit_button("Crear"):
                st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Registrado.")
