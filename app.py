import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="Portafolio de Incentivos", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; border-left: 5px solid #0056b3; padding: 15px; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stExpander header { background-color: #f1f3f5; font-weight: bold; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE LA BASE DE DATOS (NUEVA DB LIMPIA) ---
def obtener_conexion():
    # Cambiamos el nombre del archivo para forzar una base de datos limpia
    return sqlite3.connect("bd_incentivos.db", check_same_thread=False)

def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Tabla de Proyectos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, nombre TEXT NOT NULL,
            lider_asignado TEXT, estatus_tiempo TEXT, avance_real REAL,
            resumen_estatus TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT
        )
    """)
    
    # Tabla de Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, correo TEXT
        )
    """)
    
    # Crear usuarios reales por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (usuario, password, rol, correo) VALUES ('leonardo.castillo', 'Coppel2026', 'Moderador', 'leonardo.castillo@coppel.com')")
        cursor.execute("INSERT INTO usuarios (usuario, password, rol, correo) VALUES ('ivan.salazar', 'Coppel2026', 'Usuario', 'ivan.salazar@coppel.com')")
        
    conn.commit()
    conn.close()

inicializar_db()

# --- CONTROL DE ACCESO (LOGIN) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.session_state.rol = None

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #0056b3;'>💼 Portafolio de Incentivos</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Portal de seguimiento y gestión de proyectos</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("🔒 Inicio de Sesión")
            usuario_input = st.text_input("Usuario (ej. leonardo.castillo)")
            password_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if submit:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute("SELECT password, rol FROM usuarios WHERE usuario=?", (usuario_input,))
                user_data = cursor.fetchone()
                conn.close()
                
                if user_data and user_data[0] == password_input:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_input
                    st.session_state.rol = user_data[1]
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# --- BARRA LATERAL (CON CAMBIO DE CONTRASEÑA) ---
es_moderador = st.session_state.rol == "Moderador"
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Mi Panel")
    st.write(f"Hola, **{st.session_state.usuario_actual}**")
    st.caption(f"Rol: {st.session_state.rol}")
    st.divider()

    # Módulo para cambiar contraseña
    with st.expander("🔑 Cambiar mi contraseña", expanded=False):
        with st.form("form_cambio_pass"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar_pass = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("Actualizar"):
                if nueva_pass and nueva_pass == confirmar_pass:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET password=? WHERE usuario=?", (nueva_pass, st.session_state.usuario_actual))
                    conn.commit()
                    conn.close()
                    st.success("¡Contraseña actualizada!")
                else:
                    st.error("Las contraseñas no coinciden.")
    
    # Módulo para agregar usuarios (Solo Moderador)
    if es_moderador:
        with st.expander("👥 Crear nuevo usuario", expanded=False):
            with st.form("form_nuevo_usuario"):
                n_user = st.text_input("Nombre de Usuario (Login)")
                n_pass = st.text_input("Contraseña Temporal", type="password")
                n_rol = st.selectbox("Rol", ["Usuario", "Moderador"])
                
                if st.form_submit_button("Crear Usuario"):
                    if n_user and n_pass:
                        try:
                            conn = obtener_conexion()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO usuarios (usuario, password, rol, correo) VALUES (?, ?, ?, ?)", (n_user, n_pass, n_rol, ""))
                            conn.commit()
                            conn.close()
                            st.success("Usuario creado.")
                        except:
                            st.error("El usuario ya existe.")
                    else:
                        st.warning("Completa los datos.")

    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.session_state.rol = None
        st.rerun()

# --- CONSULTA PRINCIPAL DE PROYECTOS ---
conn = obtener_conexion()
df = pd.read_sql_query("SELECT * FROM proyectos", conn)

# --- CABECERA PRINCIPAL ---
st.markdown("<h2 style='color: #2c3e50;'>Dashboard de Proyectos</h2>", unsafe_allow_html=True)

# --- MÉTRICAS VISUALES SUPERIORES ---
if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    total = len(df)
    en_tiempo = len(df[df['estatus_tiempo'] == 'En tiempo'])
    retrasados = len(df[df['estatus_tiempo'] == 'Retrasado'])
    promedio_avance = df['avance_real'].mean() * 100 if total > 0 else 0

    m1.markdown(f"<div class='metric-card'><h4>📊 Total Proyectos</h4><h2>{total}</h2></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card' style='border-left-color: #28a745;'><h4>🟢 En Tiempo</h4><h2>{en_tiempo}</h2></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card' style='border-left-color: #dc3545;'><h4>🔴 Retrasados</h4><h2>{retrasados}</h2></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card' style='border-left-color: #17a2b8;'><h4>📈 Avance Global</h4><h2>{promedio_avance:.1f}%</h2></div>", unsafe_allow_html=True)
    st.write("")

# --- FUNCIÓN GENERAR PDF (Solo Moderador) ---
if es_moderador and not df.empty:
    def generar_pdf(dataframe):
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(0, 86, 179)
        pdf.cell(0, 10, "Reporte Ejecutivo de Portafolio", ln=True, align="C")
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(30, 10, "Folio", 1, 0, 'C', True)
        pdf.cell(90, 10, "Nombre del Proyecto", 1, 0, 'C', True)
        pdf.cell(50, 10, "Líder Asignado", 1, 0, 'C', True)
        pdf.cell(30, 10, "Estatus", 1, 0, 'C', True)
        pdf.cell(20, 10, "Avance", 1, 0, 'C', True)
        pdf.cell(50, 10, "Ult. Act.", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 9)
        for _, row in dataframe.iterrows():
            pdf.cell(30, 10, str(row['folio'])[:15], 1)
            pdf.cell(90, 10, str(row['nombre'])[:50], 1)
            pdf.cell(50, 10, str(row['lider_asignado'])[:25], 1)
            pdf.cell(30, 10, str(row['estatus_tiempo']), 1, 0, 'C')
            pdf.cell(20, 10, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, 'C')
            pdf.cell(50, 10, str(row['ultima_actualizacion'])[:16], 1, 1, 'C')
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            return tmp.name

    st.sidebar.markdown("### 📄 Reportes")
    pdf_path = generar_pdf(df)
    with open(pdf_path, "rb") as file:
        st.sidebar.download_button(
            label="⬇️ Descargar Reporte (PDF)", data=file, file_name=f"Reporte_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True
        )

# --- CREACIÓN DE PROYECTOS (Solo Moderador) ---
st.divider()
st.markdown("### 📋 Gestión de Proyectos")

if es_moderador:
    with st.expander("✨ Registrar Nuevo Proyecto", expanded=False):
        with st.form("form_nuevo", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            folio = c1.text_input("Folio (Opcional)")
            nombre = c2.text_input("Nombre del Proyecto *")
            lider = c3.text_input("Líder Asignado")
            
            if st.form_submit_button("Guardar en Portafolio", type="primary"):
                if nombre.strip():
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO proyectos (folio, nombre, lider_asignado, estatus_tiempo, avance_real) VALUES (?, ?, ?, 'Por iniciar', 0)", (folio, nombre, lider))
                    conn.commit()
                    st.success("✅ Proyecto creado exitosamente.")
                    st.rerun()
                else:
                    st.error("El nombre del proyecto es obligatorio.")

# --- LISTADO Y ACTUALIZACIÓN SEMANAL ---
if not df.empty:
    OPCIONES_ESTATUS = ["En tiempo", "Retrasado", "Detenido", "Cancelado", "Por iniciar"]
    for _, row in df.iterrows():
        p_id = row["id"]
        if row["estatus_tiempo"] == "En tiempo": icon = "🟢"
        elif row["estatus_tiempo"] == "Retrasado": icon = "🔴"
        elif row["estatus_tiempo"] == "Detenido": icon = "🟡"
        else: icon = "⚪"
        
        with st.expander(f"{icon} {row['folio'] or 'S/F'} | {row['nombre']} — Avance: {int((row['avance_real'] or 0)*100)}%"):
            with st.form(f"update_{p_id}"):
                st.markdown(f"**Líder:** {row['lider_asignado']} | **Última actualización:** {row['ultima_actualizacion'] or 'Sin registro'}")
                st.divider()
                
                col1, col2 = st.columns([1, 1])
                u_estatus = col1.selectbox("Estatus del Proyecto", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0)
                u_avance = col2.slider("Progreso (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05, format="%.2f")
                u_resumen = st.text_area("Resumen de Estatus / Comentarios", row["resumen_estatus"] or "", height=100)
                c_links1, c_links2 = st.columns(2)
                u_carpeta = c_links1.text_input("📁 Carpeta (URL Drive)", row["carpeta_url"] or "")
                u_plan = c_links2.text_input("📅 Plan de Trabajo (URL)", row["plan_url"] or "")
                
                c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 6])
                if c_btn1.form_submit_button("💾 Guardar", type="primary"):
                    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE proyectos SET estatus_tiempo=?, avance_real=?, resumen_estatus=?, carpeta_url=?, plan_url=?, ultima_actualizacion=? WHERE id=?", (u_estatus, u_avance, u_resumen, u_carpeta, u_plan, ahora, p_id))
                    conn.commit()
                    st.success("Actualizado")
                    st.rerun()
                
                if es_moderador:
                    if c_btn2.form_submit_button("🗑️ Eliminar"):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM proyectos WHERE id=?", (p_id,))
                        conn.commit()
                        st.rerun()

conn.close()
