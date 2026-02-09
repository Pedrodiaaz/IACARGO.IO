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
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3); padding: 25px; border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); margin-bottom: 20px;
    }
    .welcome-text { color: #1e3a8a; font-weight: 900; font-size: 35px; margin-bottom: 5px; }
    .info-msg { 
        background: rgba(255, 255, 255, 0.5); padding: 15px; border-radius: 12px;
        border-left: 5px solid #0080ff; color: #1e3a8a; font-size: 16px; margin-bottom: 25px;
    }
    .badge-paid { background-color: #d4edda; color: #155724; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; }
    .badge-debt { background-color: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; }
    .badge-method { background-color: #e2e3e5; color: #383d41; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; }
    .state-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0080ff 100%);
        color: white; padding: 12px 20px; border-radius: 12px; margin: 20px 0; font-weight: 700;
    }
    .stButton>button { border-radius: 12px; height: 3em; font-weight: 700; text-transform: uppercase; }
    .btn-eliminar button { background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
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
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("🚀 IACargo.io")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Nuevo Ingreso")
        with st.form("reg_form_evolved", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_id = c1.text_input("ID Tracking / Guía")
            f_cli = c1.text_input("Nombre del Cliente")
            f_cor = c1.text_input("Correo del Cliente")
            f_pes = c2.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_metodo = c2.selectbox("Método de Pago:", ["Pago Inmediato", "Cobro Destino", "Pago en Cuotas"])
            
            if st.form_submit_button("Registrar Paquete"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(),
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False,
                        "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                        "Pago": "PENDIENTE", "Metodo_Pago": f_metodo, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_id} registrada con {f_metodo}.")

    with t_val:
        st.subheader("Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado', False)]
        if pendientes:
            guia_v = st.selectbox("Guía para Pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_v)
            st.info(f"Cliente: {paq['Cliente']} | Peso Mensajero: {paq['Peso_Mensajero']} Kg")
            peso_real = st.number_input("Peso Real Báscula (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("Confirmar Peso Real"):
                paq.update({'Peso_Almacen': peso_real, 'Validado': True, 'Monto_USD': peso_real * PRECIO_POR_KG})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else: st.info("No hay paquetes pendientes por validar.")

    with t_cob:
        st.subheader("Módulo de Cobranza")
        if st.session_state.inventario:
            df_c = pd.DataFrame(st.session_state.inventario)
            c_p, c_pa = st.columns(2)
            with c_p:
                st.markdown("### 🟡 PENDIENTES")
                for idx, r in df_c[df_c['Pago'] == 'PENDIENTE'].iterrows():
                    st.write(f"**{r['ID_Barra']}** - ${r['Monto_USD']:.2f} | {r['Metodo_Pago']}")
                    if st.button(f"Cobrar {r['ID_Barra']}", key=f"pay_{idx}"):
                        for p in st.session_state.inventario:
                            if p['ID_Barra'] == r['ID_Barra']: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
            with c_pa:
                st.markdown("### 🟢 PAGADOS")
                st.dataframe(df_c[df_c['Pago'] == 'PAGADO'][['ID_Barra', 'Cliente', 'Monto_USD']], hide_index=True)

    with t_est:
        st.subheader("Movimiento Logístico")
        if st.session_state.inventario:
            guia_st = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="st_guia")
            nuevo_est = st.selectbox("Cambiar Estado a:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == guia_st: p["Estado"] = nuevo_est
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Actualizado."); st.rerun()

    with t_aud:
        col_a1, col_a2 = st.columns([3, 1])
        with col_a1: st.subheader("Auditoría de Datos")
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
        else:
            df_aud = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df_aud, use_container_width=True)
            st.write("---")
            guia_ed = st.selectbox("Editar ID:", [p["ID_Barra"] for p in st.session_state.inventario], key="ed_select")
            paq_ed = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed), None)
            if paq_ed:
                if st.button("🗑️ Eliminar Paquete", key="btn_del"):
                    st.session_state.papelera.append(paq_ed)
                    st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_ed]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()

    with t_res:
        st.subheader("Resumen Operativo")
        if st.session_state.inventario:
            df_r = pd.DataFrame(st.session_state.inventario)
            m1, m2, m3 = st.columns(3)
            m1.metric("Kg Totales", f"{df_r['Peso_Almacen'].sum():.1f}")
            m2.metric("Paquetes", len(df_r))
            m3.metric("Recaudado", f"${df_r[df_r['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")
            for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                st.markdown(f'<div class="state-header">📦 {est}</div>', unsafe_allow_html=True)
                df_filtro = df_r[df_r['Estado'] == est]
                if not df_filtro.empty: st.dataframe(df_filtro[['ID_Barra', 'Cliente', 'Monto_USD', 'Pago']], hide_index=True, use_container_width=True)

# --- 5. PANEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if not mis_p:
        st.markdown('<div class="info-msg">Por el momento no tienes paquetes asociados a tu perfil, si tu paquete fue recibido recientemente por nuestro equipo de trabajo pronto te reflejaremos de acuerdo a lo entregado</div>', unsafe_allow_html=True)
    else:
        for p in mis_p:
            monto = p.get('Monto_USD', 0.0)
            metodo = p.get('Metodo_Pago', 'Pago Inmediato')
            status = p.get('Pago', 'PENDIENTE')
            peso = p.get('Peso_Almacen', 0.0) if p.get('Validado') else p.get('Peso_Mensajero', 0.0)
            
            st.markdown(f"""
                <div class="p-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin:0; color:#1e3a8a;">Guía: {p['ID_Barra']}</h3>
                        <div>
                            <span class="badge-method">{metodo.upper()}</span>
                            <span class="{"badge-paid" if status=="PAGADO" else "badge-debt"}">{status}</span>
                        </div>
                    </div>
                    <p style="margin:10px 0;">Estado Actual: <b>{p['Estado']}</b></p>
                    <div style="display: flex; justify-content: space-around; background:rgba(255,255,255,0.4); padding:10px; border-radius:15px;">
                        <div style="text-align:center;"><small>Peso</small><br><b>{peso:.2f} Kg</b></div>
                        <div style="text-align:center;"><small>Total Traslado</small><br><b>${monto:.2f}</b></div>
                    </div>
            """, unsafe_allow_html=True)
            
            if metodo == "Pago en Cuotas":
                st.markdown(f"""
                    <div style="margin-top:15px; border-top: 1px dashed #0080ff; padding-top:10px;">
                        <p style="font-size:14px; font-weight:bold; color:#1e3a8a; margin-bottom:5px;">🗓️ Cronograma de Cuotas:</p>
                        <table style="width:100%; font-size:13px; color:#333;">
                            <tr><td>Inicial (30%):</td><td style="text-align:right;"><b>${monto*0.30:.2f}</b></td></tr>
                            <tr><td>Cuota 1 (35% - Quincenal):</td><td style="text-align:right;"><b>${monto*0.35:.2f}</b></td></tr>
                            <tr><td>Cuota 2 (35% - Quincenal):</td><td style="text-align:right;"><b>${monto*0.35:.2f}</b></td></tr>
                        </table>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- 6. LOGIN ---
else:
    t1, t2 = st.tabs(["Ingresar", "Registrarse"])
    with t1:
        le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
        if st.button("Entrar"):
            if le == "admin" and lp == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            u_db = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
            if u_db: st.session_state.usuario_identificado = u_db; st.rerun()
            else: st.error("Acceso denegado.")
    with t2:
        with st.form("sign"):
            nn = st.text_input("Nombre"); ne = st.text_input("Email"); np = st.text_input("Clave", type="password")
            if st.form
