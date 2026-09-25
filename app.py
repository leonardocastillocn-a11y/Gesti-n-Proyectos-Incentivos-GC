import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import tempfile
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA (FORZANDO EL COLOR PRINCIPAL DESDE AQUÍ) ---
st.set_page_config(
    page_title="Portafolio de Incentivos",
    page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ULTRA SOFISTICADO (Bypassing Streamlit Theme) ---
st.markdown("""
    <style>
    /* Importar fuente limpia */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    
    /* Fondo neutro y elegante */
    .stApp { background-color: #F8F9FA !important; }
    
    /* FORZAR COLORES DE BOTONES (Matar el rojo de Streamlit) */
    .stButton > button {
        border-radius: 4px !important; /* Bordes menos redondeados, más serios */
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #05297A !important; /* Azul Coppel Oscuro */
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1C42E8 !important; /* Azul Coppel Brillante al pasar el mouse */
        box-shadow: 0 4px 6px rgba(5, 41, 122, 0.2) !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid #C9C9C9 !important;
        color: #4A4A4A !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border: 1px solid #05297A !important;
        color: #05297A !important;
        background-color: #F8F9FA !important;
    }

    /* FORZAR INPUTS LIMPIOS */
    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stTextArea > div > div > textarea { 
        border-radius: 4px !important; 
        border: 1px solid #D1D5DB !important; 
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        font-size: 0.95rem !important;
    }
    .stTextInput > div > div > input:focus, .stSelectbox > div > div > select:focus {
        border-color: #1C42E8 !important; 
        box-shadow: 0 0 0 1px #1C42E8 !important;
    }

    /* TARJETAS DE MÉTRICAS (Elegancia Absoluta) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; 
        border: 1px solid #E5E7EB; 
        padding: 20px; 
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        border-left: 4px solid #05297A;
    }
    div[data-testid="metric-container"] > label { font-size: 0.8rem !important; color: #6B7280 !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px;}
    div[data-testid="metric-container"] > div > div { font-size: 2.2rem !important; color: #111827 !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important;}
    
    /* TABS (Pestañas) Limpias */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #E5E7EB; gap: 30px;}
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #05297A !important; font-weight: 600 !important; color: #05297A !important;}
    .stTabs [aria-selected="false"] { color: #6B7280 !important; font-weight: 400 !important;}
    
    /* LOGIN CONTAINER (Estilo Portal Corporativo) */
    .login-wrapper {
        background: white; 
        padding: 40px; 
        border-radius: 8px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
        border: 1px solid #E5E7EB;
        margin-top: 5vh;
    }
    .logo-img { width: 120px; margin-bottom: 20px; display: block; margin-left: auto; margin-right: auto;}
    .brand-title { text-align: center; color: #05297A; font-size: 1.8rem; font-weight: 700; margin-bottom: 5px; font-family: 'Inter', sans-serif;}
    .brand-subtitle { text-align: center; color: #6B7280; font-size: 0.9rem; margin-bottom: 30px; font-weight: 300;}
    
    /* ACORDEONES (Expanders) */
    .streamlit-expanderHeader { 
        background-color: white !important; border-radius: 6px !important; border: 1px solid #E5E7EB !important; 
        padding: 12px 15px !important; color: #111827 !important; font-weight: 500 !important;
    }
    .streamlit-expanderContent { 
        border: 1px solid #E5E7EB !important; border-top: none !important; 
        background-color: #FAFAFA !important; padding: 25px !important; border-bottom-left-radius: 6px !important; border-bottom-right-radius: 6px !important;
    }
    
    /* BADGES (Estados) */
    .status-badge { padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; border: 1px solid transparent;}
    .status-green { background-color: #ECFDF5; color: #065F46; border-color: #A7F3D0;}
    .status-red { background-color: #FEF2F2; color: #991B1B; border-color: #FECACA;}
    .status-yellow { background-color: #FFFBEB; color: #92400E; border-color: #FDE68A;}
    .status-gray { background-color: #F3F4F6; color: #374151; border-color: #E5E7EB;}
    
    /* Ocultar elementos default de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
def obtener_conexion(): return sqlite3.connect("db_coppel_v5.db", check_same_thread=False)

def inicializar_db():
    conn = obtener_conexion(); cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS proyectos (id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT, tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT, etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT)""")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)")
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')")
        cursor.execute("INSERT INTO usuarios VALUES ('ivan.salazar@coppel.com', 'Coppel2026', 'Usuario', 'Oscar Ivan Salazar')")
    conn.commit(); conn.close()
