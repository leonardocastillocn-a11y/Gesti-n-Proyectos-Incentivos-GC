import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="Portafolio de Incentivos", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS PROFESIONALES (UX Mejorada) ---
st.markdown("""
    <style>
    /* Fondo principal sutil */
    .stApp { background-color: #f4f6f9; }
    
    /* Tarjetas de métricas superiores */
    .metric-card { 
        background-color: white; border-radius: 12px; padding: 20px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border-top: 5px solid #0052cc; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-title { color: #6b7280; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;}
    .metric-value { color: #111827; font-size: 2.2rem; font-weight: 700; margin:0;}
    
    /* Estilos para el texto de login */
    .login-title { text-align: center; color: #0052cc; font-size: 2.5rem; font-weight: 800; margin-bottom: 0;}
    .login-sub { text-align: center; color: #6b7280; font-size: 1.1rem; margin-top: 5px; margin-bottom: 30px;}
    
    /* Badges / Píldoras para los estados */
    .badge { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; display: inline-block;}
    .bg-green { background-color: #d1fae5; color: #065f46; }
    .bg-red { background-color: #fee2e2; color: #991b1b; }
    .bg-yellow { background-color: #fef3c7; color: #92400e; }
    .bg-gray { background-color: #f3f4f6; color: #374151; }
    .bg-blue { background-color: #dbeafe; color: #1e40af; }
    
    /* Expanders limpios estilo tarjeta */
    .streamlit-expanderHeader { background-color: white !important; border-radius: 8px !important; border: none !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .streamlit-expanderContent { border: none !important; padding-top: 15px !important;}
    
    /* Inputs y botones redondeados */
    .stTextInput > div > div > input, .stSelectbox > div > div > select { border-radius: 8px !important; }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
OPCIONES_AREAS = ["Incentivos", "Afore", "Banca Empresarial", "Banco", "CAT Cobranza", "CAT P&V", "CEDIS", "Cobranza Domiciliaria", "Credito Automotriz", "Inmobiliaria", "Retail", "Sale Vale"]
OPCIONES_TIPOS = ["Esquema de Incentivos", "Tecnología", "Estratégicos", "Procesos", "Campañas", "Auditorías"]
OPCIONES_SUBTIPOS = ["EI-Nuevo incentivo completo", "EI-Actualización completa de incentivo", "EI-Ajuste menor de incentivo", "EI-Ajuste mayor de incentivo", "EI-Casos especiales", "CA-Campaña", "CA-Concurso", "PR-Documentación oficial", "PR-Nuevo proceso", "TE-Software", "TE-Tableros", "Otros"]
OPCIONES_ETAPAS = ["1. Diseño (EI)", "2. Prueba piloto (EI)", "3. Escalamiento nacional (EI)", "4. Cierre (EI)", "1. Diseño (CA)", "2. Implementación (CA)", "3. Evaluación y cierre (CA)", "4. Cierre (CA)", "1. Planeación", "2. Ejecución", "3. Cierre"]
OPCIONES_ESTATUS = ["En tiempo", "Retrasado", "Detenido", "Cancelado", "Por iniciar"]
OPCIONES_GERENTES = ["Andres Avila", "Eduardo Rodriguez", "Heriberto Vega", "Janik Orozco", "Kurokusi Ochoa", "Noel Aquino", "Yahir Ramirez", "Giovanni Vallejo", "Ruben Rivera"]

# --- BASE DE DATOS ---
def obtener_conexion(): return sqlite3.connect("db_coppel_v3.db", check_same_thread=False)

def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, nombre TEXT NOT NULL,
            area_negocio TEXT, tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT, 
            etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, 
            carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)
    """)
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (correo, password, rol, nombre) VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')")
        cursor.execute("INSERT INTO usuarios (correo, password, rol, nombre) VALUES ('ivan.salazar@coppel.com', 'Coppel2026', 'Usuario', 'Oscar Ivan Salazar')")
    conn.commit()
    conn.close()

inicializar_db()

# --- CONTROL DE ACCESO (LOGIN) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p class='login-title'>💼 Portafolio Incentivos</p>", unsafe_allow_html=True)
        st.markdown("<p class='login-sub'>Centro de Excelencia Nacional</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 👋 Iniciar Sesión")
            correo_input = st.text_input("Correo Corporativo", placeholder="nombre.apellido@coppel.com")
            password_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar de forma segura", type="primary", use_container_width=True)
            
            if submit:
                if correo_input.strip() == "":
                    st.warning("Ingresa tu correo.")
                else:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=?", (correo_input.strip().lower(),))
                    user_data = cursor.fetchone()
                    conn.close()
                    
                    if user_data and user_data[0] == password_input:
                        st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower()
                        st.session_state.rol = user_data[1]; st.session_state.nombre_actual = user_data[2]
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
    st.stop()

