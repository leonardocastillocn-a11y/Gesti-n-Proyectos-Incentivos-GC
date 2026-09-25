import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import tempfile
from fpdf import FPDF
import plotly.express as px
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Portafolio de Incentivos Coppel",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS INSTITUCIONAL (AZUL COPPEL - ALTO CONTRASTE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8F9FA !important;
        color: #081754 !important;
    }

    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #081754 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    input, textarea, select, 
    .stTextInput input, .stTextArea textarea, .stSelectbox select,
    div[data-baseweb="select"] span, div[data-baseweb="select"] div,
    div[role="combobox"] {
        color: #081754 !important;
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div {
        border-radius: 6px !important;
        border: 1px solid #C9C9C9 !important;
        background-color: #FFFFFF !important;
    }

    ::placeholder, input::placeholder, textarea::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
    }

    /* BOTONES PRIMARIOS AZUL COPPEL */
    div[data-testid="stFormSubmitButton"] button,
    button[data-testid="baseButton-primary"],
    .stButton > button {
        background-color: #05297A !important;
        background: #05297A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div[data-testid="stFormSubmitButton"] button *,
    button[data-testid="baseButton-primary"] *,
    .stButton > button * {
        color: #FFFFFF !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button:hover {
        background-color: #1C42E8 !important;
        background: #1C42E8 !important;
        box-shadow: 0 4px 10px rgba(28, 66, 232, 0.25) !important;
    }

    /* BOTONES SECUNDARIOS */
    button[data-testid="baseButton-secondary"],
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #C9C9C9 !important;
        color: #4A4A4A !important;
    }
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover {
        border-color: #05297A !important;
        color: #05297A !important;
    }

    /* TARJETAS DE MÉTRICAS */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #C9C9C9 !important;
        border-left: 4px solid #05297A !important;
        padding: 15px !important;
        border-radius: 8px !important;
    }
    div[data-testid="metric-container"] label, 
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] p { 
        color: #4A4A4A !important; 
        font-size: 0.85rem !important; 
        font-weight: 600 !important; 
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] div { 
        color: #081754 !important; 
        font-size: 2rem !important; 
        font-weight: 700 !important; 
    }

    /* PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #C9C9C9; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #05297A !important; font-weight: 700 !important; color: #081754 !important; }
    .stTabs [aria-selected="false"] { color: #4A4A4A !important; font-weight: 500 !important; }

    /* ACORDEONES (EXPANDERS) */
    .streamlit-expanderHeader, .streamlit-expanderHeader p { 
        background-color: #FFFFFF !important; 
        color: #081754 !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent { 
        border: 1px solid #C9C9C9 !important; 
        border-top: none !important; 
        background-color: #FFFFFF !important; 
        padding: 20px !important;
    }

    .status-badge { padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; border: 1px solid transparent;}
    .status-green { background-color: #E8F5E9; color: #2E7D32 !important; border-color: #A5D6A7;}
    .status-yellow { background-color: #FFF9C4; color: #F57F17 !important; border-color: #FFF59D;}
    .status-gray { background-color: #EEE8E3; color: #4A4A4A !important; border-color: #C9C9C9;}

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
    cursor.execute("""CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, proyecto_id INTEGER, nombre_tarea TEXT NOT NULL, responsable TEXT, fecha_inicio TEXT, duracion_dias INTEGER, fecha_fin TEXT, porcentaje_avance REAL, predecesoras TEXT, FOREIGN KEY (proyecto_id) REFERENCES proyectos(id))""")
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')")
        cursor.execute("INSERT INTO usuarios VALUES ('ivan.salazar@coppel.com', 'Coppel2026', 'Usuario', 'Oscar Ivan Salazar')")
    conn.commit(); conn.close()
inicializar_db()

# --- FUNCIONES DE SOPORTE ---
def obtener_lista_usuarios():
    conn = obtener_conexion()
    df_users = pd.read_sql_query("SELECT nombre FROM usuarios ORDER BY nombre ASC", conn)
    conn.close()
    if not df_users.empty:
        return df_users['nombre'].tolist()
    return ["Leonardo Castillo", "Oscar Ivan Salazar"]

def calcular_fechas_tarea(proyecto_id):
    conn = obtener_conexion()
    df_t = pd.read_sql_query("SELECT * FROM tareas WHERE proyecto_id = ? ORDER BY id ASC", conn, params=(proyecto_id,))
    conn.close()
    if df_t.empty:
        return df_t
    df_t['fecha_inicio'] = pd.to_datetime(df_t['fecha_inicio'])
    df_t['fecha_fin'] = pd.to_datetime(df_t['fecha_fin'])
    fechas_fin = {}
    for idx, row in df_t.iterrows():
        t_id = row['id']
        preds = str(row['predecesoras']).strip() if row['predecesoras'] else ""
        if preds:
            pred_ids = [int(p.strip()) for p in preds.split(',') if p.strip().isdigit() and int(p.strip()) in fechas_fin]
            if pred_ids:
                max_pred_fin = max([fechas_fin[pid] for pid in pred_ids])
                df_t.at[idx, 'fecha_inicio'] = max_pred_fin + timedelta(days=1)
        inicio = df_t.at[idx, 'fecha_inicio']
        duracion = int(row['duracion_dias'] or 1)
        fin = inicio + timedelta(days=duracion - 1)
        df_t.at[idx, 'fecha_fin'] = fin
        fechas_fin[t_id] = fin
    return df_t

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False; st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
    col_izq, col_centro, col_der = st.columns([1, 1.2, 1])
    with col_centro:
        st.write(""); st.write(""); st.write("")
        st.markdown("<h1 style='text-align: center; color:#081754 !important;'>Portafolio de Incentivos</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #4A4A4A; margin-bottom: 30px;'>Coppel</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h3 style='color:#05297A !important; font-size: 1.1rem;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
            correo_input = st.text_input("Correo Corporativo", placeholder="tu.nombre@coppel.com")
            password_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
            st.write("")
            submit = st.form_submit_button("Ingresar", type="primary", use_container_width=True)
            
            if submit:
                if correo_input.strip() == "": st.warning("El correo es requerido.")
                else:
                    conn = obtener_conexion(); cursor = conn.cursor()
                    cursor.execute("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=?", (correo_input.strip().lower(),))
                    user_data = cursor.fetchone(); conn.close()
                    if user_data and user_data[0] == password_input:
                        st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower()
                        st.session_state.rol = user_data[1]; st.session_state.nombre_actual = user_data[2]; st.rerun()
                    else: st.error("Credenciales incorrectas.")
    st.stop()

# --- SIDEBAR ---
es_moderador = st.session_state.rol == "Moderador"
with st.sidebar:
    st.markdown(f"<h3 style='margin-bottom:0; font-size:1.1rem; color:#081754;'>{st.session_state.nombre_actual}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#4A4A4A; font-size:0.85rem; margin-top:0;'>{st.session_state.correo_actual}</p>", unsafe_allow_html=True)
    
    badge_color = "status-green" if es_moderador else "status-gray"
    st.markdown(f"<div><span class='status-badge {badge_color}'>{st.session_state.rol}</span></div>", unsafe_allow_html=True)
    
    st.divider()
    with st.expander("Seguridad", expanded=False):
        with st.form("form_cambio_pass"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar_pass = st.text_input("Confirmar", type="password")
            if st.form_submit_button("Actualizar", use_container_width=True):
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
st.markdown("<h2 style='margin-bottom: 20px; color:#081754;'>Visión General</h2>", unsafe_allow_html=True)

if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    total = len(df); en_tiempo = len(df[df['estatus_tiempo'] == 'En tiempo'])
    retrasados = len(df[df['estatus_tiempo'] == 'Retrasado']); prom_avance = df['avance_real'].mean() * 100
    
    m1.metric(label="Iniciativas Activas", value=total)
    m2.metric(label="Ejecución en Tiempo", value=en_tiempo)
    m3.metric(label="En Riesgo / Retraso", value=retrasados)
    m4.metric(label="Avance Global", value=f"{prom_avance:.1f}%")
    st.write("")

# --- GENERADOR DE PDF EJECUTIVO ---
if es_moderador and not df.empty:
    def generar_pdf_ejecutivo(dataframe):
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(5, 41, 122)
        pdf.cell(0, 8, "Reporte Ejecutivo de Portafolio - Incentivos Coppel", ln=True, align="L")
        
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(100, 100, 100)
        fecha_emision = datetime.now().strftime('%d/%m/%Y %H:%M hrs')
        pdf.cell(0, 6, f"Fecha de emisión: {fecha_emision} | Generado por: {st.session_state.nombre_actual}", ln=True, align="L")
        pdf.ln(4)
        
        pdf.set_font("Arial", 'B', 8)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(8, 23, 84)
        
        pdf.cell(22, 8, "Folio", 1, 0, 'C', True)
        pdf.cell(60, 8, "Nombre del Proyecto", 1, 0, 'L', True)
        pdf.cell(30, 8, "Área", 1, 0, 'L', True)
        pdf.cell(35, 8, "Responsable", 1, 0, 'L', True)
        pdf.cell(25, 8, "Estatus", 1, 0, 'C', True)
        pdf.cell(18, 8, "Avance", 1, 0, 'C', True)
        pdf.cell(42, 8, "Ult. Actualizacion", 1, 0, 'C', True)
        pdf.cell(45, 8, "Etapa Actual", 1, 1, 'L', True)
        
        pdf.set_font("Arial", '', 8)
        pdf.set_text_color(40, 40, 40)
        
        for _, row in dataframe.iterrows():
            pdf.cell(22, 7, str(row['folio'] or 'S/F')[:12], 1, 0, 'C')
            pdf.cell(60, 7, str(row['nombre'] or '')[:35], 1, 0, 'L')
            pdf.cell(30, 7, str(row['area_negocio'] or 'N/A')[:18], 1, 0, 'L')
            pdf.cell(35, 7, str(row['lider_asignado'] or 'Sin Asignar')[:22], 1, 0, 'L')
            pdf.cell(25, 7, str(row['estatus_tiempo'] or 'N/A')[:15], 1, 0, 'C')
            pdf.cell(18, 7, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, 'C')
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(42, 7, str(row['ultima_actualizacion'] or 'Sin registro')[:19], 1, 0, 'C')
            pdf.set_font("Arial", '', 8)
            pdf.cell(45, 7, str(row['etapa_actual'] or 'N/A')[:25], 1, 1, 'L')
            
            resumen_txt = str(row['resumen_estatus'] or '').strip()
            if resumen_txt:
                pdf.set_font("Arial", 'I', 7)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(22, 6, "Bitácora:", "BL", 0, 'R')
                pdf.cell(255, 6, resumen_txt[:150], "BR", 1, 'L')
                pdf.set_font("Arial", '', 8)
                pdf.set_text_color(40, 40, 40)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            return tmp.name

    with st.sidebar:
        pdf_path = generar_pdf_ejecutivo(df)
        with open(pdf_path, "rb") as file:
            st.download_button("Descargar PDF Ejecutivo", data=file, file_name=f"Reporte_Portafolio_{datetime.now().strftime('%Y%m%d')}.pdf", use_container_width=True, type="secondary")

# --- PESTAÑAS DINÁMICAS ---
if es_moderador: tabs = st.tabs(["Seguimiento Operativo", "Nuevo Proyecto", "Accesos"])
else: tabs = st.tabs(["Seguimiento Operativo", "Nuevo Proyecto"])

lista_lideres_registrados = obtener_lista_usuarios()

# PESTAÑA 1: VISOR + PLAN DE TRABAJO CON PREDECESORAS
with tabs[0]:
    if df.empty:
        st.info("El portafolio está vacío.")
    else:
        st.markdown("<h4 style='color:#05297A; margin-bottom:10px;'>🔍 Filtros de Búsqueda</h4>", unsafe_allow_html=True)
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        txt_busqueda = f_col1.text_input("Buscar por Folio o Nombre", placeholder="ej. INC-001 o Banca")
        filtro_area = f_col2.selectbox("Área del Negocio", ["Todas las Áreas"] + OPCIONES_AREAS)
        filtro_estatus = f_col3.selectbox("Estatus de Tiempo", ["Todos los Estatus"] + OPCIONES_ESTATUS)
        filtro_lider = f_col4.selectbox("Responsable", ["Todos los Responsables"] + lista_lideres_registrados)
        
        df_filtrado = df.copy()
        if txt_busqueda.strip():
            query = txt_busqueda.strip().lower()
            df_filtrado = df_filtrado[
                df_filtrado['nombre'].str.lower().str.contains(query, na=False) | 
                df_filtrado['folio'].str.lower().str.contains(query, na=False)
            ]
        if filtro_area != "Todas las Áreas":
            df_filtrado = df_filtrado[df_filtrado["area_negocio"] == filtro_area]
        if filtro_estatus != "Todos los Estatus":
            df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"] == filtro_estatus]
        if filtro_lider != "Todos los Responsables":
            df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == filtro_lider]
            
        st.caption(f"📌 Mostrando **{len(df_filtrado)}** de **{len(df)}** iniciativas en el portafolio.")
        st.divider()
        
        if df_filtrado.empty:
            st.warning("No se encontraron iniciativas que coincidan con los filtros aplicados.")
        else:
            for _, row in df_filtrado.iterrows():
                p_id = row["id"]
                
                with st.expander(f"{row['folio'] or 'S/F'} | {row['nombre']} — Avance Global: {int((row['avance_real'] or 0)*100)}%"):
                    st.progress(float(row['avance_real'] or 0.0))
                    
                    with st.form(f"update_{p_id}"):
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"<p style='margin:0; font-size:0.88rem;'><span style='color:#4A4A4A;'>Responsable:</span> <b style='color:#081754;'>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
                        c2.markdown(f"<p style='margin:0; font-size:0.88rem;'><span style='color:#4A4A4A;'>Área:</span> <b style='color:#081754;'>{row['area_negocio']}</b></p>", unsafe_allow_html=True)
                        c3.markdown(f"<p style='margin:0; font-size:0.88rem; text-align:right;'><span style='color:#4A4A4A;'>Última Actualización:</span> <b style='color:#05297A;'>{row['ultima_actualizacion'] or 'Sin registro'}</b></p>", unsafe_allow_html=True)
                        st.divider()
                        
                        c_form1, c_form2, c_form3 = st.columns(3)
                        u_etapa = c_form1.selectbox("Fase Actual", OPCIONES_ETAPAS, index=OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0)
                        u_estatus = c_form2.selectbox("Estado", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0)
                        u_avance = c_form3.slider("Progreso Validado (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
                        
                        if es_moderador:
                            idx_lider = lista_lideres_registrados.index(row["lider_asignado"]) if row["lider_asignado"] in lista_lideres_registrados else 0
                            u_lider = st.selectbox("Reasignar Líder de Proyecto", lista_lideres_registrados, index=idx_lider)
                        else:
                            u_lider = row["lider_asignado"]
                            
                        u_resumen = st.text_area("Bitácora de Estatus / Comentarios", row["resumen_estatus"] or "", height=80)
                        
                        l1, l2 = st.columns(2)
                        u_carpeta = l1.text_input("Repositorio Drive (URL)", row["carpeta_url"] or "")
                        u_plan = l2.text_input("Plan de Trabajo Excel (URL)", row["plan_url"] or "")
                        
                        st.write("")
                        btn1, btn2, btn3 = st.columns([2, 2, 6])
                        if btn1.form_submit_button("Guardar Cambios", type="primary"):
                            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cursor = conn.cursor()
                            cursor.execute("UPDATE proyectos SET etapa_actual=?, estatus_tiempo=?, avance_real=?, lider_asignado=?, resumen_estatus=?, carpeta_url=?, plan_url=?, ultima_actualizacion=? WHERE id=?", (u_etapa, u_estatus, u_avance, u_lider, u_resumen, u_carpeta, u_plan, ahora, p_id))
                            conn.commit(); st.rerun()
                        
                        if es_moderador:
                            if btn2.form_submit_button("Eliminar", type="secondary"):
                                cursor = conn.cursor(); cursor.execute("DELETE FROM proyectos WHERE id=?", (p_id,)); conn.commit(); st.rerun()

                    # --- SECCIÓN PLAN DE TRABAJO CON PREDECESORAS ---
                    st.divider()
                    st.markdown("<h4 style='color:#05297A;'>📅 Plan de Trabajo y Cronograma (Gantt)</h4>", unsafe_allow_html=True)
                    
                    df_tareas = calcular_fechas_tarea(p_id)
                    
                    if not df_tareas.empty:
                        fig = px.timeline(
                            df_tareas, x_start="fecha_inicio", x_end="fecha_fin", y="nombre_tarea",
                            color="porcentaje_avance", color_continuous_scale=[[0, "#C9C9C9"], [0.5, "#F0D224"], [1, "#05297A"]],
                            hover_data=["id", "responsable", "predecesoras", "duracion_dias"], title="Cronograma WBS de Tareas y Dependencias"
                        )
                        fig.update_yaxes(autorange="reversed")
                        fig.update_layout(height=250 + (len(df_tareas) * 25), xaxis_title="Fechas", yaxis_title="Tareas", margin=dict(l=10, r=10, t=30, b=10))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.dataframe(df_tareas[["id", "nombre_tarea", "responsable", "fecha_inicio", "duracion_dias", "fecha_fin", "predecesoras", "porcentaje_avance"]], use_container_width=True, hide_index=True)
                    else:
                        st.info("No hay tareas registradas en el cronograma interactivo.")
                    
                    with st.expander("➕ Agregar Tarea al Cronograma"):
                        with st.form(f"form_tarea_{p_id}", clear_on_submit=True):
                            col_t1, col_t2 = st.columns(2)
                            t_nombre = col_t1.text_input("Nombre de la Tarea *")
                            t_resp = col_t2.selectbox("Responsable", lista_lideres_registrados)
                            
                            col_t3, col_t4, col_t5 = st.columns(3)
                            t_f_inicio = col_t3.date_input("Fecha Inicio estimada")
                            t_duracion = col_t4.number_input("Duración (Días)", min_value=1, value=5)
                            t_preds = col_t5.text_input("Predecesoras (IDs ej. 1, 2)", help="Escribe los IDs de las tareas que deben terminar antes.")
                            
                            if st.form_submit_button("Guardar Tarea"):
                                if t_nombre.strip():
                                    cursor = conn.cursor()
                                    f_fin_est = pd.to_datetime(t_f_inicio) + timedelta(days=t_duracion - 1)
                                    cursor.execute("""
                                        INSERT INTO tareas (
                                            proyecto_id, nombre_tarea, responsable, fecha_inicio, 
                                            duracion_dias, fecha_fin, porcentaje_avance, predecesoras
                                        ) VALUES (?, ?, ?, ?, ?, ?, 0.0, ?)
                                    """, (p_id, t_nombre, t_resp, str(t_f_inicio), t_duracion, str(f_fin_est.date()), t_preds))
                                    conn.commit(); st.success("Tarea agregada."); st.rerun()
                                else:
                                    st.error("Nombre requerido.")

# PESTAÑA 2: NUEVO PROYECTO
with tabs[1]:
    if es_moderador:
        st.write("")
        with st.form("form_nuevo", clear_on_submit=True):
            st.markdown("<h4 style='color:#05297A;'>Alta de Iniciativa</h4>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            folio = c1.text_input("Folio Interno")
            nombre = c2.text_input("Nombre de la Iniciativa *")
            lider = c3.selectbox("Líder Asignado *", lista_lideres_registrados)
            
            c4, c5, c6 = st.columns(3)
            area = c4.selectbox("Área Solicitante", OPCIONES_AREAS)
            tipo = c5.selectbox("Categoría General", OPCIONES_TIPOS)
            subtipo = c6.selectbox("Subcategoría Específica", OPCIONES_SUBTIPOS)
            
            c7, c8, c9 = st.columns(3)
            gerente = c7.selectbox("Patrocinador", OPCIONES_GERENTES)
            etapa = c8.selectbox("Fase de Arranque", OPCIONES_ETAPAS)
            estatus_inicial = c9.selectbox("Estado Inicial", OPCIONES_ESTATUS, index=4)
            
            st.write("")
            if st.form_submit_button("Registrar Proyecto", type="primary"):
                if nombre.strip():
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)", (folio, nombre, area, tipo, subtipo, gerente, lider, etapa, estatus_inicial))
                    conn.commit(); st.success("Iniciativa creada."); st.rerun()
                else: st.error("El Nombre es obligatorio.")
    else:
        st.warning("Solo los Moderadores pueden dar de alta proyectos.")

# PESTAÑA 3: USUARIOS
if es_moderador:
    with tabs[2]:
        st.write("")
        df_users = pd.read_sql_query("SELECT nombre as Colaborador, correo as Correo, rol as Permisos FROM usuarios", conn)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        st.write("")
        
        c_add, c_del = st.columns(2)
        with c_add:
            with st.form("form_alta_usuario", clear_on_submit=True):
                st.markdown("<h4 style='color:#05297A;'>Dar de Alta</h4>", unsafe_allow_html=True)
                n_nombre = st.text_input("Nombre Completo")
                n_correo = st.text_input("Correo Institucional")
                n_pass = st.text_input("Clave Temporal", type="password")
                n_rol = st.selectbox("Nivel de Permisos", ["Usuario", "Moderador"])
                st.write("")
                if st.form_submit_button("Guardar Usuario", type="primary"):
                    if n_correo and n_pass and n_nombre:
                        try:
                            cursor = conn.cursor(); cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", (n_correo.strip().lower(), n_pass, n_rol, n_nombre))
                            conn.commit(); st.success("Cuenta activada."); st.rerun()
                        except: st.error("El correo ya existe.")
                    else: st.warning("Faltan datos.")
            
        with c_del:
            with st.form("form_baja_usuario"):
                st.markdown("<h4 style='color:#081754;'>Revocar Acceso</h4>", unsafe_allow_html=True)
                lista_correos = df_users['Correo'].tolist()
                if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
                correo_borrar = st.selectbox("Colaborador a eliminar", ["Seleccionar..."] + lista_correos)
                st.write(""); st.write(""); st.write("")
                if st.form_submit_button("Eliminar Cuenta", type="secondary"):
                    if correo_borrar != "Seleccionar...":
                        cursor = conn.cursor(); cursor.execute("DELETE FROM usuarios WHERE correo=?", (correo_borrar,)); conn.commit(); st.success("Cuenta eliminada."); st.rerun()
                    else: st.warning("Selecciona una cuenta.")

conn.close()
