import io
from datetime import datetime, timedelta
import tempfile
from fpdf import FPDF
import pandas as pd
import plotly.express as px
import sqlalchemy
import streamlit as st

# Intentar importar la librería de IA de Google
try:
  import google.generativeai as genai

  HAS_GEMINI = True
except ImportError:
  HAS_GEMINI = False

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
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #F4F6F9 !important; color: #1E293B !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important; }
    h1, h2, h3, h4, h5, h6 { color: #0F172A !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    label { color: #334155 !important; font-weight: 600 !important; font-size: 0.85rem !important; text-transform: uppercase; letter-spacing: 0.03em; }
    .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div { border-radius: 8px !important; border: 1px solid #CBD5E1 !important; background-color: #F8FAFC !important; transition: all 0.2s ease; }
    .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within { border-color: #05297A !important; box-shadow: 0 0 0 2px rgba(5, 41, 122, 0.2) !important; background-color: #FFFFFF !important; }
    div[data-testid="stFormSubmitButton"] button, .stButton > button[kind="primary"] { background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 0.5rem 1rem !important; box-shadow: 0 4px 6px -1px rgba(28, 66, 232, 0.2) !important; transition: all 0.3s ease !important; }
    div[data-testid="stFormSubmitButton"] button:hover, .stButton > button[kind="primary"]:hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(28, 66, 232, 0.3) !important; }
    button[data-testid="baseButton-secondary"], .stButton > button[kind="secondary"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; color: #334155 !important; border-radius: 8px !important; font-weight: 500 !important; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important; transition: all 0.2s ease !important; }
    button[data-testid="baseButton-secondary"]:hover, .stButton > button[kind="secondary"]:hover { border-color: #0F172A !important; color: #0F172A !important; background-color: #F8FAFC !important; }
    .stButton > button[kind="primary"] p { color: #FFFFFF !important; } .stButton > button[kind="secondary"] p { color: inherit !important; }
    div[data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-top: 4px solid #05297A !important; padding: 20px 24px !important; border-radius: 12px !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; }
    div[data-testid="metric-container"] label { color: #64748B !important; font-size: 0.85rem !important; font-weight: 600 !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] div { color: #0F172A !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -0.02em; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #E2E8F0; padding-bottom: 0px; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #05297A !important; font-weight: 700 !important; color: #05297A !important; background-color: transparent !important; }
    .stTabs [aria-selected="false"] { color: #64748B !important; font-weight: 500 !important; }
    .streamlit-expanderHeader { background-color: #FFFFFF !important; color: #0F172A !important; font-weight: 600 !important; border-radius: 12px !important; border: 1px solid #E2E8F0 !important; padding: 1rem !important; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important; }
    .streamlit-expanderContent { border: 1px solid #E2E8F0 !important; border-top: none !important; background-color: #FFFFFF !important; padding: 24px !important; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.02em; display: inline-block; }
    .status-green { background-color: #DCFCE7; color: #166534 !important; border: 1px solid #BBF7D0;}
    .status-yellow { background-color: #FEF9C3; color: #854D0E !important; border: 1px solid #FEF08A;}
    .status-gray { background-color: #F1F5F9; color: #475569 !important; border: 1px solid #E2E8F0;}
    
    /* Kanban CSS */
    .kanban-card { background: #FFFFFF; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; border-left: 4px solid #05297A; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 15px; transition: transform 0.2s;}
    .kanban-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .kanban-title { font-weight: 700; color: #0F172A; font-size: 0.95rem; margin-bottom: 8px; line-height: 1.2; }
    .kanban-meta { font-size: 0.8rem; color: #64748B; margin-bottom: 4px;}
    
    /* Timeline CSS */
    .timeline-item { border-left: 2px solid #CBD5E1; padding-left: 15px; margin-bottom: 15px; position: relative; }
    .timeline-item::before { content: ''; position: absolute; left: -6px; top: 0; width: 10px; height: 10px; border-radius: 50%; background: #05297A; }
    .timeline-date { font-size: 0.75rem; color: #64748B; font-weight: 600; margin-bottom: 2px; }
    .timeline-text { font-size: 0.85rem; color: #1E293B; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONSTANTES ---
OPCIONES_AREAS = [
    "Incentivos",
    "Afore",
    "Banca Empresarial",
    "Banco",
    "CAT Cobranza",
    "CAT P&V",
    "CEDIS",
    "Cobranza Domiciliaria",
    "Credito Automotriz",
    "Inmobiliaria",
    "Retail",
    "Sale Vale",
]
OPCIONES_TIPOS = [
    "Esquema de Incentivos",
    "Tecnología",
    "Estratégicos",
    "Procesos",
    "Campañas",
    "Auditorías",
]
OPCIONES_SUBTIPOS = [
    "EI-Nuevo incentivo completo",
    "EI-Actualización completa de incentivo",
    "EI-Ajuste menor de incentivo",
    "EI-Ajuste mayor de incentivo",
    "EI-Casos especiales",
    "CA-Campaña",
    "CA-Concurso",
    "PR-Documentación oficial",
    "PR-Nuevo proceso",
    "TE-Software",
    "TE-Tableros",
    "Otros",
]
OPCIONES_ETAPAS = [
    "1. Diseño (EI)",
    "2. Prueba piloto (EI)",
    "3. Escalamiento nacional (EI)",
    "4. Cierre (EI)",
    "1. Diseño (CA)",
    "2. Implementación (CA)",
    "3. Evaluación y cierre (CA)",
    "4. Cierre (CA)",
    "1. Planeación",
    "2. Ejecución",
    "3. Cierre",
]
OPCIONES_ESTATUS = [
    "Por iniciar",
    "En tiempo",
    "Retrasado",
    "Detenido",
    "Cancelado",
]
OPCIONES_GERENTES = [
    "Andres Avila",
    "Eduardo Rodriguez",
    "Heriberto Vega",
    "Janik Orozco",
    "Kurokusi Ochoa",
    "Noel Aquino",
    "Yahir Ramirez",
    "Giovanni Vallejo",
    "Ruben Rivera",
]


# --- BASE DE DATOS ---
def obtener_engine():
  db_url = (
      st.secrets["postgres"]["url"]
      if "postgres" in st.secrets
      else "sqlite:///db_coppel_v5.db"
  )
  return sqlalchemy.create_engine(db_url)


def inicializar_db():
  engine = obtener_engine()
  with engine.begin() as conn:
    conn.execute(
        sqlalchemy.text("""CREATE TABLE IF NOT EXISTS proyectos (id SERIAL
        PRIMARY KEY, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT,
        tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT,
        etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus
        TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT)""")
    )
    conn.execute(
        sqlalchemy.text("""CREATE TABLE IF NOT EXISTS usuarios (correo TEXT
        PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)""")
    )
    conn.execute(
        sqlalchemy.text("""CREATE TABLE IF NOT EXISTS tareas (id SERIAL PRIMARY
        KEY, proyecto_id INTEGER, nombre_tarea TEXT NOT NULL, responsable TEXT,
        fecha_inicio TEXT, duracion_dias INTEGER, fecha_fin TEXT,
        porcentaje_avance REAL, predecesoras TEXT)""")
    )
    conn.execute(
        sqlalchemy.text("""CREATE TABLE IF NOT EXISTS bitacora (id SERIAL
        PRIMARY KEY, proyecto_id INTEGER, usuario_nombre TEXT, fecha_hora TEXT,
        comentario TEXT)""")
    )

    res = conn.execute(
        sqlalchemy.text("SELECT COUNT(*) FROM usuarios")
    ).fetchone()
    if res[0] == 0:
      conn.execute(
          sqlalchemy.text(
              "INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com',"
              " 'Coppel2026', 'Moderador', 'Leonardo Castillo')"
          )
      )
      conn.execute(
          sqlalchemy.text(
              "INSERT INTO usuarios VALUES ('ivan.salazar@coppel.com',"
              " 'Coppel2026', 'Usuario', 'Oscar Ivan Salazar')"
          )
      )


inicializar_db()


def obtener_lista_usuarios():
  engine = obtener_engine()
  df = pd.read_sql("SELECT nombre FROM usuarios ORDER BY nombre ASC", engine)
  return (
      df["nombre"].tolist()
      if not df.empty
      else ["Leonardo Castillo", "Oscar Ivan Salazar"]
  )


def calcular_fechas_tarea(proyecto_id):
  engine = obtener_engine()
  df_t = pd.read_sql(
      f"SELECT * FROM tareas WHERE proyecto_id = {proyecto_id} ORDER BY id ASC",
      engine,
  )
  if df_t.empty:
    return df_t
  df_t["fecha_inicio"] = pd.to_datetime(df_t["fecha_inicio"])
  df_t["fecha_fin"] = pd.to_datetime(df_t["fecha_fin"])
  fechas_fin = {}
  for idx, row in df_t.iterrows():
    t_id = row["id"]
    preds = str(row["predecesoras"]).strip() if row["predecesoras"] else ""
    if preds:
      pred_ids = [
          int(p.strip())
          for p in preds.split(",")
          if p.strip().isdigit() and int(p.strip()) in fechas_fin
      ]
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
  st.session_state.autenticado = False
  st.session_state.correo_actual = None
  st.session_state.nombre_actual = None
  st.session_state.rol = None

if not st.session_state.autenticado:
  col_izq, col_centro, col_der = st.columns([1, 1.2, 1])
  with col_centro:
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        "<h1 style='text-align: center; color:#05297A !important; font-size:"
        " 2.5rem; letter-spacing: -1px;'>Portafolio de Incentivos</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #64748B; margin-bottom: 40px;"
        " font-size: 1.1rem;'>Coppel Corporativo</p>",
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
      st.markdown(
          "<h3 style='color:#0F172A !important; font-size: 1.2rem;"
          " margin-bottom: 20px;'>Acceso al Sistema</h3>",
          unsafe_allow_html=True,
      )
      correo_input = st.text_input(
          "Correo Corporativo", placeholder="tu.nombre@coppel.com"
      )
      password_input = st.text_input("Contraseña", type="password")
      st.write("")
      if st.form_submit_button(
          "Ingresar de forma segura", type="primary", use_container_width=True
      ):
        if correo_input.strip() == "":
          st.warning("El correo es requerido.")
        else:
          engine = obtener_engine()
          with engine.connect() as conn:
            res = conn.execute(
                sqlalchemy.text(
                    "SELECT password, rol, nombre FROM usuarios WHERE"
                    " LOWER(correo)=:c"
                ),
                {"c": correo_input.strip().lower()},
            ).fetchone()
            if res and res[0] == password_input:
              st.session_state.autenticado = True
              st.session_state.correo_actual = correo_input.strip().lower()
              st.session_state.rol = res[1]
              st.session_state.nombre_actual = res[2]
              st.rerun()
            else:
              st.error("Credenciales incorrectas.")
  st.stop()

# --- DATOS GLOBALES ---
engine = obtener_engine()
df = pd.read_sql("SELECT * FROM proyectos", engine)
df_bitacora = pd.read_sql("SELECT * FROM bitacora ORDER BY id DESC", engine)
es_moderador = st.session_state.rol == "Moderador"

# --- ALERTAS INTELIGENTES ---
if not df.empty:
  proyectos_retrasados = df[df["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
  if not proyectos_retrasados.empty and "alerta_mostrada" not in st.session_state:
    st.toast(
        f"Tienes {len(proyectos_retrasados)} iniciativas requiriendo atención"
        " urgente.",
        icon="🚨",
    )
    st.session_state.alerta_mostrada = True

# --- SIDEBAR MEJORADO ---
with st.sidebar:
  st.markdown(
      f"<div style='background-color:#F8FAFC; padding: 20px; border-radius:"
      " 12px; border: 1px solid #E2E8F0; margin-bottom: 20px;'><h3"
      " style='margin:0 0 5px 0; font-size:1.1rem; color:#0F172A;'>👤"
      f" {st.session_state.nombre_actual}</h3><p style='margin:0 0 10px 0;"
      f" color:#64748B; font-size:0.8rem;'>{st.session_state.correo_actual}</p><span"
      " class='status-badge"
      f" {'status-green' if es_moderador else 'status-gray'}'>{st.session_state.rol}</span></div>",
      unsafe_allow_html=True,
  )

  with st.expander("⚙️ Configuración de Seguridad", expanded=False):
    with st.form("form_cambio_pass"):
      nueva_pass = st.text_input("Nueva Contraseña", type="password")
      confirmar_pass = st.text_input("Confirmar", type="password")
      if st.form_submit_button("Actualizar Clave", use_container_width=True):
        if nueva_pass == confirmar_pass and nueva_pass:
          with engine.begin() as conn:
            conn.execute(
                sqlalchemy.text(
                    "UPDATE usuarios SET password=:p WHERE correo=:c"
                ),
                {"p": nueva_pass, "c": st.session_state.correo_actual},
            )
          st.success("Guardado.")
        else:
          st.error("No coinciden.")
  st.write("")

  # DESCARGAS
  st.markdown(
      "<h4 style='color:#0F172A; font-size: 0.9rem;'>📥 Exportar"
      " Información</h4>",
      unsafe_allow_html=True,
  )
  if not df.empty:

    def generar_pdf(dataframe):
      pdf = FPDF(orientation="L", unit="mm", format="A4")
      pdf.set_auto_page_break(auto=True, margin=15)
      pdf.add_page()
      pdf.set_font("Arial", "B", 16)
      pdf.set_text_color(5, 41, 122)
      pdf.cell(
          0, 8, "Reporte Ejecutivo de Portafolio", ln=True, align="L"
      )
      pdf.set_font("Arial", "", 9)
      pdf.set_text_color(100, 100, 100)
      pdf.cell(
          0,
          6,
          f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
          ln=True,
          align="L",
      )
      pdf.ln(4)
      pdf.set_font("Arial", "B", 8)
      pdf.set_fill_color(241, 245, 249)
      pdf.set_text_color(8, 23, 84)
      pdf.cell(22, 8, "Folio", 1, 0, "C", True)
      pdf.cell(60, 8, "Nombre del Proyecto", 1, 0, "L", True)
      pdf.cell(30, 8, "Área", 1, 0, "L", True)
      pdf.cell(35, 8, "Responsable", 1, 0, "L", True)
      pdf.cell(25, 8, "Estatus", 1, 0, "C", True)
      pdf.cell(18, 8, "Avance", 1, 0, "C", True)
      pdf.cell(42, 8, "Ult. Act.", 1, 0, "C", True)
      pdf.cell(45, 8, "Etapa Actual", 1, 1, "L", True)
      pdf.set_font("Arial", "", 8)
      pdf.set_text_color(40, 40, 40)
      for _, row in dataframe.iterrows():
        pdf.cell(22, 7, str(row["folio"])[:12], 1, 0, "C")
        pdf.cell(60, 7, str(row["nombre"])[:35], 1, 0, "L")
        pdf.cell(30, 7, str(row["area_negocio"])[:18], 1, 0, "L")
        pdf.cell(35, 7, str(row["lider_asignado"])[:22], 1, 0, "L")
        pdf.cell(25, 7, str(row["estatus_tiempo"])[:15], 1, 0, "C")
        pdf.cell(
            18, 7, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, "C"
        )
        pdf.set_font("Arial", "B", 8)
        pdf.cell(42, 7, str(row["ultima_actualizacion"])[:19], 1, 0, "C")
        pdf.set_font("Arial", "", 8)
        pdf.cell(45, 7, str(row["etapa_actual"])[:25], 1, 1, "L")
      with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

    with open(generar_pdf(df), "rb") as file:
      st.download_button(
          "Descargar Reporte PDF",
          data=file,
          file_name=f"Reporte_{datetime.now().strftime('%Y%m%d')}.pdf",
          use_container_width=True,
          type="secondary",
      )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
      df.to_excel(writer, index=False, sheet_name="Proyectos")
    st.download_button(
        "Descargar Base (Excel)",
        data=excel_buffer.getvalue(),
        file_name=f"Base_Datos_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
        type="secondary",
    )

  st.write("")
  if st.button("Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# --- HEADER Y MÉTRICAS PERMANENTES ---
st.markdown(
    "<h2 style='margin-bottom: 25px; color:#0F172A;'>📊 Visión General del"
    " Portafolio</h2>",
    unsafe_allow_html=True,
)
if not df.empty and not proyectos_retrasados.empty:
  st.markdown(
      "<div style='background-color:#FEF2F2; border-left: 4px solid #EF4444;"
      " padding: 15px; border-radius: 8px; margin-bottom: 20px;'><p"
      " style='color:#991B1B; margin:0; font-weight:600;'>⚠️ Atención Crítica:"
      f" Tienes {len(proyectos_retrasados)} proyectos marcados como Retrasados"
      " o Detenidos.</p></div>",
      unsafe_allow_html=True,
  )

total_p = len(df)
en_t = len(df[df["estatus_tiempo"] == "En tiempo"]) if total_p > 0 else 0
ret = len(proyectos_retrasados) if total_p > 0 else 0
prom = df["avance_real"].mean() * 100 if total_p > 0 else 0.0
m1, m2, m3, m4 = st.columns(4)
m1.metric("INICIATIVAS ACTIVAS", total_p)
m2.metric("EJECUCIÓN EN TIEMPO", en_t)
m3.metric("EN RIESGO / RETRASO", ret)
m4.metric("AVANCE GLOBAL", f"{prom:.1f}%")
st.write("")

# --- PESTAÑAS (TABS) ---
if es_moderador:
  tabs = st.tabs([
      "📈 Dashboard Analítico",
      "🚀 Seguimiento",
      "📋 Kanban",
      "🤖 Copiloto IA",
      "➕ Nuevo Proyecto",
      "👥 Accesos",
  ])
else:
  tabs = st.tabs([
      "📈 Dashboard Analítico",
      "🚀 Seguimiento",
      "📋 Kanban",
      "🤖 Copiloto IA",
      "➕ Nuevo Proyecto",
  ])
lista_lideres_registrados = obtener_lista_usuarios()

# PESTAÑA 1: DASHBOARD ANALÍTICO
with tabs[0]:
  st.write("")
  if df.empty:
    st.info("Sin datos suficientes para generar gráficos. Agrega proyectos.")
  else:
    d_col1, d_col2 = st.columns(2)
    with d_col1:
      fig1 = px.pie(
          df,
          names="area_negocio",
          title="Distribución por Área del Negocio",
          hole=0.4,
          color_discrete_sequence=px.colors.qualitative.Prism,
      )
      fig1.update_layout(
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
      )
      st.plotly_chart(fig1, use_container_width=True)
    with d_col2:
      df_status_count = df["estatus_tiempo"].value_counts().reset_index()
      df_status_count.columns = ["Estatus", "Cantidad"]
      fig2 = px.bar(
          df_status_count,
          x="Estatus",
          y="Cantidad",
          title="Salud del Portafolio",
          color="Estatus",
          color_discrete_map={
              "En tiempo": "#166534",
              "Retrasado": "#475569",
              "Detenido": "#854D0E",
              "Por iniciar": "#94A3B8",
          },
      )
      fig2.update_layout(
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
      )
      st.plotly_chart(fig2, use_container_width=True)

# PESTAÑA 2: SEGUIMIENTO OPERATIVO
with tabs[1]:
  if df.empty:
    st.info("El portafolio está vacío.")
  else:
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    txt_busqueda = f_col1.text_input(
        "Búsqueda Rápida", placeholder="Ej. INC-001 o Banco..."
    )
    filtro_area = f_col2.selectbox(
        "Área del Negocio", ["Todas las Áreas"] + OPCIONES_AREAS
    )
    filtro_estatus = f_col3.selectbox(
        "Estatus Operativo", ["Todos los Estatus"] + OPCIONES_ESTATUS
    )
    filtro_lider = f_col4.selectbox(
        "Responsable Asignado",
        ["Todos los Responsables"] + lista_lideres_registrados,
    )

    df_filtrado = df.copy()
    if txt_busqueda.strip():
      df_filtrado = df_filtrado[
          df_filtrado["nombre"]
          .str.lower()
          .str.contains(txt_busqueda.lower(), na=False)
          | df_filtrado["folio"]
          .str.lower()
          .str.contains(txt_busqueda.lower(), na=False)
      ]
    if filtro_area != "Todas las Áreas":
      df_filtrado = df_filtrado[df_filtrado["area_negocio"] == filtro_area]
    if filtro_estatus != "Todos los Estatus":
      df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"] == filtro_estatus]
    if filtro_lider != "Todos los Responsables":
      df_filtrado = df_filtrado[
          df_filtrado["lider_asignado"] == filtro_lider
      ]

    st.markdown(
        f"<p style='color: #64748B; font-size: 0.9rem; margin-top: 10px;'>📌"
        f" Mostrando <b>{len(df_filtrado)}</b> iniciativas.</p>",
        unsafe_allow_html=True,
    )

    for _, row in df_filtrado.iterrows():
      p_id = row["id"]
      badge_status = (
          "status-green"
          if row["estatus_tiempo"] == "En tiempo"
          else (
              "status-yellow"
              if row["estatus_tiempo"] == "Detenido"
              else "status-gray"
          )
      )

      with st.expander(
          f"{row['folio'] or 'S/F'} | {row['nombre']} — Avance:"
          f" {int((row['avance_real'] or 0)*100)}%"
      ):
        st.progress(float(row["avance_real"] or 0.0))

        with st.form(f"update_{p_id}"):
          c1, c2, c3 = st.columns(3)
          c1.markdown(
              f"<p style='margin:0; font-size:0.9rem;'><span"
              f" style='color:#64748B;'>Responsable:</span> <b"
              f" style='color:#0F172A;'>{row['lider_asignado']}</b></p>",
              unsafe_allow_html=True,
          )
          c2.markdown(
              f"<p style='margin:0; font-size:0.9rem;'><span"
              " style='color:#64748B;'>Estatus:</span> <span"
              f" class='status-badge {badge_status}'>{row['estatus_tiempo']}</span></p>",
              unsafe_allow_html=True,
          )
          c3.markdown(
              f"<p style='margin:0; font-size:0.9rem; text-align:right;'><span"
              " style='color:#64748B;'>Últ. Actualización:</span> <b"
              f" style='color:#05297A;'>{row['ultima_actualizacion'] or 'N/A'}</b></p>",
              unsafe_allow_html=True,
          )
          st.divider()

          c_form1, c_form2, c_form3 = st.columns(3)
          u_etapa = c_form1.selectbox(
              "Fase Actual",
              OPCIONES_ETAPAS,
              index=(
                  OPCIONES_ETAPAS.index(row["etapa_actual"])
                  if row["etapa_actual"] in OPCIONES_ETAPAS
                  else 0
              ),
          )
          u_estatus = c_form2.selectbox(
              "Estado",
              OPCIONES_ESTATUS,
              index=(
                  OPCIONES_ESTATUS.index(row["estatus_tiempo"])
                  if row["estatus_tiempo"] in OPCIONES_ESTATUS
                  else 0
              ),
          )
          u_avance = c_form3.slider(
              "Progreso Validado (%)",
              0.0,
              1.0,
              float(row["avance_real"] or 0.0),
              0.05,
          )
          u_lider = (
              st.selectbox(
                  "Reasignar Líder de Proyecto",
                  lista_lideres_registrados,
                  index=(
                      lista_lideres_registrados.index(row["lider_asignado"])
                      if row["lider_asignado"] in lista_lideres_registrados
                      else 0
                  ),
              )
              if es_moderador
              else row["lider_asignado"]
          )

          st.markdown(
              "<p style='font-size:0.85rem; font-weight:600; color:#334155;"
              " margin-bottom:5px;'>NUEVO COMENTARIO DE BITÁCORA</p>",
              unsafe_allow_html=True,
          )
          u_comentario = st.text_input(
              "Agregar actualización (Se guardará en el historial)",
              placeholder="Escribe el estatus de la semana...",
          )

          l1, l2 = st.columns(2)
          u_carpeta = l1.text_input(
              "Repositorio Drive (URL)", row["carpeta_url"] or ""
          )
          u_plan = l2.text_input(
              "Enlace Externo (Opcional)", row["plan_url"] or ""
          )

          st.write("")
          btn1, btn2, btn3 = st.columns([3, 3, 6])
          if btn1.form_submit_button("Actualizar Proyecto", type="primary"):
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with engine.begin() as conn:
              conn.execute(
                  sqlalchemy.text("""UPDATE proyectos SET etapa_actual=:e, estatus_tiempo=:s, avance_real=:a, 
                                            lider_asignado=:l, carpeta_url=:c, plan_url=:p, ultima_actualizacion=:u WHERE id=:id"""),
                  {
                      "e": u_etapa,
                      "s": u_estatus,
                      "a": u_avance,
                      "l": u_lider,
                      "c": u_carpeta,
                      "p": u_plan,
                      "u": ahora,
                      "id": p_id,
                  },
              )
              if u_comentario.strip():
                conn.execute(
                    sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) 
                                                VALUES (:p_id, :usr, :fh, :com)"""),
                    {
                        "p_id": p_id,
                        "usr": st.session_state.nombre_actual,
                        "fh": ahora,
                        "com": u_comentario.strip(),
                    },
                )
            st.rerun()

          if es_moderador and btn2.form_submit_button(
              "Eliminar", type="secondary"
          ):
            with engine.begin() as conn:
              conn.execute(
                  sqlalchemy.text("DELETE FROM proyectos WHERE id=:id"),
                  {"id": p_id},
              )
            st.rerun()

        historial_proyecto = df_bitacora[df_bitacora["proyecto_id"] == p_id]
        if not historial_proyecto.empty:
          st.markdown(
              "<h5 style='margin-top: 15px; color:#0F172A;'>📜 Historial de"
              " Cambios</h5>",
              unsafe_allow_html=True,
          )
          for _, h_row in historial_proyecto.iterrows():
            st.markdown(
                f"<div class='timeline-item'><div"
                f" class='timeline-date'>{h_row['fecha_hora']} | Por"
                f" {h_row['usuario_nombre']}</div><div"
                f" class='timeline-text'>{h_row['comentario']}</div></div>",
                unsafe_allow_html=True,
            )
        else:
          st.caption("No hay comentarios en el historial aún.")

        st.markdown(
            "<h4 style='color:#0F172A; margin-top: 20px; padding-top: 20px;"
            " border-top: 1px dashed #CBD5E1;'>📅 Cronograma de Tareas"
            " (Gantt)</h4>",
            unsafe_allow_html=True,
        )
        df_tareas = calcular_fechas_tarea(p_id)
        if not df_tareas.empty:
          fig = px.timeline(
              df_tareas,
              x_start="fecha_inicio",
              x_end="fecha_fin",
              y="nombre_tarea",
              color="porcentaje_avance",
              color_continuous_scale=[
                  [0, "#E2E8F0"],
                  [0.5, "#FCD34D"],
                  [1, "#05297A"],
              ],
              hover_data=["responsable"],
          )
          fig.update_yaxes(autorange="reversed")
          fig.update_layout(
              height=200 + (len(df_tareas) * 20),
              margin=dict(l=0, r=0, t=10, b=0),
          )
          st.plotly_chart(fig, use_container_width=True)
        else:
          st.info("Sin tareas registradas.")

        with st.expander("➕ Agregar Tarea"):
          with st.form(f"ft_{p_id}", clear_on_submit=True):
            t_nom = st.text_input("Nombre Tarea *")
            c_t1, c_t2, c_t3, c_t4 = st.columns(4)
            t_res = c_t1.selectbox("Responsable", lista_lideres_registrados)
            t_ini = c_t2.date_input("Inicio")
            t_dur = c_t3.number_input("Días", 1, value=5)
            t_pre = c_t4.text_input("Predecesoras (Ej. 1, 2)")
            if st.form_submit_button("Guardar Tarea"):
              if t_nom.strip():
                with engine.begin() as conn:
                  conn.execute(
                      sqlalchemy.text("""INSERT INTO tareas (proyecto_id, nombre_tarea, responsable, fecha_inicio, duracion_dias, fecha_fin, porcentaje_avance, predecesoras) 
                                                VALUES (:pid, :n, :r, :fi, :d, :ff, 0.0, :p)"""),
                      {
                          "pid": p_id,
                          "n": t_nom,
                          "r": t_res,
                          "fi": str(t_ini),
                          "d": t_dur,
                          "ff": str(
                              pd.to_datetime(t_ini) + timedelta(days=t_dur - 1)
                          ),
                          "p": t_pre,
                      },
                  )
                st.rerun()

# PESTAÑA 3: VISTA KANBAN
with tabs[2]:
  st.write("")
  if df.empty:
    st.info("Agrega proyectos para verlos en el tablero Kanban.")
  else:
    k_cols = st.columns(len(OPCIONES_ESTATUS))
    for i, status in enumerate(OPCIONES_ESTATUS):
      with k_cols[i]:
        st.markdown(
            f"<div style='background-color:#F8FAFC; padding:10px;"
            " border-radius:8px; border:1px solid #E2E8F0; text-align:center;"
            " font-weight:700; color:#0F172A;"
            f" margin-bottom:15px;'>{status.upper()}</div>",
            unsafe_allow_html=True,
        )
        df_k = df[df["estatus_tiempo"] == status]
        for _, k_row in df_k.iterrows():
          st.markdown(
              f"""
                        <div class='kanban-card'>
                            <div class='kanban-title'>{k_row['nombre']}</div>
                            <div class='kanban-meta'>👤 {k_row['lider_asignado']}</div>
                            <div class='kanban-meta'>📈 {int((k_row['avance_real'] or 0)*100)}% Completado</div>
                            <div class='kanban-meta' style='margin-top:8px;'><i>Folio: {k_row['folio'] or 'S/F'}</i></div>
                        </div>
                    """,
              unsafe_allow_html=True,
          )

# PESTAÑA 4: ASISTENTE DE IA (COPILOTO GEMINI)
with tabs[3]:
  st.write("")
  st.markdown(
      "<h3 style='color:#0F172A; margin-bottom: 5px;'>🤖 Copiloto de Inteligencia"
      " Artificial</h3>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color:#64748B; font-size:0.95rem; margin-bottom:20px;'>Pregunta"
      " en lenguaje natural sobre retrasos, estado de proyectos, áreas o"
      " desempeño del equipo.</p>",
      unsafe_allow_html=True,
  )

  api_key_gemini = (
      st.secrets.get("GEMINI_API_KEY", None)
      or st.secrets.get("gemini", {}).get("api_key", None)
      if "gemini" in st.secrets or "GEMINI_API_KEY" in st.secrets
      else None
  )

  if not api_key_gemini and HAS_GEMINI:
    api_key_gemini = st.text_input(
        "🔑 Ingresa tu Gemini API Key para activar la IA:", type="password"
    )

  if HAS_GEMINI and api_key_gemini:
    try:
      genai.configure(api_key=api_key_gemini)

      if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

      for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
          st.markdown(message["content"])

      if user_query := st.chat_input(
          "Ej: ¿Cuáles son los proyectos retrasados y quién es el"
          " responsable?"
      ):
        st.session_state.chat_history.append(
            {"role": "user", "content": user_query}
        )
        with st.chat_message("user"):
          st.markdown(user_query)

        # Contexto estructurado en tiempo real del portafolio
        contexto_proyectos = df[[
            "folio",
            "nombre",
            "area_negocio",
            "lider_asignado",
            "etapa_actual",
            "estatus_tiempo",
            "avance_real",
        ]].to_string(index=False)
        system_instruction = f"""
                Eres el Asistente Inteligente Ejecutivo del Portafolio de Incentivos Coppel.
                Responde con precisión, profesionalismo y brevedad utilizando la base de datos real del portafolio:
                
                DATOS ACTUALES DEL PORTAFOLIO:
                {contexto_proyectos}
                """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"{system_instruction}\n\nPregunta del Usuario: {user_query}"
        )

        with st.chat_message("assistant"):
          st.markdown(response.text)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response.text}
        )

    except Exception as e:
      st.error(f"Error en la conexión con la IA: {e}")
  else:
    st.info(
        "💡 Para habilitar el Copiloto de IA, añade `GEMINI_API_KEY ="
        " 'tu_clave'` en los **Secrets** de Streamlit Cloud o pégala en el"
        " campo de texto superior."
    )

# PESTAÑA 5: NUEVO PROYECTO
idx_tab_nuevo = 4 if es_moderador else 4
with tabs[idx_tab_nuevo]:
  st.write("")
  if es_moderador:
    with st.form("f_nuevo", clear_on_submit=True):
      st.markdown("<h3>Formulario de Alta</h3>", unsafe_allow_html=True)
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
      estatus_inicial = c9.selectbox(
          "Estado Inicial", OPCIONES_ESTATUS, index=0
      )
      if st.form_submit_button("Crear Proyecto", type="primary"):
        if nombre.strip():
          with engine.begin() as conn:
            conn.execute(
                sqlalchemy.text("""INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) 
                                        VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, 0)"""),
                {
                    "f": folio,
                    "n": nombre,
                    "a": area,
                    "t": tipo,
                    "s": subtipo,
                    "g": gerente,
                    "l": lider,
                    "e": etapa,
                    "st": estatus_inicial,
                },
            )
          st.success("Iniciativa creada.")
          st.rerun()
        else:
          st.error("Nombre obligatorio.")

# PESTAÑA 6: USUARIOS (Solo Moderador)
if es_moderador:
  with tabs[5]:
    st.write("")
    df_users = pd.read_sql(
        "SELECT nombre, correo, rol FROM usuarios ORDER BY nombre ASC", engine
    )
    df_users.columns = ["Colaborador", "Correo", "Permisos"]

    col_table, col_forms = st.columns([1.5, 1])
    with col_table:
      st.markdown("<h4>Directorio Activo</h4>", unsafe_allow_html=True)
      st.dataframe(df_users, use_container_width=True, hide_index=True)

    with col_forms:
      with st.form("f_alta"):
        st.markdown("<h4>Crear Credencial</h4>", unsafe_allow_html=True)
        n_nom = st.text_input("Nombre Completo")
        n_cor = st.text_input("Correo Institucional")
        n_pas = st.text_input("Clave Temporal", type="password")
        n_rol = st.selectbox("Permisos", ["Usuario", "Moderador"])
        if st.form_submit_button("Registrar Usuario", type="primary"):
          if n_cor and n_pas and n_nom:
            try:
              with engine.begin() as conn:
                conn.execute(
                    sqlalchemy.text(
                        "INSERT INTO usuarios VALUES (:c, :p, :r, :n)"
                    ),
                    {
                        "c": n_cor.strip().lower(),
                        "p": n_pas,
                        "r": n_rol,
                        "n": n_nom,
                    },
                )
              st.rerun()
            except:
              st.error("El correo ya existe.")

      with st.form("f_baja"):
        lista_correos = df_users["Correo"].tolist()
        if st.session_state.correo_actual in lista_correos:
          lista_correos.remove(st.session_state.correo_actual)
        correo_borrar = st.selectbox(
            "Colaborador a dar de baja", ["Seleccionar..."] + lista_correos
        )
        if st.form_submit_button("Eliminar Cuenta", type="secondary"):
          if correo_borrar != "Seleccionar...":
            with engine.begin() as conn:
              conn.execute(
                  sqlalchemy.text("DELETE FROM usuarios WHERE correo=:c"),
                  {"c": correo_borrar},
              )
            st.rerun()
