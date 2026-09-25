from datetime import datetime, timedelta
import tempfile
from fpdf import FPDF
import pandas as pd
import plotly.express as px
import sqlalchemy
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Portafolio de Incentivos Coppel",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS PREMIUM / ENTERPRISE UI ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Fondo global de la app */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #F4F6F9 !important; /* Gris ultra claro para dar profundidad */
        color: #1E293B !important; /* Texto pizarra oscuro */
    }

    /* Ajuste del Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important;
    }

    /* Títulos generales */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Campos de entrada */
    .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFC !important;
        transition: all 0.2s ease;
    }
    .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within {
        border-color: #05297A !important;
        box-shadow: 0 0 0 2px rgba(5, 41, 122, 0.2) !important;
        background-color: #FFFFFF !important;
    }

    /* BOTONES PRIMARIOS */
    div[data-testid="stFormSubmitButton"] button,
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(28, 66, 232, 0.2), 0 2px 4px -1px rgba(28, 66, 232, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover,
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(28, 66, 232, 0.3), 0 4px 6px -2px rgba(28, 66, 232, 0.15) !important;
    }

    /* BOTONES SECUNDARIOS */
    button[data-testid="baseButton-secondary"],
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #334155 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover {
        border-color: #0F172A !important;
        color: #0F172A !important;
        background-color: #F8FAFC !important;
    }

    /* CORRECCIÓN DE COLOR DE TEXTO EN BOTONES */
    .stButton > button[kind="primary"] p { color: #FFFFFF !important; }
    .stButton > button[kind="secondary"] p { color: inherit !important; }

    /* TARJETAS DE MÉTRICAS */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-top: 4px solid #05297A !important;
        padding: 20px 24px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    }
    div[data-testid="metric-container"] label { 
        color: #64748B !important; 
        font-size: 0.85rem !important; 
        font-weight: 600 !important; 
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] div { 
        color: #0F172A !important; 
        font-size: 2.2rem !important; 
        font-weight: 800 !important; 
        letter-spacing: -0.02em;
    }

    /* PESTAÑAS (TABS) Modernas */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 32px; 
        border-bottom: 2px solid #E2E8F0; 
        padding-bottom: 0px;
    }
    .stTabs [aria-selected="true"] { 
        border-bottom: 3px solid #05297A !important; 
        font-weight: 700 !important; 
        color: #05297A !important; 
        background-color: transparent !important;
    }
    .stTabs [aria-selected="false"] { 
        color: #64748B !important; 
        font-weight: 500 !important; 
    }

    /* ACORDEONES (EXPANDERS - Aspecto de Tarjeta) */
    .streamlit-expanderHeader { 
        background-color: #FFFFFF !important; 
        color: #0F172A !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 1rem !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
    }
    .streamlit-expanderContent { 
        border: 1px solid #E2E8F0 !important; 
        border-top: none !important; 
        background-color: #FFFFFF !important; 
        padding: 24px !important;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }

    /* BADGES DE ESTATUS */
    .status-badge { 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-size: 0.75rem; 
        font-weight: 700; 
        letter-spacing: 0.02em;
        display: inline-block;
    }
    .status-green { background-color: #DCFCE7; color: #166534 !important; border: 1px solid #BBF7D0;}
    .status-yellow { background-color: #FEF9C3; color: #854D0E !important; border: 1px solid #FEF08A;}
    .status-gray { background-color: #F1F5F9; color: #475569 !important; border: 1px solid #E2E8F0;}

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONSTANTES ---
OPCIONES_AREAS = [
    "Incentivos", "Afore", "Banca Empresarial", "Banco", "CAT Cobranza", 
    "CAT P&V", "CEDIS", "Cobranza Domiciliaria", "Credito Automotriz", 
    "Inmobiliaria", "Retail", "Sale Vale",
]
OPCIONES_TIPOS = ["Esquema de Incentivos", "Tecnología", "Estratégicos", "Procesos", "Campañas", "Auditorías"]
OPCIONES_SUBTIPOS = [
    "EI-Nuevo incentivo completo", "EI-Actualización completa de incentivo", 
    "EI-Ajuste menor de incentivo", "EI-Ajuste mayor de incentivo", 
    "EI-Casos especiales", "CA-Campaña", "CA-Concurso", "PR-Documentación oficial", 
    "PR-Nuevo proceso", "TE-Software", "TE-Tableros", "Otros",
]
OPCIONES_ETAPAS = [
    "1. Diseño (EI)", "2. Prueba piloto (EI)", "3. Escalamiento nacional (EI)", "4. Cierre (EI)", 
    "1. Diseño (CA)", "2. Implementación (CA)", "3. Evaluación y cierre (CA)", "4. Cierre (CA)", 
    "1. Planeación", "2. Ejecución", "3. Cierre",
]
OPCIONES_ESTATUS = ["En tiempo", "Retrasado", "Detenido", "Cancelado", "Por iniciar"]
OPCIONES_GERENTES = [
    "Andres Avila", "Eduardo Rodriguez", "Heriberto Vega", "Janik Orozco", 
    "Kurokusi Ochoa", "Noel Aquino", "Yahir Ramirez", "Giovanni Vallejo", "Ruben Rivera",
]

# --- CONEXIÓN A BASE DE DATOS (POSTGRESQL) ---
def obtener_engine():
  if "postgres" in st.secrets:
    db_url = st.secrets["postgres"]["url"]
  else:
    db_url = "sqlite:///db_coppel_v5.db"
  return sqlalchemy.create_engine(db_url)

def inicializar_db():
  engine = obtener_engine()
  with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id SERIAL PRIMARY KEY, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT,
                tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT,
                etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT,
                carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT
            )
        """))
    conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT
            )
        """))
    conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS tareas (
                id SERIAL PRIMARY KEY, proyecto_id INTEGER, nombre_tarea TEXT NOT NULL,
                responsable TEXT, fecha_inicio TEXT, duracion_dias INTEGER, fecha_fin TEXT,
                porcentaje_avance REAL, predecesoras TEXT
            )
        """))
    res = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM usuarios")).fetchone()
    if res[0] == 0:
      conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')"))
      conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES ('ivan.salazar@coppel.com', 'Coppel2026', 'Usuario', 'Oscar Ivan Salazar')"))

inicializar_db()

def obtener_lista_usuarios():
  engine = obtener_engine()
  df_users = pd.read_sql("SELECT nombre FROM usuarios ORDER BY nombre ASC", engine)
  if not df_users.empty: return df_users["nombre"].tolist()
  return ["Leonardo Castillo", "Oscar Ivan Salazar"]

def calcular_fechas_tarea(proyecto_id):
  engine = obtener_engine()
  df_t = pd.read_sql(f"SELECT * FROM tareas WHERE proyecto_id = {proyecto_id} ORDER BY id ASC", engine)
  if df_t.empty: return df_t
  df_t["fecha_inicio"] = pd.to_datetime(df_t["fecha_inicio"])
  df_t["fecha_fin"] = pd.to_datetime(df_t["fecha_fin"])
  fechas_fin = {}
  for idx, row in df_t.iterrows():
    t_id = row["id"]
    preds = str(row["predecesoras"]).strip() if row["predecesoras"] else ""
    if preds:
      pred_ids = [int(p.strip()) for p in preds.split(",") if p.strip().isdigit() and int(p.strip()) in fechas_fin]
      if pred_ids:
        max_pred_fin = max([fechas_fin[pid] for pid in pred_ids])
        df_t.at[idx, "fecha_inicio"] = max_pred_fin + timedelta(days=1)
    inicio = df_t.at[idx, "fecha_inicio"]
    duracion = int(row["duracion_dias"] or 1)
    fin = inicio + timedelta(days=duracion - 1)
    df_t.at[idx, "fecha_fin"] = fin
    fechas_fin[t_id] = fin
  return df_t

# --- LOGIN ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False; st.session_state.correo_actual = None
  st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
  col_izq, col_centro, col_der = st.columns([1, 1.2, 1])
  with col_centro:
    st.write(""); st.write(""); st.write("")
    st.markdown("<h1 style='text-align: center; color:#05297A !important; font-size: 2.5rem; letter-spacing: -1px;'>Portafolio de Incentivos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 40px; font-size: 1.1rem;'>Coppel Corporativo</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
      st.markdown("<h3 style='color:#0F172A !important; font-size: 1.2rem; margin-bottom: 20px;'>Acceso al Sistema</h3>", unsafe_allow_html=True)
      correo_input = st.text_input("Correo Corporativo", placeholder="tu.nombre@coppel.com")
      password_input = st.text_input("Contraseña", type="password")
      st.write("")
      submit = st.form_submit_button("Ingresar de forma segura", type="primary", use_container_width=True)

      if submit:
        if correo_input.strip() == "": st.warning("El correo es requerido.")
        else:
          engine = obtener_engine()
          with engine.connect() as conn:
            res = conn.execute(sqlalchemy.text("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=:c"), {"c": correo_input.strip().lower()}).fetchone()
            if res and res[0] == password_input:
              st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower()
              st.session_state.rol = res[1]; st.session_state.nombre_actual = res[2]; st.rerun()
            else: st.error("Credenciales incorrectas.")
  st.stop()

# --- SIDEBAR MEJORADO ---
es_moderador = st.session_state.rol == "Moderador"
with st.sidebar:
  st.markdown(f"<div style='background-color:#F8FAFC; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>"
              f"<h3 style='margin:0 0 5px 0; font-size:1.1rem; color:#0F172A;'>👤 {st.session_state.nombre_actual}</h3>"
              f"<p style='margin:0 0 10px 0; color:#64748B; font-size:0.8rem;'>{st.session_state.correo_actual}</p>"
              f"<span class='status-badge {'status-green' if es_moderador else 'status-gray'}'>{st.session_state.rol}</span>"
              f"</div>", unsafe_allow_html=True)
  
  with st.expander("⚙️ Configuración de Seguridad", expanded=False):
    with st.form("form_cambio_pass"):
      nueva_pass = st.text_input("Nueva Contraseña", type="password")
      confirmar_pass = st.text_input("Confirmar", type="password")
      if st.form_submit_button("Actualizar Clave", use_container_width=True):
        if nueva_pass == confirmar_pass and nueva_pass:
          engine = obtener_engine()
          with engine.begin() as conn:
            conn.execute(sqlalchemy.text("UPDATE usuarios SET password=:p WHERE correo=:c"), {"p": nueva_pass, "c": st.session_state.correo_actual})
          st.success("Guardado.")
        else: st.error("No coinciden.")

  st.write("")
  if st.button("Cerrar Sesión", use_container_width=True, type="secondary"):
    st.session_state.autenticado = False; st.rerun()

# --- DATOS GLOBALES ---
engine = obtener_engine()
df = pd.read_sql("SELECT * FROM proyectos", engine)

# --- HEADER Y MÉTRICAS (SIEMPRE VISIBLES) ---
st.markdown("<h2 style='margin-bottom: 25px; color:#0F172A; display: flex; align-items: center; gap: 10px;'>📊 Visión General del Portafolio</h2>", unsafe_allow_html=True)

total_proyectos = len(df)
en_tiempo = len(df[df["estatus_tiempo"] == "En tiempo"]) if total_proyectos > 0 else 0
retrasados = len(df[df["estatus_tiempo"] == "Retrasado"]) if total_proyectos > 0 else 0
prom_avance = df["avance_real"].mean() * 100 if total_proyectos > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="INICIATIVAS ACTIVAS", value=total_proyectos)
m2.metric(label="EJECUCIÓN EN TIEMPO", value=en_tiempo)
m3.metric(label="EN RIESGO / RETRASO", value=retrasados)
m4.metric(label="AVANCE GLOBAL", value=f"{prom_avance:.1f}%")
st.write("")
st.write("")

# --- GENERADOR DE PDF EJECUTIVO ---
if es_moderador and not df.empty:
  def generar_pdf_ejecutivo(dataframe):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page()
    pdf.set_font("Arial", "B", 16); pdf.set_text_color(5, 41, 122)
    pdf.cell(0, 8, "Reporte Ejecutivo de Portafolio - Incentivos Coppel", ln=True, align="L")
    pdf.set_font("Arial", "", 9); pdf.set_text_color(100, 100, 100)
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M hrs")
    pdf.cell(0, 6, f"Fecha de emisión: {fecha_emision} | Generado por: {st.session_state.nombre_actual}", ln=True, align="L"); pdf.ln(4)
    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(241, 245, 249); pdf.set_text_color(8, 23, 84)
    pdf.cell(22, 8, "Folio", 1, 0, "C", True); pdf.cell(60, 8, "Nombre del Proyecto", 1, 0, "L", True); pdf.cell(30, 8, "Área", 1, 0, "L", True); pdf.cell(35, 8, "Responsable", 1, 0, "L", True); pdf.cell(25, 8, "Estatus", 1, 0, "C", True); pdf.cell(18, 8, "Avance", 1, 0, "C", True); pdf.cell(42, 8, "Ult. Actualizacion", 1, 0, "C", True); pdf.cell(45, 8, "Etapa Actual", 1, 1, "L", True)
    pdf.set_font("Arial", "", 8); pdf.set_text_color(40, 40, 40)
    for _, row in dataframe.iterrows():
      pdf.cell(22, 7, str(row["folio"] or "S/F")[:12], 1, 0, "C"); pdf.cell(60, 7, str(row["nombre"] or "")[:35], 1, 0, "L"); pdf.cell(30, 7, str(row["area_negocio"] or "N/A")[:18], 1, 0, "L"); pdf.cell(35, 7, str(row["lider_asignado"] or "Sin Asignar")[:22], 1, 0, "L"); pdf.cell(25, 7, str(row["estatus_tiempo"] or "N/A")[:15], 1, 0, "C"); pdf.cell(18, 7, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, "C"); pdf.set_font("Arial", "B", 8); pdf.cell(42, 7, str(row["ultima_actualizacion"] or "Sin registro")[:19], 1, 0, "C"); pdf.set_font("Arial", "", 8); pdf.cell(45, 7, str(row["etapa_actual"] or "N/A")[:25], 1, 1, "L")
      resumen_txt = str(row["resumen_estatus"] or "").strip()
      if resumen_txt:
        pdf.set_font("Arial", "I", 7); pdf.set_text_color(90, 90, 90)
        pdf.cell(22, 6, "Bitácora:", "BL", 0, "R"); pdf.cell(255, 6, resumen_txt[:150], "BR", 1, "L")
        pdf.set_font("Arial", "", 8); pdf.set_text_color(40, 40, 40)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
      pdf.output(tmp.name); return tmp.name

  with st.sidebar:
    st.write("")
    pdf_path = generar_pdf_ejecutivo(df)
    with open(pdf_path, "rb") as file:
      st.download_button("📥 Descargar Reporte PDF", data=file, file_name=f"Reporte_Portafolio_{datetime.now().strftime('%Y%m%d')}.pdf", use_container_width=True, type="secondary")

# --- PESTAÑAS DINÁMICAS ---
if es_moderador: tabs = st.tabs(["🚀 Seguimiento Operativo", "➕ Nuevo Proyecto", "👥 Control de Accesos"])
else: tabs = st.tabs(["🚀 Seguimiento Operativo", "➕ Nuevo Proyecto"])

lista_lideres_registrados = obtener_lista_usuarios()

# PESTAÑA 1: VISOR + PLAN DE TRABAJO
with tabs[0]:
  st.write("")
  if df.empty:
    st.markdown("""
        <div style='text-align: center; padding: 60px 20px; background-color: #FFFFFF; border-radius: 16px; border: 1px dashed #CBD5E1; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-top: 20px;'>
            <div style='font-size: 3rem; margin-bottom: 15px;'>🗂️</div>
            <h3 style='color: #0F172A; margin-bottom: 10px;'>Tu portafolio está listo para arrancar</h3>
            <p style='color: #64748B; font-size: 1.1rem; max-width: 500px; margin: 0 auto;'>No hay proyectos registrados en la base de datos de la nube. Ve a la pestaña <b>Nuevo Proyecto</b> para crear tu primera iniciativa.</p>
        </div>
    """, unsafe_allow_html=True)
  else:
    st.markdown("<h4 style='color:#0F172A; margin-bottom:15px; font-size: 1rem;'>🔍 Filtros de Búsqueda Avanzada</h4>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    txt_busqueda = f_col1.text_input("Búsqueda Rápida", placeholder="Ej. INC-001 o Banco...")
    filtro_area = f_col2.selectbox("Área del Negocio", ["Todas las Áreas"] + OPCIONES_AREAS)
    filtro_estatus = f_col3.selectbox("Estatus Operativo", ["Todos los Estatus"] + OPCIONES_ESTATUS)
    filtro_lider = f_col4.selectbox("Responsable Asignado", ["Todos los Responsables"] + lista_lideres_registrados)

    df_filtrado = df.copy()
    if txt_busqueda.strip():
      query = txt_busqueda.strip().lower()
      df_filtrado = df_filtrado[df_filtrado["nombre"].str.lower().str.contains(query, na=False) | df_filtrado["folio"].str.lower().str.contains(query, na=False)]
    if filtro_area != "Todas las Áreas": df_filtrado = df_filtrado[df_filtrado["area_negocio"] == filtro_area]
    if filtro_estatus != "Todos los Estatus": df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"] == filtro_estatus]
    if filtro_lider != "Todos los Responsables": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == filtro_lider]

    st.markdown(f"<p style='color: #64748B; font-size: 0.9rem; margin-top: 10px;'>📌 Mostrando <b>{len(df_filtrado)}</b> de <b>{len(df)}</b> iniciativas.</p>", unsafe_allow_html=True)
    
    if df_filtrado.empty:
      st.warning("No se encontraron iniciativas que coincidan con los filtros aplicados.")
    else:
      for _, row in df_filtrado.iterrows():
        p_id = row["id"]
        
        badge_status = "status-gray"
        if row["estatus_tiempo"] == "En tiempo": badge_status = "status-green"
        elif row["estatus_tiempo"] == "Detenido": badge_status = "status-yellow"

        expander_title = f"{row['folio'] or 'S/F'} | {row['nombre']} — Avance: {int((row['avance_real'] or 0)*100)}%"
        
        with st.expander(expander_title):
          st.progress(float(row["avance_real"] or 0.0))

          with st.form(f"update_{p_id}"):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<p style='margin:0; font-size:0.9rem;'><span style='color:#64748B;'>Responsable:</span> <b style='color:#0F172A;'>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
            c2.markdown(f"<p style='margin:0; font-size:0.9rem;'><span style='color:#64748B;'>Estatus:</span> <span class='status-badge {badge_status}'>{row['estatus_tiempo']}</span></p>", unsafe_allow_html=True)
            c3.markdown(f"<p style='margin:0; font-size:0.9rem; text-align:right;'><span style='color:#64748B;'>Últ. Actualización:</span> <b style='color:#05297A;'>{row['ultima_actualizacion'] or 'N/A'}</b></p>", unsafe_allow_html=True)
            st.divider()

            c_form1, c_form2, c_form3 = st.columns(3)
            u_etapa = c_form1.selectbox("Fase Actual", OPCIONES_ETAPAS, index=(OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0))
            u_estatus = c_form2.selectbox("Estado", OPCIONES_ESTATUS, index=(OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0))
            u_avance = c_form3.slider("Progreso Validado (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)

            if es_moderador:
              idx_lider = (lista_lideres_registrados.index(row["lider_asignado"]) if row["lider_asignado"] in lista_lideres_registrados else 0)
              u_lider = st.selectbox("Reasignar Líder de Proyecto", lista_lideres_registrados, index=idx_lider)
            else:
              u_lider = row["lider_asignado"]

            u_resumen = st.text_area("Bitácora de Estatus / Comentarios", row["resumen_estatus"] or "", height=80)

            l1, l2 = st.columns(2)
            u_carpeta = l1.text_input("Repositorio Drive (URL)", row["carpeta_url"] or "")
            u_plan = l2.text_input("Enlace Externo (Opcional)", row["plan_url"] or "")

            st.write("")
            btn1, btn2, btn3 = st.columns([3, 3, 6])
            if btn1.form_submit_button("Actualizar Proyecto", type="primary"):
              ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              engine = obtener_engine()
              with engine.begin() as conn:
                conn.execute(sqlalchemy.text("UPDATE proyectos SET etapa_actual=:e, estatus_tiempo=:s, avance_real=:a, lider_asignado=:l, resumen_estatus=:r, carpeta_url=:c, plan_url=:p, ultima_actualizacion=:u WHERE id=:id"),
                             {"e": u_etapa, "s": u_estatus, "a": u_avance, "l": u_lider, "r": u_resumen, "c": u_carpeta, "p": u_plan, "u": ahora, "id": p_id})
              st.rerun()

            if es_moderador:
              if btn2.form_submit_button("Eliminar", type="secondary"):
                engine = obtener_engine()
                with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM proyectos WHERE id=:id"), {"id": p_id})
                st.rerun()

          # --- PLAN DE TRABAJO (GANTT) ---
          st.markdown("<h4 style='color:#0F172A; margin-top: 20px; padding-top: 20px; border-top: 1px dashed #CBD5E1;'>📅 Cronograma de Tareas (Gantt)</h4>", unsafe_allow_html=True)
          df_tareas = calcular_fechas_tarea(p_id)

          if not df_tareas.empty:
            fig = px.timeline(df_tareas, x_start="fecha_inicio", x_end="fecha_fin", y="nombre_tarea", color="porcentaje_avance", color_continuous_scale=[[0, "#E2E8F0"], [0.5, "#FCD34D"], [1, "#05297A"]], hover_data=["id", "responsable", "predecesoras", "duracion_dias"])
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=250 + (len(df_tareas) * 25), margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_tareas[["id", "nombre_tarea", "responsable", "fecha_inicio", "duracion_dias", "fecha_fin", "predecesoras", "porcentaje_avance"]], use_container_width=True, hide_index=True)
          else:
            st.info("Sin tareas registradas. Agrega una tarea abajo para generar el diagrama de Gantt.")

          with st.expander("➕ Agregar Tarea al Cronograma"):
            with st.form(f"form_tarea_{p_id}", clear_on_submit=True):
              col_t1, col_t2 = st.columns(2)
              t_nombre = col_t1.text_input("Nombre de la Tarea *")
              t_resp = col_t2.selectbox("Responsable de Tarea", lista_lideres_registrados)
              col_t3, col_t4, col_t5 = st.columns(3)
              t_f_inicio = col_t3.date_input("Fecha Inicio estimada")
              t_duracion = col_t4.number_input("Duración (Días hábiles)", min_value=1, value=5)
              t_preds = col_t5.text_input("Predecesoras (IDs ej. 1, 2)")
              if st.form_submit_button("Guardar Tarea en Cronograma", type="primary"):
                if t_nombre.strip():
                  engine = obtener_engine()
                  f_fin_est = pd.to_datetime(t_f_inicio) + timedelta(days=t_duracion - 1)
                  with engine.begin() as conn:
                    conn.execute(sqlalchemy.text("INSERT INTO tareas (proyecto_id, nombre_tarea, responsable, fecha_inicio, duracion_dias, fecha_fin, porcentaje_avance, predecesoras) VALUES (:p_id, :n, :r, :fi, :d, :ff, 0.0, :p)"),
                                 {"p_id": p_id, "n": t_nombre, "r": t_resp, "fi": str(t_f_inicio), "d": t_duracion, "ff": str(f_fin_est.date()), "p": t_preds})
                  st.success("Tarea agregada exitosamente."); st.rerun()
                else: st.error("El nombre de la tarea es obligatorio.")

# PESTAÑA 2: NUEVO PROYECTO
with tabs[1]:
  st.write("")
  if es_moderador:
    with st.form("form_nuevo", clear_on_submit=True):
      st.markdown("<h3 style='color:#0F172A; margin-bottom: 20px;'>Formulario de Alta de Iniciativa</h3>", unsafe_allow_html=True)
      c1, c2, c3 = st.columns(3)
      folio = c1.text_input("Folio Interno")
      nombre = c2.text_input("Nombre de la Iniciativa *")
      lider = c3.selectbox("Líder Asignado *", lista_lideres_registrados)

      c4, c5, c6 = st.columns(3)
      area = c4.selectbox("Área Solicitante", OPCIONES_AREAS)
      tipo = c5.selectbox("Categoría General", OPCIONES_TIPOS)
      subtipo = c6.selectbox("Subcategoría Específica", OPCIONES_SUBTIPOS)

      c7, c8, c9 = st.columns(3)
      gerente = c7.selectbox("Patrocinador (Sponsor)", OPCIONES_GERENTES)
      etapa = c8.selectbox("Fase de Arranque", OPCIONES_ETAPAS)
      estatus_inicial = c9.selectbox("Estado Inicial", OPCIONES_ESTATUS, index=4)

      st.write("")
      if st.form_submit_button("Crear Proyecto", type="primary"):
        if nombre.strip():
          engine = obtener_engine()
          with engine.begin() as conn:
            conn.execute(sqlalchemy.text("INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, 0)"),
                         {"f": folio, "n": nombre, "a": area, "t": tipo, "s": subtipo, "g": gerente, "l": lider, "e": etapa, "st": estatus_inicial})
          st.success("Iniciativa creada en el Portafolio."); st.rerun()
        else: st.error("El Nombre es obligatorio.")
  else:
    st.info("No tienes permisos suficientes. Solo los perfiles 'Moderador' pueden dar de alta nuevos proyectos.")

# PESTAÑA 3: USUARIOS
if es_moderador:
  with tabs[2]:
    st.write("")
    engine = obtener_engine()
    
    # CORRECCIÓN DE COLUMNAS (KEYERROR POSTGRES)
    df_users = pd.read_sql("SELECT nombre, correo, rol FROM usuarios", engine)
    df_users.columns = ["Colaborador", "Correo", "Permisos"]
    
    col_table, col_forms = st.columns([1.5, 1])
    
    with col_table:
        st.markdown("<h4 style='color:#0F172A;'>Directorio Activo</h4>", unsafe_allow_html=True)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    
    with col_forms:
      with st.form("form_alta_usuario", clear_on_submit=True):
        st.markdown("<h4 style='color:#0F172A;'>Crear Credencial</h4>", unsafe_allow_html=True)
        n_nombre = st.text_input("Nombre Completo")
        n_correo = st.text_input("Correo Institucional")
        n_pass = st.text_input("Clave Temporal", type="password")
        n_rol = st.selectbox("Nivel de Permisos", ["Usuario", "Moderador"])
        if st.form_submit_button("Registrar Usuario", type="primary"):
          if n_correo and n_pass and n_nombre:
            try:
              engine = obtener_engine()
              with engine.begin() as conn: conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES (:c, :p, :r, :n)"), {"c": n_correo.strip().lower(), "p": n_pass, "r": n_rol, "n": n_nombre})
              st.success("Cuenta activada."); st.rerun()
            except: st.error("El correo ya existe en el sistema.")
          else: st.warning("Faltan datos obligatorios.")

      with st.form("form_baja_usuario"):
        st.markdown("<h4 style='color:#0F172A; margin-top: 10px;'>Revocar Acceso</h4>", unsafe_allow_html=True)
        lista_correos = df_users["Correo"].tolist()
        if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
        correo_borrar = st.selectbox("Colaborador a dar de baja", ["Seleccionar..."] + lista_correos)
        if st.form_submit_button("Eliminar Cuenta", type="secondary"):
          if correo_borrar != "Seleccionar...":
            engine = obtener_engine()
            with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM usuarios WHERE correo=:c"), {"c": correo_borrar})
            st.success("Cuenta eliminada."); st.rerun()
          else: st.warning("Selecciona una cuenta válida.")
