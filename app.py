import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="Portafolio de Incentivos", page_icon="📊", layout="wide")

# --- CONTROL DE ACCESO (LOGIN) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None

if not st.session_state.autenticado:
    st.title("🔒 Sistema de Incentivos")
    st.write("Por favor, inicia sesión para continuar.")
    
    usuario = st.selectbox("Perfil", ["Seleccionar...", "Moderador", "Líder de Proyecto"])
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # CONTRASEÑAS CONFIGURADAS AQUÍ:
        if usuario == "Moderador" and password == "admin123":
            st.session_state.autenticado = True
            st.session_state.rol = "Moderador"
            st.rerun()
        elif usuario == "Líder de Proyecto" and password == "user123":
            st.session_state.autenticado = True
            st.session_state.rol = "Usuario"
            st.rerun()
        else:
            st.error("Contraseña incorrecta o perfil no válido.")
    st.stop() # Detiene la ejecución si no está logueado

# --- BARRA LATERAL ---
st.sidebar.title("Bienvenido")
st.sidebar.info(f"👤 Rol actual: **{st.session_state.rol}**")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.rerun()

st.sidebar.divider()

# --- BASE DE DATOS ---
def obtener_conexion():
    conn = sqlite3.connect("portafolio_incentivos.db", check_same_thread=False)
    return conn

def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, nombre TEXT NOT NULL, atencion TEXT, area_negocio TEXT,
            tipo_proyecto TEXT, subtipo TEXT, puestos_impactar TEXT, inicio_planificado TEXT, fin_planificado TEXT,
            nacional_incentivos TEXT, gerente_incentivos TEXT, lider_asignado TEXT, origen_presupuesto TEXT,
            etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, carpeta_url TEXT,
            plan_url TEXT, ultima_actualizacion TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_db()

# --- CONSTANTES ---
OPCIONES_ESTATUS = ["En tiempo", "Retrasado", "Detenido", "Cancelado", "Por iniciar"]
es_moderador = st.session_state.rol == "Moderador"

# --- INTERFAZ PRINCIPAL ---
st.title("📊 Portafolio de Proyectos de Incentivos")

conn = obtener_conexion()
df = pd.read_sql_query("SELECT * FROM proyectos", conn)

# 1. FUNCIÓN PARA DESCARGAR PDF (Solo Moderador)
if es_moderador and not df.empty:
    def generar_pdf(dataframe):
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Reporte de Portafolio de Proyectos - Incentivos", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10)
        # Encabezados de tabla
        pdf.cell(30, 10, "Folio", 1)
        pdf.cell(80, 10, "Nombre", 1)
        pdf.cell(40, 10, "Lider", 1)
        pdf.cell(30, 10, "Estatus", 1)
        pdf.cell(20, 10, "Avance", 1)
        pdf.cell(50, 10, "Ult. Act.", 1)
        pdf.ln()
        
        pdf.set_font("Arial", '', 9)
        for _, row in dataframe.iterrows():
            pdf.cell(30, 10, str(row['folio'])[:15], 1)
            pdf.cell(80, 10, str(row['nombre'])[:40], 1)
            pdf.cell(40, 10, str(row['lider_asignado'])[:20], 1)
            pdf.cell(30, 10, str(row['estatus_tiempo']), 1)
            pdf.cell(20, 10, f"{int((row['avance_real'] or 0)*100)}%", 1)
            pdf.cell(50, 10, str(row['ultima_actualizacion'])[:16], 1)
            pdf.ln()
            
        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            return tmp.name

    st.sidebar.markdown("### 📄 Exportar")
    pdf_path = generar_pdf(df)
    with open(pdf_path, "rb") as file:
        st.sidebar.download_button(
            label="⬇️ Descargar Reporte PDF",
            data=file,
            file_name=f"Reporte_Incentivos_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
        )

# 2. CREACIÓN DE PROYECTOS (Solo Moderador)
if es_moderador:
    with st.expander("➕ Crear Nuevo Proyecto", expanded=False):
        with st.form("form_nuevo"):
            c1, c2, c3 = st.columns(3)
            folio = c1.text_input("Folio (ej. INC-001)")
            nombre = c2.text_input("Nombre del Proyecto *")
            lider = c3.text_input("Líder Asignado")
            
            if st.form_submit_button("Guardar Proyecto"):
                if nombre.strip():
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO proyectos (folio, nombre, lider_asignado, estatus_tiempo, avance_real) VALUES (?, ?, ?, 'Por iniciar', 0)", (folio, nombre, lider))
                    conn.commit()
                    st.success("Creado correctamente")
                    st.rerun()

# 3. LISTADO Y ACTUALIZACIÓN SEMANAL
st.subheader("📋 Actualización de Avances Semanales")

if not df.empty:
    for _, row in df.iterrows():
        p_id = row["id"]
        color = "🟢" if row["estatus_tiempo"] == "En tiempo" else ("🔴" if row["estatus_tiempo"] == "Retrasado" else "🟡")
        
        with st.expander(f"{color} {row['folio'] or 'S/F'} - {row['nombre']} | Líder: {row['lider_asignado']} | Avance: {int((row['avance_real'] or 0)*100)}%"):
            
            # --- FORMULARIO DE ACTUALIZACIÓN SEMANAL (Para ambos roles) ---
            st.caption("Campos de actualización periódica:")
            with st.form(f"update_{p_id}"):
                col1, col2 = st.columns(2)
                
                # Los 6 campos solicitados
                u_estatus = col1.selectbox("Estatus de tiempo", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0)
                u_avance = col2.slider("% Avance real", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
                
                u_resumen = st.text_area("Resumen estatus / Bitácora", row["resumen_estatus"] or "")
                
                u_carpeta = st.text_input("Carpeta de proyecto (URL Drive)", row["carpeta_url"] or "")
                u_plan = st.text_input("Plan de trabajo (URL Sheets)", row["plan_url"] or "")
                
                st.info(f"🕒 Última actualización registrada: {row['ultima_actualizacion'] or 'Nunca'}")
                
                if st.form_submit_button("💾 Guardar Cambios"):
                    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE proyectos SET 
                        estatus_tiempo=?, avance_real=?, resumen_estatus=?, 
                        carpeta_url=?, plan_url=?, ultima_actualizacion=? 
                        WHERE id=?
                    """, (u_estatus, u_avance, u_resumen, u_carpeta, u_plan, ahora, p_id))
                    conn.commit()
                    st.success("¡Información actualizada!")
                    st.rerun()
            
            # --- BORRADO (Solo Moderador) ---
            if es_moderador:
                if st.button("🗑️ Eliminar proyecto", key=f"del_{p_id}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM proyectos WHERE id=?", (p_id,))
                    conn.commit()
                    st.rerun()

conn.close()