# --- BARRA LATERAL ---
es_moderador = st.session_state.rol == "Moderador"
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.nombre_actual}**")
    st.caption(f"{st.session_state.correo_actual} | 🔑 {st.session_state.rol}")
    st.divider()

    with st.expander("🔐 Seguridad", expanded=False):
        with st.form("form_cambio_pass"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar_pass = st.text_input("Confirmar", type="password")
            if st.form_submit_button("Actualizar"):
                if nueva_pass == confirmar_pass and nueva_pass:
                    conn = obtener_conexion(); cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET password=? WHERE correo=?", (nueva_pass, st.session_state.correo_actual))
                    conn.commit(); conn.close(); st.success("Actualizada!")
                else: st.error("No coinciden.")
    
    if es_moderador:
        with st.expander("👥 Gestión de Usuarios", expanded=False):
            with st.form("form_nuevo_usuario"):
                n_nombre = st.text_input("Nombre Completo")
                n_correo = st.text_input("Correo")
                n_pass = st.text_input("Clave Temporal", type="password")
                n_rol = st.selectbox("Rol", ["Usuario", "Moderador"])
                if st.form_submit_button("Dar de alta"):
                    if n_correo and n_pass and n_nombre:
                        try:
                            conn = obtener_conexion(); cursor = conn.cursor()
                            cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", (n_correo.strip().lower(), n_pass, n_rol, n_nombre))
                            conn.commit(); conn.close(); st.success("Creado.")
                        except: st.error("Ya existe.")
    st.divider()
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False; st.rerun()

# --- DATOS PRINCIPALES ---
conn = obtener_conexion()
df = pd.read_sql_query("SELECT * FROM proyectos", conn)

# --- CABECERA Y MÉTRICAS (UI MEJORADA) ---
st.markdown("<h2 style='color: #111827; margin-bottom: 25px;'>📈 Visión General del Portafolio</h2>", unsafe_allow_html=True)

if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    total = len(df); en_tiempo = len(df[df['estatus_tiempo'] == 'En tiempo'])
    retrasados = len(df[df['estatus_tiempo'] == 'Retrasado']); prom_avance = df['avance_real'].mean() * 100
    
    m1.markdown(f"<div class='metric-card' style='border-top-color: #0052cc;'><p class='metric-title'>Total Proyectos</p><p class='metric-value'>{total}</p></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card' style='border-top-color: #10b981;'><p class='metric-title'>En Tiempo</p><p class='metric-value'>{en_tiempo}</p></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card' style='border-top-color: #ef4444;'><p class='metric-title'>Retrasados / Riesgo</p><p class='metric-value'>{retrasados}</p></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card' style='border-top-color: #8b5cf6;'><p class='metric-title'>Avance Global</p><p class='metric-value'>{prom_avance:.1f}%</p></div>", unsafe_allow_html=True)
    st.write("")

# --- PDF GENERATOR ---
if es_moderador and not df.empty:
    def generar_pdf(dataframe):
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18); pdf.set_text_color(0, 82, 204)
        pdf.cell(0, 10, "Reporte de Estatus de Portafolio", ln=True, align="C")
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"Corte al: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C"); pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 8); pdf.set_fill_color(245, 247, 250); pdf.set_text_color(50, 50, 50)
        pdf.cell(20, 10, "Folio", 1, 0, 'C', True); pdf.cell(65, 10, "Proyecto", 1, 0, 'C', True)
        pdf.cell(45, 10, "Lider", 1, 0, 'C', True); pdf.cell(25, 10, "Estatus", 1, 0, 'C', True)
        pdf.cell(15, 10, "Avance", 1, 0, 'C', True); pdf.cell(45, 10, "Etapa", 1, 0, 'C', True); pdf.cell(30, 10, "Act.", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 8); pdf.set_text_color(0, 0, 0)
        for _, row in dataframe.iterrows():
            pdf.cell(20, 10, str(row['folio'])[:10], 1); pdf.cell(65, 10, str(row['nombre'])[:38], 1)
            pdf.cell(45, 10, str(row['lider_asignado'])[:25], 1); pdf.cell(25, 10, str(row['estatus_tiempo']), 1, 0, 'C')
            pdf.cell(15, 10, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, 'C'); pdf.cell(45, 10, str(row['etapa_actual'])[:25], 1, 0, 'C'); pdf.cell(30, 10, str(row['ultima_actualizacion'])[:10], 1, 1, 'C')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp: pdf.output(tmp.name); return tmp.name

    st.sidebar.markdown("### 📄 Descargas")
    pdf_path = generar_pdf(df)
    with open(pdf_path, "rb") as file: st.sidebar.download_button("⬇️ Exportar Portafolio (PDF)", data=file, file_name="Portafolio.pdf", use_container_width=True)

# --- PESTAÑAS (TABS) PARA ORGANIZAR LA VISTA ---
tab1, tab2 = st.tabs(["📋 Seguimiento de Proyectos Activos", "➕ Alta de Nuevo Proyecto"])

