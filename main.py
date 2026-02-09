import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
PRECIO_POR_KG = 5.0
ARCHIVO_DB = "inventario_logistica.csv"
# --- CREDENCIALES ---
ADMIN_USER = "admin"
ADMIN_PASS = "admin123" # ¡CAMBIA ESTA CONTRASEÑA EN UN ENTORNO REAL!

# --- MOTOR DE PERSISTENCIA (MEMORIA ETERNA) ---
def guardar_datos():
    if not inventario: # Evita guardar un DataFrame vacío al inicio
        return 
    df = pd.DataFrame(inventario)
    df.to_csv(ARCHIVO_DB, index=False)
    # print(f"💾 Respaldo automático realizado en {ARCHIVO_DB}") # Silenciado para la interfaz final

def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        try:
            # print("⏳ Recuperando datos de la memoria...") # Silenciado para la interfaz final
            return pd.read_csv(ARCHIVO_DB).to_dict('records')
        except Exception as e:
            # print(f"⚠️ Error al cargar datos: {e}. Iniciando con datos vacíos.") # Silenciado
            return []
    return []

# --- INICIALIZACIÓN ---
inventario = cargar_datos()

# --- NOTIFICACIONES ---
def enviar_notificacion(paquete, tipo):
    print(f"\n📧 [NOTIFICACIÓN A: {paquete['Correo']}]")
    if tipo == "pago":
        print(f"PAGO RECIBIDO: Su envío {paquete['ID_Barra']} por ${paquete['Monto_USD']} está solvente.")
    elif tipo == "alerta":
        print(f"ALERTA: Discrepancia de peso en {paquete['ID_Barra']}. Verificación requerida.")
    else:
        print(f"ESTATUS: Su paquete {paquete['ID_Barra']} cambió a: {paquete['Estado']}.")

# --- OPERACIONES (Admin) ---

