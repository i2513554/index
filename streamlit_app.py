import streamlit as st
from PIL import Image
import datetime
import mysql.connector
from mysql.connector import Error

# Configuración de la página
st.set_page_config(page_title="Sistema de Alquiler de Vehículos SAV", layout="wide")
# Cargar imagen
logo = Image.open("./img/maqui.png")

# columnas de alineación
col1, col2 = st.columns([1, 6])
with col1:
    st.image(logo, width=180)
with col2:
    st.markdown("<h1 style='margin-top: 15px;'>Sistema de Gestión de Alquiler Vehicular</h1>", unsafe_allow_html=True)

# Conexión a MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@M_1793258s#",
            database="alquiler_vehiculos",
            auth_plugin='mysql_native_password'
        )
        return connection
    except Error as e:
        st.error(f"Error al conectar a MySQL: {e}")
        return None

# Funciones para consultas 
def fetch_all(conn, query, params=None):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Error as e:
        st.error(f"Error en consulta: {e}")
        return None

def fetch_one(conn, query, params=None):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()
    except Error as e:
        st.error(f"Error en consulta: {e}")
        return None

def get_sucursales():
    conn = create_connection()
    if conn:
        try:
            return fetch_all(conn, "SELECT * FROM sucursal")
        finally:
            conn.close()
    return []

def get_vehiculos_disponibles():
    conn = create_connection()
    if conn:
        try:
            query = """
            SELECT v.*, s.nombre as nombre_sucursal 
            FROM vehiculo v
            JOIN sucursal s ON v.id_sucursal = s.id_sucursal
            WHERE v.estado = 'disponible'
            """
            return fetch_all(conn, query)
        finally:
            conn.close()
    return []

# Lista de opciones de contenido
menu = st.sidebar.selectbox("Menú Principal", [
    "Registro de Clientes",
    "Gestión de Vehículos",
    "Proceso de Alquiler",
    "Contratos Activos",
    "Mantenimientos"
]
)
with st.sidebar.container():
# información de contacto
    st.markdown("---")
    st.markdown("""
    **Software Tipo :** Gestión de flota vehicular
    **Servidor utilizado :** phpmyadmin\n 
     
    **Plataforma:** web  
    **versión:** 1.0.2
    """)    
    st.markdown("---")
    
    st.markdown("""
    **🧑‍💻 Realizado por:**  
    Miguel   
    **🆔:** 1479258--\n
    **Ciclo:** 1

    """)
    st.markdown("---")