with tab1:
    if df.empty:
        st.info("No hay proyectos en el portafolio. Ve a la pestaña 'Alta de Nuevo Proyecto'.")
    else:
        st.caption("Despliega cada tarjeta para actualizar los avances de la semana.")
        for _, row in df.iterrows():
            p_id = row["id"]
            
            # Badges visuales
            if row["estatus_tiempo"] == "En tiempo": css_class = "bg-green"
            elif row["estatus_tiempo"] == "Retrasado": css_class = "bg-red"
            elif row["estatus_tiempo"] == "Detenido": css_class = "bg-yellow"
            else: css_class = "bg-gray"
            
            # Header de la tarjeta con layout HTML
            header_html = f"""
                <div style="display: flex; justify_content: space-between; align-items: center; width: 100%;">
                    <div style="flex-grow: 1;">
                        <span style="color: #6b7280; font-size: 0.8rem; margin-right: 10px;">{row['folio'] or 'S/F'}</span>
                        <span style="font-weight: 700; color: #111827; font-size: 1.1rem;">{row['nombre']}</span>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <span class="badge bg-blue">{row['area_negocio']}</span>
                        <span class="badge {css_class}">{row['estatus_tiempo']}</span>
                    </div>
                </div>
            """
            
            with st.expander(f"📁 {row['folio'] or 'S/F'} - {row['nombre']}"):
                # Barra de progreso visual nativa de Streamlit
                avance_int = int((row['avance_real'] or 0)*100)
                st.progress(float(row['avance_real'] or 0.0), text=f"Progreso actual: {avance_int}%")
                
                with st.form(f"update_{p_id}"):
                    c_info1, c_info2 = st.columns(2)
                    c_info1.markdown(f"<p style='color:#6b7280; margin:0;'>Líder: <b>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
                    c_info2.markdown(f"<p style='color:#6b7280; margin:0; text-align:right;'>Última mod: <b>{row['ultima_actualizacion'] or 'Nunca'}</b></p>", unsafe_allow_html=True)
                    st.divider()
                    
                    col1, col2, col3 = st.columns(3)
                    u_etapa = col1.selectbox("Etapa Actual", OPCIONES_ETAPAS, index=OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0)
                    u_estatus = col2.selectbox("Estatus de Ejecución", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0)
                    u_avance = col3.slider("Porcentaje Completado", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05, format="%.2f")
                    
                    u_resumen = st.text_area("Bitácora y Comentarios Relevantes", row["resumen_estatus"] or "", height=80)
                    
                    c_links1, c_links2 = st.columns(2)
                    u_carpeta = c_links1.text_input("Enlace Google Drive", row["carpeta_url"] or "", placeholder="https://drive.google.com/...")
                    u_plan = c_links2.text_input("Enlace Plan de Trabajo", row["plan_url"] or "", placeholder="https://docs.google.com/spreadsheets/...")
                    
                    c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 6])
                    if c_btn1.form_submit_button("Guardar Cambios", type="primary"):
                        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE proyectos SET etapa_actual=?, estatus_tiempo=?, avance_real=?, resumen_estatus=?, carpeta_url=?, plan_url=?, ultima_actualizacion=? WHERE id=?
                        """, (u_etapa, u_estatus, u_avance, u_resumen, u_carpeta, u_plan, ahora, p_id))
                        conn.commit(); st.rerun()
                    
                    if es_moderador:
                        if c_btn2.form_submit_button("🗑️ Eliminar"):
                            cursor = conn.cursor(); cursor.execute("DELETE FROM proyectos WHERE id=?", (p_id,)); conn.commit(); st.rerun()

with tab2:
    if es_moderador:
        st.markdown("### Registrar Iniciativa en el Portafolio")
        with st.form("form_nuevo", clear_on_submit=True):
            st.markdown("<p style='color:#0052cc; font-weight:600;'>1. Identificación</p>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            folio = c1.text_input("Código / Folio")
            nombre = c2.text_input("Nombre de la Iniciativa *")
            lider = c3.text_input("Líder Asignado")
            
            st.markdown("<p style='color:#0052cc; font-weight:600; margin-top:15px;'>2. Taxonomía</p>", unsafe_allow_html=True)
            c4, c5, c6 = st.columns(3)
            area = c4.selectbox("Área Solicitante", OPCIONES_AREAS)
            tipo = c5.selectbox("Categoría", OPCIONES_TIPOS)
            subtipo = c6.selectbox("Subcategoría", OPCIONES_SUBTIPOS)
            
            st.markdown("<p style='color:#0052cc; font-weight:600; margin-top:15px;'>3. Gestión</p>", unsafe_allow_html=True)
            c7, c8, c9 = st.columns(3)
            gerente = c7.selectbox("Patrocinador / Gerente", OPCIONES_GERENTES)
            etapa = c8.selectbox("Etapa Inicial", OPCIONES_ETAPAS)
            estatus_inicial = c9.selectbox("Estatus de Tiempo", OPCIONES_ESTATUS, index=4)
            
            st.divider()
            if st.form_submit_button("Crear Proyecto", type="primary"):
                if nombre.strip():
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (folio, nombre, area, tipo, subtipo, gerente, lider, etapa, estatus_inicial))
                    conn.commit(); st.success("✅ Creado con éxito."); st.rerun()
                else: st.error("Falta el nombre.")
    else:
        st.warning("🔒 Solo los Moderadores (Administradores) pueden registrar nuevos proyectos. Si requieres dar de alta uno, comunícate con el Centro de Excelencia.")

conn.close()