def registrar_mercancia():
    print("\n--- 📦 1. REGISTRO Y COTIZACIÓN ---")
    id_p = input("ID Único: ")
    cli = input("Nombre del Cliente: ")
    cor = input("Correo: ")
    des = input("Contenido: ")
    try:
        peso_input = input("Peso en báscula (kg): ")
        peso = float(peso_input)
        monto = peso * PRECIO_POR_KG
        print(f"💰 COTIZACIÓN: ${monto}")
        pago = input(f"¿Paga ahora? (S/N): ").upper()
        estatus_pago = "PAGADO" if pago == "S" else "PENDIENTE"
        
        paquete = {
            "ID_Barra": id_p, "Cliente": cli, "Correo": cor,
            "Descripcion": des, "Peso_Origen": peso, "Peso_Almacen": 0.0, 
            "Monto_USD": monto, "Estado": "Recogido en casa", "Pago": estatus_pago,
            "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        inventario.append(paquete)
        guardar_datos()
        print(f"✅ REGISTRADO.")
        enviar_notificacion(paquete, "registro")
    except ValueError:
        print("❌ Error: Por favor ingresa un número para el peso (usa punto para decimales).")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def verificar_y_pesar():
    print("\n--- 🏗️ 2. VALIDACIÓN DE PESO ---")
    id_p = input("ID del paquete: ")
    for p in inventario:
        if p["ID_Barra"] == id_p:
            try:
                p_real = float(input(f"Peso en almacén (kg): "))
                p["Peso_Almacen"] = p_real
                diff = abs(p_real - p["Peso_Origen"])
                if diff > (p["Peso_Origen"] * 0.05):
                    p["Estado"] = "🔴 RETENIDO: DISCREPANCIA"
                    enviar_notificacion(p, "alerta")
                else:
                    p["Estado"] = "🟢 VERIFICADO EN ALMACÉN"
                    enviar_notificacion(p, "estatus")
                guardar_datos()
                print("✅ Verificación completada.")
                return
            except ValueError:
                print("❌ Error: Por favor ingresa un número válido para el peso.")
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
    print("❌ ID no encontrado.")

def gestionar_pago():
    print("\n--- 💰 3. GESTIÓN DE COBROS ---")
    id_p = input("ID del paquete: ")
    for p in inventario:
        if p["ID_Barra"] == id_p:
            if p["Pago"] == "PENDIENTE":
                if input(f"¿Confirmar pago de ${p['Monto_USD']}? (S/N): ").upper() == "S":
                    p["Pago"] = "PAGADO"
                    guardar_datos()
                    enviar_notificacion(p, "pago")
            else: print("Este paquete ya está solvente.")
            return
    print("❌ No encontrado.")

def actualizar_estatus():
    print("\n--- 🔄 4. CONTROL DE TRÁNSITO ---")
    id_p = input("ID: ")
    for p in inventario:
        if p["ID_Barra"] == id_p:
            print("1. Tránsito Int. | 2. Aduana | 3. Entregado")
            op = input("Opción: ")
            estados = {"1": "En Tránsito Internacional", "2": "En Aduana", "3": "Entregado"}
            if op in estados:
                p["Estado"] = estados[op]
                guardar_datos()
                enviar_notificacion(p, "estatus")
            return
    print("❌ ID no encontrado.")

def reporte_general_admin():
    print("\n--- 📋 5. REPORTE DE AUDITORÍA ---")
    if not inventario: print("No hay datos registrados.")
    else: print(pd.DataFrame(inventario)[["ID_Barra", "Cliente", "Monto_USD", "Pago", "Estado", "Peso_Origen", "Peso_Almacen", "Fecha_Registro"]])

# --- OPERACIÓN (Cliente y Admin) ---
def buscar_paquete_cliente_o_admin(id_buscar):
    print("\n--- 🔍 RASTREO DE PAQUETE ---")
    for p in inventario:
        if p["ID_Barra"] == id_buscar:
            print("\n" + "="*40)
            print(f"   DETALLE DE ENVÍO: {id_buscar}")
            print("="*40)
            print(f"Cliente:      {p['Cliente']}")
            print(f"Descripción:  {p['Descripcion']}")
            print(f"Estado:       {p['Estado']}")
            print(f"Estatus Pago: {p['Pago']}")
            print(f"Monto:        ${p['Monto_USD']:.2f}")
            print(f"Peso Origen:  {p['Peso_Origen']} kg")
            print(f"Peso Almacén: {p['Peso_Almacen']} kg")
            print(f"Registrado:   {p['Fecha_Registro']}")
            print("="*40)
            return True
    print("❌ Paquete no localizado. Verifique el ID.")
    return False

# --- PANELES DE USUARIO ---
def panel_admin():
    while True:
        print(f"\n{'='*48}\n  PANEL DE ADMINISTRACIÓN (TÚ)\n{'='*48}")
        print("1. Registro | 2. Pesaje | 3. Cobro | 4. Tránsito")
        print("5. Reporte Auditoría | 6. Rastreo por ID | 7. Salir")
        op = input("\nSelección: ")
        if op=="1": registrar_mercancia()
        elif op=="2": verificar_y_pesar()
        elif op=="3": gestionar_pago()
        elif op=="4": actualizar_estatus()
        elif op=="5": reporte_general_admin()
        elif op=="6": 
            id_busqueda = input("Ingrese el ID del paquete a rastrear: ")
            buscar_paquete_cliente_o_admin(id_busqueda)
        elif op=="7": break
        else: print("Opción no válida.")

def panel_cliente():
    while True:
        print(f"\n{'='*48}\n  PORTAL DEL CLIENTE (RASTREO)\n{'='*48}")
        print("1. Rastrea tu paquete | 2. Salir")
        op = input("\nSelección: ")
        if op=="1": 
            id_busqueda = input("Ingrese su ID de paquete: ")
            buscar_paquete_cliente_o_admin(id_busqueda)
        elif op=="2": break
        else: print("Opción no válida.")

# --- INICIO DEL SISTEMA (LOGIN) ---
def iniciar_sistema():
    while True:
        print(f"\n{'='*48}\n  ACCESO AL SISTEMA LOGÍSTICO\n{'='*48}")
        print("1. Acceder como Administrador")
        print("2. Rastreo de Cliente")
        print("3. Salir")
        rol_opcion = input("Seleccione su rol: ")

        if rol_opcion == "1":
            user = input("Usuario: ")
            passwd = input("Contraseña: ")
            if user == ADMIN_USER and passwd == ADMIN_PASS:
                print("✅ Acceso como Administrador concedido.")
                panel_admin()
            else:
                print("❌ Credenciales de Administrador incorrectas.")
        elif rol_opcion == "2":
            print("✅ Acceso como Cliente concedido.")
            panel_cliente()
        elif rol_opcion == "3":
            print("👋 Cerrando sistema. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

iniciar_sistema()

panel_principal()