inicializar_db()

# --- LOGIN (Sofisticado) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False; st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""
            <div class='login-wrapper'>
                <p class='brand-title'>Portafolio de Incentivos</p>
                <p class='brand-subtitle'>Centro de Excelencia Nacional</p>
            </div>
        """, unsafe_allow_html=True)
        
        # El form va fuera del div HTML para que los componentes nativos de Streamlit funcionen
        with st.form("login_form"):
            st.markdown("<h4 style='color:#111827; font-size:1rem; font-weight:500;'>Autenticación Segura</h4>", unsafe_allow_html=True)
            correo_input = st.text_input("Correo Institucional", placeholder="ejemplo@coppel.com")
            password_input = st.text_input("Contraseña", type="password")
            st.write("")
            submit = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)
            
            if submit:
                if correo_input.strip() == "": st.warning("Ingresa tus credenciales.")
                else:
                    conn = obtener_conexion(); cursor = conn.cursor()
                    cursor.execute("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=?", (correo_input.strip().lower(),))
                    user_data = cursor.fetchone(); conn.close()
                    if user_data and user_data[0] == password_input:
                        st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower()
                        st.session_state.rol = user_data[1]; st.session_state.nombre_actual = user_data[2]; st.rerun()
                    else: st.error("Acceso denegado. Credenciales inválidas.")
    st.stop()

# --- SIDEBAR (Corporativo Minimalista) ---
es_moderador = st.session_state.rol == "Moderador"
with st.sidebar:
    st.markdown(f"<p style='color:#05297A; font-weight:700; font-size:1.1rem; margin-bottom:0;'>{st.session_state.nombre_actual}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#6B7280; font-size:0.8rem; margin-top:0;'>{st.session_state.correo_actual}</p>", unsafe_allow_html=True)
    
    rol_color = "status-green" if es_moderador else "status-gray"
    st.markdown(f"<span class='status-badge {rol_color}'>{st.session_state.rol.upper()}</span>", unsafe_allow_html=True)
    
    st.divider()
    with st.expander("Seguridad de la Cuenta", expanded=False):
        with st.form("form_cambio_pass"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar_pass = st.text_input("Confirmar", type="password")
            if st.form_submit_button("Actualizar Credencial", use_container_width=True):
                if nueva_pass == confirmar_pass and nueva_pass:
                    conn = obtener_conexion(); cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET password=? WHERE correo=?", (nueva_pass, st.session_state.correo_actual))
                    conn.commit(); conn.close(); st.success("Guardado.")
                else: st.error("No coinciden.")
    
    st.divider()
    if st.button("Cerrar Sesión", use_container_width=True, type="secondary"):
        st.session_state.autenticado = False; st.rerun()

# --- DATOS GLOBALES ---
conn = obtener_conexion()
df = pd.read_sql_query("SELECT * FROM proyectos", conn)

# --- HEADER Y MÉTRICAS ---
st.markdown("<h2 style='font-size:1.5rem; color:#111827; margin-bottom:20px;'>Resumen Ejecutivo</h2>", unsafe_allow_html=True)

if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    total = len(df); en_tiempo = len(df[df['estatus_tiempo'] == 'En tiempo'])
    retrasados = len(df[df['estatus_tiempo'] == 'Retrasado']); prom_avance = df['avance_real'].mean() * 100
    
    m1.metric(label="Total Iniciativas", value=total)
    m2.metric(label="Ejecución en Tiempo", value=en_tiempo)
    m3.metric(label="En Riesgo / Retraso", value=retrasados)
    m4.metric(label="Avance del Portafolio", value=f"{prom_avance:.1f}%")
    st.write("")

# --- GENERADOR PDF (Moderador) ---
if es_moderador and not df.empty:
    def generar_pdf(dataframe):
        pdf = FPDF(orientation="L", unit="mm", format="A4"); pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.set_text_color(5, 41, 122) # Azul Coppel
        pdf.cell(0, 8, "Reporte Ejecutivo de Portafolio", ln=True, align="L")
        pdf.set_font("Arial", '', 9); pdf.set_text_color(107, 114, 128) 
        pdf.cell(0, 6, f"Generado el: {datetime.now().strftime('%d/%m/%Y')} | Uso Interno Exclusivo", ln=True, align="L"); pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 8); pdf.set_fill_color(248, 249, 250); pdf.set_text_color(17, 24, 39)
        pdf.cell(20, 10, "Folio", 'B', 0, 'L', True); pdf.cell(70, 10, "Proyecto", 'B', 0, 'L', True)
        pdf.cell(45, 10, "Lider Asignado", 'B', 0, 'L', True); pdf.cell(25, 10, "Estatus", 'B', 0, 'C', True)
        pdf.cell(20, 10, "Avance", 'B', 0, 'C', True); pdf.cell(50, 10, "Etapa Actual", 'B', 0, 'L', True); pdf.cell(45, 10, "Ult. Act.", 'B', 1, 'L', True)
        
        pdf.set_font("Arial", '', 8); pdf.set_text_color(75, 85, 99)
        for _, row in dataframe.iterrows():
            pdf.cell(20, 10, str(row['folio'])[:10], 'B'); pdf.cell(70, 10, str(row['nombre'])[:40], 'B')
            pdf.cell(45, 10, str(row['lider_asignado'])[:25], 'B'); pdf.cell(25, 10, str(row['estatus_tiempo']), 'B', 0, 'C')
            pdf.cell(20, 10, f"{int((row['avance_real'] or 0)*100)}%", 'B', 0, 'C'); pdf.cell(50, 10, str(row['etapa_actual'])[:30], 'B', 0, 'L'); pdf.cell(45, 10, str(row['ultima_actualizacion'])[:16], 'B', 1, 'L')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp: pdf.output(tmp.name); return tmp.name

    with st.sidebar:
        pdf_path = generar_pdf(df)
        with open(pdf_path, "rb") as file: st.download_button("Descargar Reporte (PDF)", data=file, file_name="Portafolio_Incentivos.pdf", use_container_width=True, type="secondary")

# --- PESTAÑAS DINÁMICAS (Líneas simples, sin iconos) ---
if es_moderador: tabs = st.tabs(["Seguimiento Operativo", "Registrar Iniciativa", "Accesos"])
else: tabs = st.tabs(["Seguimiento Operativo", "Registrar Iniciativa"])

# PESTAÑA 1: LISTADO Y EDICIÓN
with tabs[0]:
    if df.empty:
        st.info("No existen registros en el portafolio.")
    else:
        st.write("")
        for _, row in df.iterrows():
            p_id = row["id"]
            if row["estatus_tiempo"] == "En tiempo": css_class = "status-green"
            elif row["estatus_tiempo"] == "Retrasado": css_class = "status-red"
            elif row["estatus_tiempo"] == "Detenido": css_class = "status-yellow"
            else: css_class = "status-gray"
            
            with st.expander(f"{row['folio'] or 'S/F'} | {row['nombre']}"):
                
                # HTML Custom para meter el badge y la progress bar de forma limpia
                st.markdown(f"""
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                        <span style='color:#6B7280; font-size:0.85rem;'>Avance reportado: <b>{int((row['avance_real'] or 0)*100)}%</b></span>
                        <span class='status-badge {css_class}'>{row['estatus_tiempo'].upper()}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.progress(float(row['avance_real'] or 0.0))
                
                with st.form(f"update_{p_id}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"<p style='margin:0; font-size:0.85rem; color:#4B5563;'>Responsable: <b style='color:#111827;'>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
                    c2.markdown(f"<p style='margin:0; font-size:0.85rem; color:#4B5563; text-align:right;'>Actualizado: <b style='color:#111827;'>{row['ultima_actualizacion'] or 'N/D'}</b></p>", unsafe_allow_html=True)
                    st.divider()
                    
                    c_form1, c_form2, c_form3 = st.columns(3)
                    u_etapa = c_form1.selectbox("Fase Actual", OPCIONES_ETAPAS, index=OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0)
                    u_estatus = c_form2.selectbox("Estado", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0)
                    u_avance = c_form3.slider("Progreso (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
                    
                    u_resumen = st.text_area("Bitácora Ejecutiva", row["resumen_estatus"] or "", height=80)
                    
                    l1, l2 = st.columns(2)
                    u_carpeta = l1.text_input("Repositorio Documental (URL)", row["carpeta_url"] or "")
                    u_plan = l2.text_input("Plan de Trabajo (URL)", row["plan_url"] or "")
                    
                    st.write("")
                    btn1, btn2, btn3 = st.columns([2, 2, 6])
                    if btn1.form_submit_button("Guardar Cambios", type="primary"):
                        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor = conn.cursor()
                        cursor.execute("UPDATE proyectos SET etapa_actual=?, estatus_tiempo=?, avance_real=?, resumen_estatus=?, carpeta_url=?, plan_url=?, ultima_actualizacion=? WHERE id=?", (u_etapa, u_estatus, u_avance, u_resumen, u_carpeta, u_plan, ahora, p_id))
                        conn.commit(); st.rerun()
                    
                    if es_moderador:
                        if btn2.form_submit_button("Eliminar", type="secondary"):
                            cursor = conn.cursor(); cursor.execute("DELETE FROM proyectos WHERE id=?", (p_id,)); conn.commit(); st.rerun()

# PESTAÑA 2: NUEVO PROYECTO
with tabs[1]:
    if es_moderador:
        st.write("")
        with st.form("form_nuevo", clear_on_submit=True):
            st.markdown("<p style='color:#05297A; font-weight:600; font-size:1.1rem; margin-bottom:20px;'>Alta de Iniciativa</p>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            folio = c1.text_input("Folio Interno")
            nombre = c2.text_input("Nombre de la Iniciativa *")
            lider = c3.text_input("Líder Asignado")
            
            c4, c5, c6 = st.columns(3)
            area = c4.selectbox("Área Solicitante", OPCIONES_AREAS)
            tipo = c5.selectbox("Categoría", OPCIONES_TIPOS)
            subtipo = c6.selectbox("Subcategoría", OPCIONES_SUBTIPOS)
            
            c7, c8, c9 = st.columns(3)
            gerente = c7.selectbox("Patrocinador", OPCIONES_GERENTES)
            etapa = c8.selectbox("Fase de Arranque", OPCIONES_ETAPAS)
            estatus_inicial = c9.selectbox("Estado Inicial", OPCIONES_ESTATUS, index=4)
            
            st.write("")
            if st.form_submit_button("Registrar Proyecto", type="primary"):
                if nombre.strip():
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)", (folio, nombre, area, tipo, subtipo, gerente, lider, etapa, estatus_inicial))
                    conn.commit(); st.success("Iniciativa registrada correctamente."); st.rerun()
                else: st.error("El campo 'Nombre' es obligatorio.")
    else:
        st.warning("El alta de proyectos está restringida al perfil Moderador.")

# PESTAÑA 3: USUARIOS
if es_moderador:
    with tabs[2]:
        st.write("")
        df_users = pd.read_sql_query("SELECT nombre as Colaborador, correo as Correo, rol as Perfil FROM usuarios", conn)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        st.write("")
        
        c_add, c_del = st.columns(2)
        with c_add:
            with st.form("form_alta_usuario", clear_on_submit=True):
                st.markdown("<p style='color:#05297A; font-weight:600;'>Alta de Usuario</p>", unsafe_allow_html=True)
                n_nombre = st.text_input("Nombre Completo")
                n_correo = st.text_input("Correo Institucional")
                n_pass = st.text_input("Clave Temporal", type="password")
                n_rol = st.selectbox("Nivel de Acceso", ["Usuario", "Moderador"])
                st.write("")
                if st.form_submit_button("Crear Cuenta", type="primary"):
                    if n_correo and n_pass and n_nombre:
                        try:
                            cursor = conn.cursor(); cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", (n_correo.strip().lower(), n_pass, n_rol, n_nombre))
                            conn.commit(); st.success("Cuenta habilitada."); st.rerun()
                        except: st.error("El correo ya se encuentra registrado.")
                    else: st.warning("Por favor, completa todos los campos.")
            
        with c_del:
            with st.form("form_baja_usuario"):
                st.markdown("<p style='color:#05297A; font-weight:600;'>Revocación de Accesos</p>", unsafe_allow_html=True)
                lista_correos = df_users['Correo'].tolist()
                if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
                correo_borrar = st.selectbox("Seleccione el colaborador", ["Seleccionar..."] + lista_correos)
                st.write(""); st.write(""); st.write("")
                if st.form_submit_button("Eliminar Cuenta", type="secondary"):
                    if correo_borrar != "Seleccionar...":
                        cursor = conn.cursor(); cursor.execute("DELETE FROM usuarios WHERE correo=?", (correo_borrar,)); conn.commit(); st.success("Cuenta revocada."); st.rerun()
                    else: st.warning("Seleccione una cuenta válida.")

conn.close()