# Módulo de Registro de Clientes
if menu == "Registro de Clientes":
    st.header("📝 Registro de Nuevo Cliente")
    
    with st.form("form_cliente"):
        dni = st.text_input("DNI (8 dígitos)", max_chars=8)
        nombre = st.text_input("Nombres")
        apellido = st.text_input("Apellidos")
        telefono = st.text_input("Teléfono (9 dígitos)", max_chars=9)
        direccion = st.text_input("direcion domiciliaria",max_chars=250)
        
        if st.form_submit_button("Guardar Cliente"):
            if len(dni) != 8:
                st.error("El DNI debe tener 8 dígitos")
            elif len(telefono) != 9:
                st.error("El teléfono debe tener 9 dígitos")
            else:
                conn = create_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        query = """
                        INSERT INTO cliente (dni, nombre, apellido, telefono, direccion)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(query, (dni, nombre, apellido, telefono, direccion))
                        conn.commit()
                        st.success("Cliente registrado exitosamente!")
                    except Error as e:
                        st.error(f"Error al registrar cliente: {e}")
                    finally:
                        conn.close()

# Módulo de Gestión de Vehículos
elif menu == "Gestión de Vehículos":
    st.header("🚙 Vehículos Disponibles")
    
# Obtener sucursales para el filtro
    sucursales = get_sucursales()
    nombres_sucursales = [s['nombre'] for s in sucursales] if sucursales else []
    
# Controles de filtrado y ordenación
    col1, col2 = st.columns(2)
    
    with col1:
        sucursal_filtro = st.selectbox("Filtrar por sucursal", ["Todas"] + nombres_sucursales)
    
    with col2:
        orden_options = {
            "Marca (A-Z)": "marca ASC",
            "Marca (Z-A)": "marca DESC",
            "Precio (↑)": "precio_alquiler ASC",
            "Precio (↓)": "precio_alquiler DESC",
            "Año (↑)": "anio ASC",
            "Año (↓)": "anio DESC"
        }
        orden_seleccionado = st.selectbox("Ordenar por", list(orden_options.keys()))
    
    conn = create_connection()
    if conn:
        try:
            # Construir consulta SQL
            query = """
                SELECT 
                    v.id_vehiculo as "ID",
                    v.placa as "Placa",
                    v.marca as "Marca",
                    v.modelo as "Modelo",
                    v.año as "Año",
                    CONCAT('S/. ', FORMAT(v.precio_dia, 2)) as "Precio Diario",
                    s.nombre as "Sucursal",
                    v.estado as "Estado",
                    v.kilometraje as "Kilometraje"
                FROM vehiculo v 
                JOIN sucursal s ON v.id_sucursal = s.id_sucursal
            """
            params = []
            where_clauses = []
            
            if sucursal_filtro != "Todas":
                where_clauses.append("s.nombre = %s")
                params.append(sucursal_filtro)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += f" ORDER BY {orden_options[orden_seleccionado]}"
            
            vehiculos = fetch_all(conn, query, params if params else None)
            
            if vehiculos:
                # Mostrar tabla con st.data_editor para permitir ordenación
                st.data_editor(
                    vehiculos,
                    column_config={
                        "Precio Diario": st.column_config.TextColumn(
                            "Precio Diario",
                            help="Precio de alquiler por día"
                        ),
                        "Año": st.column_config.NumberColumn(
                            "Año",
                            format="%d"
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    disabled=True  # Hace la tabla de solo lectura
                )
                
                # Mostrar resumen
                st.subheader("📊 Resumen")
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Total Vehículos", len(vehiculos))
                with cols[1]:
                    marcas_unicas = len(set(v['Marca'] for v in vehiculos))
                    st.metric("Marcas Únicas", marcas_unicas)
                with cols[2]:
                    precios = [float(v['Precio Diario'].replace('S/. ', '')) for v in vehiculos]
                    avg_price = sum(precios) / len(precios) if precios else 0
                    st.metric("Precio Promedio", f"S/. {avg_price:.2f}")
                
            else:
                st.warning("No se encontraron vehículos con los filtros seleccionados")
                
        except Error as e:
            st.error(f"Error al obtener vehículos: {e}")
        finally:
            conn.close()
# Módulo de Proceso de Alquiler
elif menu == "Proceso de Alquiler":
    st.header("📄 Nuevo Contrato de Alquiler")
    
    # Paso 1: Buscar cliente
    st.subheader("1. Seleccionar Cliente")
    dni_cliente = st.text_input("Buscar cliente por DNI", max_chars=8)
    cliente_encontrado = None
    
    if dni_cliente and len(dni_cliente) == 8:
        conn = create_connection()
        if conn:
            try:
                query = "SELECT * FROM cliente WHERE dni = %s"
                cliente_encontrado = fetch_one(conn, query, (dni_cliente,))
                if cliente_encontrado:
                    st.success(f"Cliente encontrado: {cliente_encontrado['nombre']} {cliente_encontrado['apellido']}")
                else:
                    st.warning("Cliente no encontrado. Regístrelo primero.")
            except Error as e:
                st.error(f"Error al buscar cliente: {e}")
            finally:
                conn.close()
    
    # Paso 2: Seleccionar vehículo
    st.subheader("2. Seleccionar Vehículo")
    vehiculos_disponibles = get_vehiculos_disponibles()
    
    if vehiculos_disponibles:
        opciones_vehiculos = [f"{v['placa']} - {v['marca']} {v['modelo']}" for v in vehiculos_disponibles]
        vehiculo_seleccionado = st.selectbox("Vehículos disponibles", options=opciones_vehiculos)
        
        # Paso 3: Fechas y detalles
        st.subheader("3. Detalles del Alquiler")
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_inicio = st.date_input("Fecha de inicio", datetime.date.today())
        with col2:
            fecha_fin = st.date_input("Fecha de devolución", datetime.date.today() + datetime.timedelta(days=1))
        with col3:
            deposito_seguro = st.number_input("Depósito de seguridad (S/)", min_value=0.0, value=100.0, step=10.0)## mostrar el valor de la cantidad a depositar como garantia (deposito seguro)
        dias = (fecha_fin - fecha_inicio).days
        if dias > 0:
            # Obtener el vehículo seleccionado
            placa_seleccionada = vehiculo_seleccionado.split(" - ")[0]
            vehiculo = next(v for v in vehiculos_disponibles if v['placa'] == placa_seleccionada)
            
            precio_dia = vehiculo['precio_dia']
            total = dias * precio_dia
            
            st.info(f"Total a pagar por {dias} días: S/. {total:.2f}")
        
        # Confirmación
        if st.button("Generar Contrato") and cliente_encontrado:
            if fecha_fin <= fecha_inicio:
                st.error("La fecha de devolución debe ser posterior a la de inicio")
            else:
                conn = create_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        
                        # Registrar contrato
                        query_contrato = """
                        INSERT INTO contrato (
                            id_cliente, id_vehiculo, id_empleado, id_sucursal,
                            fecha_inicio, fecha_fin, precio_total, estado, deposito_seguro
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        valores = (
                            int(cliente_encontrado['id_cliente']),
                            int(vehiculo['id_vehiculo']),
                            1,  # ID de empleado simulado
                            int(vehiculo['id_sucursal']),
                            fecha_inicio,
                            fecha_fin,
                            float(total),
                            "activo",
                            float(deposito_seguro)
                        )
                        cursor.execute(query_contrato, valores)
                        
                        # Actualizar estado del vehículo
                        cursor.execute(
                            "UPDATE vehiculo SET estado = 'alquilado' WHERE id_vehiculo = %s",
                            (vehiculo['id_vehiculo'],)
                        )
                        
                        conn.commit()
                        st.success("Contrato generado exitosamente!")
                    except Error as e:
                        conn.rollback()
                        st.error(f"Error al generar contrato: {e}")
                    finally:
                        conn.close()

# Módulo de Contratos Activos
elif menu == "Contratos Activos":
    st.subheader("  Resumen de Deudas")
    conn = create_connection()
    if conn:
        try:
            # Campo para ingresar DNI
            dni_cliente = st.text_input("Ingrese el DNI del cliente:")
            
            if dni_cliente:  # Solo proceder si se ingresó un DNI
                # Consulta para obtener contratos activos del cliente con ese DNI
                query = """
                    SELECT c.precio_total
                    FROM contrato c
                    JOIN cliente cl ON c.id_cliente = cl.id_cliente
                    WHERE cl.dni = %s AND c.estado = 'activo'
                """
                params = (dni_cliente,)
                
                contratos_activos = fetch_all(conn, query, params)
                
                if contratos_activos:
                    # Calcular suma total de la deuda
                    total_deuda = sum(contrato['precio_total'] for contrato in contratos_activos)
                    st.success(f"Deuda total activa para DNI {dni_cliente}: S/. {total_deuda:.2f}")
                else:
                    st.warning(f"No se encontraron contratos activos para el DNI {dni_cliente}")
            
            #tabla de contratos activos
            query_contratos = """
                SELECT c.id_contrato, cl.dni, cl.nombre, v.placa, 
                       c.fecha_inicio, c.fecha_fin, c.precio_total, c.estado
                FROM contrato c
                JOIN cliente cl ON c.id_cliente = cl.id_cliente
                JOIN vehiculo v ON c.id_vehiculo = v.id_vehiculo
                WHERE c.estado = 'activo'
            """
            todos_contratos = fetch_all(conn, query_contratos)
            
            if todos_contratos:
                st.subheader("📋 Todos los contratos activos")
                st.dataframe(todos_contratos)
            else:
                st.info("No hay contratos activos actualmente")
                
        except Error as e:
            st.error(f"Error en la consulta: {e}")
        finally:
            conn.close()

# dar por finalizado el contrato de alquiler
    st.header("Finalizar contrato")
    conn = create_connection()
    if conn:
        try:
            query = """
                SELECT c.id_contrato, cl.nombre as cliente, v.placa, v.marca, v.modelo,
                       c.fecha_inicio, c.fecha_fin, c.precio_total
                FROM contrato c
                JOIN cliente cl ON c.id_cliente = cl.id_cliente
                JOIN vehiculo v ON c.id_vehiculo = v.id_vehiculo
                WHERE c.estado = 'activo'
            """
            contratos_activos = fetch_all(conn, query)
            
            if contratos_activos:
                
                # Finalizar contrato
                opciones_contratos = [f"{c['id_contrato']} - {c['cliente']} - {c['placa']}" for c in contratos_activos]
                contrato_seleccionado = st.selectbox(
                    "Seleccionar contrato para finalizar",
                    options=opciones_contratos
                )

                if st.button("Finalizar Contrato"):
                    id_contrato = int(contrato_seleccionado.split(" - ")[0])
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("SELECT id_vehiculo FROM contrato WHERE id_contrato = %s", (id_contrato,))
                        id_vehiculo = cursor.fetchone()[0]
                        
                        cursor.execute("UPDATE contrato SET estado = 'finalizado' WHERE id_contrato = %s", (id_contrato,))
                        cursor.execute("UPDATE vehiculo SET estado = 'disponible' WHERE id_vehiculo = %s", (id_vehiculo,))
                        
                        conn.commit()
                        st.success("Contrato finalizado y vehículo liberado")
                        st.rerun()
                    except Error as e:
                        conn.rollback()
                        st.error(f"Error al finalizar contrato: {e}")
            else:
                st.info("No hay contratos activos actualmente")
                
        except Error as e:
            st.error(f"Error al obtener contratos: {e}")
        finally:
            conn.close()
     
# Módulo de Mantenimientos
elif menu == "Mantenimientos": 
    st.header("🔧 Gestión de Mantenimientos")
    
    tab1, tab2 = st.tabs(["Registrar Mantenimiento", "Historial"])
    
    with tab1:
        with st.form("form_mantenimiento"):
            vehiculos_mtto = get_vehiculos_disponibles()
            if vehiculos_mtto:
                opciones_vehiculos = [f"{v['placa']} - {v['marca']} {v['modelo']}" for v in vehiculos_mtto]
                vehiculo_mtto = st.selectbox("Vehículo", options=opciones_vehiculos)
                
                col1, col2 = st.columns(2)
                with col1:
                    tipo_mtto = st.selectbox("Tipo", ["Preventivo", "Correctivo", "Reparación"])
                    fecha_inicio = st.date_input("Fecha inicio", datetime.date.today())
                with col2:
                    costo = st.number_input("Costo (S/.)", min_value=0.0, step=50.0)
                    fecha_fin = st.date_input("Fecha fin estimada", datetime.date.today() + datetime.timedelta(days=1))
                
                observaciones = st.text_area("Observaciones")
                
                if st.form_submit_button("Registrar Mantenimiento"):
                    placa_seleccionada = vehiculo_mtto.split(" - ")[0]
                    vehiculo = next(v for v in vehiculos_mtto if v['placa'] == placa_seleccionada)
                    id_vehiculo = vehiculo['id_vehiculo']
                    
                    conn = create_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            
                            query_mtto = """
                            INSERT INTO mantenimiento (
                                id_vehiculo, tipo, fecha_inicio, fecha_fin, costo,
                                id_empleado, estado_disponible, observaciones
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(query_mtto, (
                                id_vehiculo, tipo_mtto.lower(), fecha_inicio, fecha_fin, costo,
                                1, False, observaciones
                            ))
                            
                            cursor.execute(
                                "UPDATE vehiculo SET estado = 'mantenimiento' WHERE id_vehiculo = %s",
                                (id_vehiculo,)
                            )
                            
                            conn.commit()
                            st.success("Mantenimiento registrado. Vehículo no disponible para alquiler.")
                            st.rerun()
                            
                        except Error as e:
                            conn.rollback()
                            st.error(f"Error al registrar mantenimiento: {e}")
                        finally:
                            conn.close()
    
    with tab2:
        st.subheader("Historial de Mantenimientos")
        
        col1, col2 = st.columns(2)
        with col1:
            placa_filtro = st.text_input("Buscar por placa:", placeholder="Ej: ABC123")
        with col2:
            orden_options = {
                "Fecha reciente": "m.fecha_inicio DESC",
                "Fecha antigua": "m.fecha_inicio ASC",
                "Costo alto": "m.costo DESC",
                "Costo bajo": "m.costo ASC",
                "Tipo de mantenimiento": "m.tipo ASC"
            }
            orden_seleccionado = st.selectbox("Ordenar por:", list(orden_options.keys()))
        
        conn = create_connection()
        if conn:
            try:
                query = """
                SELECT 
                    m.id_mantenimiento as "ID",
                    v.placa as "Placa",
                    v.marca as "Marca",
                    v.modelo as "Modelo",
                    m.tipo as "Tipo",
                    DATE_FORMAT(m.fecha_inicio, '%Y-%m-%d') as "Fecha Inicio",
                    DATE_FORMAT(m.fecha_fin, '%Y-%m-%d') as "Fecha Fin",
                    CONCAT('S/. ', FORMAT(m.costo, 2)) as "Costo",
                    e.nombre as "Técnico",
                    IFNULL(m.observaciones, 'Sin observaciones') as "Detalles"
                FROM mantenimiento m
                JOIN vehiculo v ON m.id_vehiculo = v.id_vehiculo
                JOIN empleado e ON m.id_empleado = e.id_empleado
                """
                params = []
                if placa_filtro:
                    query += " WHERE v.placa LIKE %s"
                    params.append(f"%{placa_filtro}%")
                
                query += f" ORDER BY {orden_options[orden_seleccionado]}"
                
                historial = fetch_all(conn, query, params if params else None)
                
                if historial:
                    st.dataframe(
                        historial,
                        column_config={
#                            "Costo": st.column_config.NumberColumn(format="S/. %s"),
                    "Costo_Formateado": st.column_config.TextColumn("Costo"),
                            "Detalles": st.column_config.TextColumn(width="large")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    if placa_filtro:
                        costo_total = sum(float(h['Costo'].replace('S/. ', '')) for h in historial)
                        st.metric(f"Total gastado en mantenimientos", f"S/. {costo_total:,.2f}")
                else:
                    st.warning("No se encontraron mantenimientos con los filtros seleccionados")
                    
            except Error as e:
                st.error(f"Error al obtener historial: {e}")
            finally:
                conn.close()

