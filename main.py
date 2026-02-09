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
        st.subheader("Registro de Paquete")
        with st.form("reg_form_v3", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_id = c1.text_input("ID Tracking / Guía")
            f_cli = c1.text_input("Nombre del Cliente")
            f_cor = c1.text_input("Correo del Cliente")
            f_pes = c2.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_metodo = c2.selectbox("Método de Pago:", ["Pago Inmediato", "Cobro Destino", "Pago en Cuotas"])
            
            if st.form_submit_button("Registrar en Sistema"):
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
        st.subheader("Validación de Peso")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado', False)]
        if pendientes:
            guia_v = st.selectbox("ID para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_v)
            peso_real = st.number_input("Peso Real Almacén (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("⚖️ Confirmar Validación"):
                paq.update({'Peso_Almacen': peso_real, 'Validado': True, 'Monto_USD': peso_real * PRECIO_POR_KG})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else: st.info("No hay paquetes pendientes.")

    with t_cob:
        st.subheader("Control de Cobros")
        if st.session_state.inventario:
            df_c = pd.DataFrame(st.session_state.inventario)
            c_pen, c_pag = st.columns(2)
            with c_pen:
                st.markdown("### 🟡 PENDIENTES")
                for idx, r in df_c[df_c['Pago'] == 'PENDIENTE'].iterrows():
                    st.write(f"**{r['ID_Barra']}** - ${r['Monto_USD']:.2f} ({r['Metodo_Pago']})")
                    if st.button(f"Marcar Pago {r['ID_Barra']}", key=f"pay_{idx}"):
                        for p in st.session_state.inventario:
                            if p['ID_Barra'] == r['ID_Barra']: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
            with c_pag:
                st.markdown("### 🟢 PAGADOS")
                st.dataframe(df_c[df_c['Pago'] == 'PAGADO'][['ID_Barra', 'Cliente', 'Monto_USD']], hide_index=True)

    with t_est:
        st.subheader("Control de Estados")
        if st.session_state.inventario:
            guia_st = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_est = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == guia_st: p["Estado"] = n_est
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        col_a1, col_a2 = st.columns([3, 1])
        with col_a1: st.subheader("Auditoría y Papelera")
        with col_a2: ver_p = st.checkbox("🗑️ Ver Papelera")
        if ver_p:
            if st.session_state.papelera:
                st.dataframe(pd.DataFrame(st.session_state.papelera), use_container_width=True)
                guia_res = st.selectbox("Restaurar:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("♻️ Restaurar"):
                    paq_r = next(p for p in st.session_state.papelera if p["ID_Barra"] == guia_res)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()
        else:
            st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True)
            guia_el = st.selectbox("ID para eliminar:", [p["ID_Barra"] for p in st.session_state.inventario])
            if st.button("🗑️ Eliminar a Papelera"):
                paq_el = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_el)
                st.session_state.papelera.append(paq_el)
                st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_el]
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()

    with t_res:
        st.subheader("Resumen General")
        if st.session_state.inventario:
            df_r = pd.DataFrame(st.session_state.inventario)
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("Kg Validados", f"{df_r['Peso_Almacen'].sum():.1f}")
            c_m2.metric("Paquetes Activos", len(df_r))
            c_m3.metric("Recaudación", f"${df_r[df_r['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    
    if not mis_p:
        st.markdown('<div class="info-msg">No tienes paquetes registrados todavía...</div>', unsafe_allow_html=True)
    else:
        for p in mis_p:
            monto = p.get('Monto_USD', 0.0)
            metodo = p.get('Metodo_Pago', 'Pago Inmediato')
            status = p.get('Pago', 'PENDIENTE')
            peso = p.get('Peso_Almacen', 0.0) if p.get('Validado') else p.get('Peso_Mensajero', 0.0)
            
            st.markdown(f"""
                <div class="p-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h3 style="margin:0; color:#1e3a8a;">Guía: {p['ID_Barra']}</h3>
                        <div>
                            <span class="badge-method">{metodo.upper()}</span>
                            <span class="{"badge-paid" if status=="PAGADO" else "badge-debt"}">{status}</span>
                        </div>
                    </div>
                    <p style="margin:10px 0;">Estado: <b>{p['Estado']}</b></p>
                    <div style="display: flex; justify-content: space-around; border-top:1px solid #eee; padding-top:10px;">
                        <div><small>Peso</small><br><b>{peso:.2f} Kg</b></div>
                        <div><small>Total</small><br><b>${monto:.2f}</b></div>
                    </div>
            """, unsafe_allow_html=True)
            
            if metodo == "Pago en Cuotas":
                st.markdown(f"""
                    <div style="margin-top:10px; padding:10px; border: 1px dashed #0080ff; border-radius:10px; background:rgba(0,128,255,0.05);">
                        <p style="margin:0; font-size:13px; font-weight:bold; color:#1e3a8a;">Plan Quincenal:</p>
                        <p style="margin:0; font-size:12px;">• Inicial (30%): ${monto*0.30:.2f}</p>
                        <p style="margin:0; font-size:12px;">• Pago 1 (35%): ${monto*0.35:.2f}</p>
                        <p style
