import io
from datetime import datetime, timedelta
import tempfile
from fpdf import FPDF
import pandas as pd
import plotly.express as px
import sqlalchemy
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Heading 360 | Executive Steering Engine",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- AVATARES Y ASSETS ---
URL_ROBOT = "https://cdn-icons-png.flaticon.com/512/8943/8943377.png" 
URL_USER = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# --- CSS ENTERPRISE SAAS / PERFECT SYMMETRY UX ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
        background-color: #F8FAFC !important; 
        color: #0F172A !important; 
    }
    
    /* SIDEBAR MODERNO */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0 !important; 
        box-shadow: 4px 0 24px rgba(15, 23, 42, 0.02) !important;
    }
    
    /* ENCABEZADOS Y JERARQUÍA */
    h1, h2, h3, h4, h5, h6 { 
        color: #0F172A !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.02em !important; 
    }
    
    label { 
        color: #64748B !important; 
        font-weight: 600 !important; 
        font-size: 0.75rem !important; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
    }
    
    /* TARJETAS KPI EXECUTIVE */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-num {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
        letter-spacing: -0.03em;
    }
    
    /* INPUTS Y FORMULARIOS ELEGANTES */
    .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div, .stNumberInput > div > div, .stDateInput > div > div { 
        border-radius: 10px !important; 
        border: 1px solid #CBD5E1 !important; 
        background-color: #FFFFFF !important; 
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within { 
        border-color: #2563EB !important; 
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important; 
    }
    
    /* TARJETAS DE FORMULARIOS UNIFICADAS */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02) !important;
        padding: 20px !important;
    }

    /* ACORDEONES LIMPIOS */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02) !important;
        margin-bottom: 12px !important;
    }
    
    /* BOTONES PRIMARIOS Y SECUNDARIOS */
    div[data-testid="stFormSubmitButton"] button, .stButton > button[kind="primary"] { 
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important; 
        color: #FFFFFF !important; 
        border: none !important; 
        border-radius: 10px !important; 
        font-weight: 600 !important; 
        padding: 0.5rem 1.2rem !important; 
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important; 
    }
    
    button[data-testid="baseButton-secondary"], .stButton > button[kind="secondary"] { 
        background-color: #FFFFFF !important; 
        border: 1px solid #CBD5E1 !important; 
        color: #334155 !important; 
        border-radius: 10px !important; 
        font-weight: 600 !important; 
    }
    
    /* BADGES DE ESTADO ESTILIZADOS */
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; display: inline-block; letter-spacing: 0.03em; }
    .status-green { background-color: #ECFDF5; color: #047857 !important; border: 1px solid #A7F3D0;}
    .status-yellow { background-color: #FFFBEB; color: #B45309 !important; border: 1px solid #FDE68A;}
    .status-red { background-color: #FEF2F2; color: #B91C1C !important; border: 1px solid #FECACA;}
    .status-gray { background-color: #F1F5F9; color: #475569 !important; border: 1px solid #E2E8F0;}
    
    /* TABLERO KANBAN PREMIUM */
    .kanban-card { background: #FFFFFF; padding: 18px; border-radius: 14px; border: 1px solid #E2E8F0; border-top: 4px solid #2563EB; box-shadow: 0 4px 12px rgba(0,0,0,0.02); margin-bottom: 16px; }
    .kanban-title { font-weight: 700; color: #0F172A; font-size: 0.95rem; margin-bottom: 8px; }
    .kanban-meta { font-size: 0.8rem; color: #64748B; margin-bottom: 4px; }

    /* PESTAÑAS (TABS) SAAS */
    .stTabs [data-baseweb="tab-list"] { gap: 28px; border-bottom: 2px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #2563EB !important; font-weight: 700 !important; color: #2563EB !important; background-color: transparent !important; }
    .stTabs [aria-selected="false"] { color: #64748B !important; font-weight: 600 !important; }

    /* WIDGET FLOTANTE FIJO EXCLUSIVO PROJECT IA (ESQUINA INFERIOR DERECHA) */
    .floating-ia-box {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 999999 !important;
    }
    .floating-ia-box div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 12px 24px !important;
        box-shadow: 0 8px 24px rgba(28, 66, 232, 0.35) !important;
        border: 2px solid #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: transform 0.2s ease !important;
    }
    .floating-ia-box div[data-testid="stPopover"] > button:hover {
        transform: scale(1.04) translateY(-2px) !important;
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONSTANTES DE CONFIGURACIÓN ---
OPCIONES_AREAS = ["Incentivos", "Afore", "Banca Empresarial", "Banco", "CAT Cobranza", "CAT P&V", "CEDIS", "Cobranza Domiciliaria", "Credito Automotriz", "Inmobiliaria", "Retail", "Sale Vale"]
OPCIONES_TIPOS = ["Esquema de Incentivos", "Tecnología", "Estratégicos", "Procesos", "Campañas", "Auditorías"]
OPCIONES_SUBTIPOS = ["EI-Nuevo incentivo completo", "EI-Actualización completa de incentivo", "EI-Ajuste menor de incentivo", "EI-Ajuste mayor de incentivo", "EI-Casos especiales", "CA-Campaña", "CA-Concurso", "PR-Documentación oficial", "PR-Nuevo proceso", "TE-Software", "TE-Tableros", "Otros"]
OPCIONES_ETAPAS = ["1. Diseño (EI)", "2. Prueba piloto (EI)", "3. Escalamiento nacional (EI)", "4. Cierre (EI)", "1. Diseño (CA)", "2. Implementación (CA)", "3. Evaluación y cierre (CA)", "4. Cierre (CA)", "1. Planeación", "2. Ejecución", "3. Cierre"]
OPCIONES_ESTATUS = ["Por iniciar", "En tiempo", "Retrasado", "Detenido", "Cancelado"]
OPCIONES_GERENTES = ["Andres Avila", "Eduardo Rodriguez", "Heriberto Vega", "Janik Orozco", "Kurokusi Ochoa", "Noel Aquino", "Yahir Ramirez", "Giovanni Vallejo", "Ruben Rivera"]

# --- CONEXIÓN DE BASE DE DATOS Y CACHÉ ---
@st.cache_resource
def obtener_engine():
  db_url = st.secrets["postgres"]["url"] if "postgres" in st.secrets else "sqlite:///db_coppel_v5.db"
  return sqlalchemy.create_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)

def inicializar_db():
  engine = obtener_engine()
  
  with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS proyectos (id SERIAL PRIMARY KEY, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT, tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT, etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT, presupuesto REAL DEFAULT 0.0, roi_estimado REAL DEFAULT 0.0, fecha_inicio_baseline TEXT, fecha_fin_baseline TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS tareas (id SERIAL PRIMARY KEY, proyecto_id INTEGER, nombre_tarea TEXT NOT NULL, responsable TEXT, fecha_inicio TEXT, duracion_dias INTEGER, fecha_fin TEXT, porcentaje_avance REAL, predecesoras TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS bitacora (id SERIAL PRIMARY KEY, proyecto_id INTEGER, usuario_nombre TEXT, fecha_hora TEXT, comentario TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS solicitudes_baseline (id SERIAL PRIMARY KEY, proyecto_id INTEGER, solicitante TEXT, fecha_fin_propuesta TEXT, motivo TEXT, estado TEXT DEFAULT 'Pendiente', fecha_solicitud TEXT, aprobador TEXT)"""))

  for col_sql in [
      "ALTER TABLE proyectos ADD COLUMN presupuesto REAL DEFAULT 0.0",
      "ALTER TABLE proyectos ADD COLUMN roi_estimado REAL DEFAULT 0.0",
      "ALTER TABLE proyectos ADD COLUMN fecha_inicio_baseline TEXT",
      "ALTER TABLE proyectos ADD COLUMN fecha_fin_baseline TEXT"
  ]:
      try:
          with engine.begin() as conn: conn.execute(sqlalchemy.text(col_sql))
      except Exception: pass

  with engine.begin() as conn:
    res = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM usuarios")).fetchone()
    if res[0] == 0:
      conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')"))

inicializar_db()

@st.cache_data(ttl=3)
def cargar_datos_completos():
  engine = obtener_engine()
  df_p = pd.read_sql("SELECT * FROM proyectos ORDER BY id DESC", engine)
  df_b = pd.read_sql("SELECT * FROM bitacora ORDER BY id DESC", engine)
  df_t = pd.read_sql("SELECT * FROM tareas ORDER BY id ASC", engine)
  df_u = pd.read_sql("SELECT nombre, correo, password, rol FROM usuarios ORDER BY nombre ASC", engine)
  df_s = pd.read_sql("SELECT * FROM solicitudes_baseline ORDER BY id DESC", engine)
  
  if 'presupuesto' not in df_p.columns: df_p['presupuesto'] = 0.0
  if 'roi_estimado' not in df_p.columns: df_p['roi_estimado'] = 0.0
  if 'fecha_inicio_baseline' not in df_p.columns: df_p['fecha_inicio_baseline'] = None
  if 'fecha_fin_baseline' not in df_p.columns: df_p['fecha_fin_baseline'] = None
  
  df_p['presupuesto'] = df_p['presupuesto'].fillna(0.0)
  df_p['roi_estimado'] = df_p['roi_estimado'].fillna(0.0)
  
  return df_p, df_b, df_t, df_u, df_s

def limpiar_cache_y_recargar():
  cargar_datos_completos.clear()

def obtener_lista_usuarios(df_u):
  return df_u["nombre"].tolist() if not df_u.empty else ["Leonardo Castillo"]

def auto_sincronizar_avance_proyecto(engine, p_id):
  with engine.begin() as conn:
    res = conn.execute(sqlalchemy.text("SELECT AVG(porcentaje_avance) FROM tareas WHERE proyecto_id = :pid"), {"pid": p_id}).fetchone()
    if res and res[0] is not None:
      promedio_real = round(float(res[0]) / 100.0, 4)
      ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      conn.execute(sqlalchemy.text("UPDATE proyectos SET avance_real = :a, ultima_actualizacion = :u WHERE id = :pid"),
                   {"a": promedio_real, "u": ahora, "pid": p_id})

def calcular_fechas_tarea_df(df_tareas_proyecto):
  if df_tareas_proyecto.empty: return df_tareas_proyecto
  df_t = df_tareas_proyecto.copy()
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
    df_t.at[idx, "avance_txt"] = f"{int(row['porcentaje_avance'])}%"
  return df_t

def evaluar_estancamiento(fecha_actualizacion_str):
  if not fecha_actualizacion_str or str(fecha_actualizacion_str).strip() in ["", "None", "N/A"]: return True
  try:
    f_act = datetime.strptime(str(fecha_actualizacion_str)[:19], "%Y-%m-%d %H:%M:%S")
    return (datetime.now() - f_act).days > 20
  except Exception: return False

def calcular_metricas_baseline(row):
  f_fin_b_str = row.get("fecha_fin_baseline")
  if not f_fin_b_str or str(f_fin_b_str).strip() in ["", "None", "N/A"]:
      return {"pct_planeado": 0.0, "desviacion": 0.0, "estatus_sugerido": row.get("estatus_tiempo", "En tiempo"), "tiene_baseline": False}
  
  try:
      f_ini_b_str = row.get("fecha_inicio_baseline")
      f_ini = datetime.strptime(str(f_ini_b_str)[:10], "%Y-%m-%d") if f_ini_b_str and str(f_ini_b_str).strip() not in ["", "None"] else datetime.now() - timedelta(days=30)
      f_fin = datetime.strptime(str(f_fin_b_str)[:10], "%Y-%m-%d")
      hoy = datetime.now()

      if hoy <= f_ini: pct_planeado = 0.0
      elif hoy >= f_fin: pct_planeado = 1.0
      else: pct_planeado = min(max((hoy - f_ini).days / max((f_fin - f_ini).days, 1), 0.0), 1.0)

      avance_real = float(row.get("avance_real") or 0.0)
      desviacion = avance_real - pct_planeado

      if avance_real >= 1.0: estatus = "En tiempo"
      elif hoy > f_fin and avance_real < 1.0: estatus = "Retrasado"
      elif desviacion < -0.10: estatus = "Retrasado"
      else: estatus = row.get("estatus_tiempo", "En tiempo")

      return {"pct_planeado": pct_planeado, "desviacion": desviacion, "estatus_sugerido": estatus, "tiene_baseline": True, "fecha_fin_baseline": str(f_fin_b_str)[:10]}
  except Exception:
      return {"pct_planeado": 0.0, "desviacion": 0.0, "estatus_sugerido": row.get("estatus_tiempo", "En tiempo"), "tiene_baseline": False}

# --- GATEWAY DE AUTENTICACIÓN ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False; st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
  col_izq, col_centro, col_der = st.columns([1, 1.3, 1])
  with col_centro:
    st.write(""); st.write("")
    st.markdown("<h1 style='text-align: center; color:#0F172A !important; font-size: 2.6rem; letter-spacing: -1.5px;'>HEADING 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 30px; font-size: 1rem; font-weight: 500;'>Project Steering Platform</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
      st.markdown("<h3 style='color:#0F172A !important; font-size: 1.15rem; margin-bottom: 16px;'>Acceso Institucional</h3>", unsafe_allow_html=True)
      correo_input = st.text_input("Correo Institucional", placeholder="tu.nombre@coppel.com")
      password_input = st.text_input("Contraseña", type="password")
      st.write("")
      if st.form_submit_button("Ingresar a Heading 360", type="primary", use_container_width=True):
        if correo_input.strip() == "": st.warning("Por favor ingresa tu correo.")
        else:
          engine = obtener_engine()
          with engine.connect() as conn:
            res = conn.execute(sqlalchemy.text("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=:c"), {"c": correo_input.strip().lower()}).fetchone()
            if res and res[0] == password_input:
              st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower(); st.session_state.rol = res[1]; st.session_state.nombre_actual = res[2]; st.rerun()
            else: st.error("Credenciales incorrectas.")
  st.stop()

# --- CARGA GENERAL DE DATOS ---
df, df_bitacora, df_tareas_all, df_users_raw, df_solicitudes_baseline = cargar_datos_completos()
es_moderador = st.session_state.rol == "Moderador"
lista_lideres_registrados = obtener_lista_usuarios(df_users_raw)

if not df.empty:
  df['es_estancado'] = df['ultima_actualizacion'].apply(evaluar_estancamiento) & (~df['etapa_actual'].str.contains("Cierre", case=False, na=False))
  df['info_baseline'] = df.apply(calcular_metricas_baseline, axis=1)
  df['estatus_calculado'] = df.apply(lambda r: r['info_baseline']['estatus_sugerido'], axis=1)
  proyectos_retrasados = df[df["estatus_calculado"].isin(["Retrasado", "Detenido"])]
  proyectos_estancados = df[df['es_estancado']]
else:
  df['es_estancado'] = False
  df['info_baseline'] = None
  df['estatus_calculado'] = "En tiempo"
  proyectos_estancados = pd.DataFrame()
  proyectos_retrasados = pd.DataFrame()

# --- SIDEBAR EXECUTIVE ---
with st.sidebar:
  st.markdown(f"""
  <div style='background-color:#FFFFFF; padding: 18px; border-radius: 14px; border: 1px solid #E2E8F0; margin-bottom: 18px;'>
    <h3 style='margin:0 0 2px 0; font-size:1.05rem; color:#0F172A;'>{st.session_state.nombre_actual}</h3>
    <p style='margin:0 0 10px 0; color:#64748B; font-size:0.8rem;'>{st.session_state.correo_actual}</p>
    <span class='status-badge {'status-green' if es_moderador else 'status-gray'}'>{st.session_state.rol}</span>
  </div>
  """, unsafe_allow_html=True)
  
  with st.expander("⚙️ Perfil & Seguridad", expanded=False):
    with st.form("form_cambio_pass"):
      nueva_pass = st.text_input("Nueva Contraseña", type="password")
      confirmar_pass = st.text_input("Confirmar Contraseña", type="password")
      if st.form_submit_button("Actualizar Clave", use_container_width=True):
        if nueva_pass == confirmar_pass and nueva_pass:
          engine = obtener_engine()
          with engine.begin() as conn: conn.execute(sqlalchemy.text("UPDATE usuarios SET password=:p WHERE correo=:c"), {"p": nueva_pass, "c": st.session_state.correo_actual})
          limpiar_cache_y_recargar(); st.success("¡Contraseña actualizada!")
        else: st.error("Las contraseñas no coinciden.")

  st.write("")
  st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;'>Exportación de Datos</p>", unsafe_allow_html=True)
  if not df.empty:
    def generar_pdf(dataframe):
      pdf = FPDF(orientation="L", unit="mm", format="A4"); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page(); pdf.set_font("Arial", "B", 16); pdf.set_text_color(15, 23, 42)
      pdf.cell(0, 8, "Heading 360 - Reporte de Portafolio Executive", ln=True, align="L"); pdf.set_font("Arial", "", 9); pdf.set_text_color(100, 100, 100)
      pdf.cell(0, 6, f"Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", ln=True, align="L"); pdf.ln(4)
      pdf.set_font("Arial", "B", 8); pdf.set_fill_color(241, 245, 249); pdf.set_text_color(15, 23, 42)
      pdf.cell(22, 8, "Folio", 1, 0, "C", True); pdf.cell(60, 8, "Iniciativa", 1, 0, "L", True); pdf.cell(30, 8, "Area", 1, 0, "L", True); pdf.cell(35, 8, "Responsable", 1, 0, "L", True); pdf.cell(25, 8, "Estatus", 1, 0, "C", True); pdf.cell(18, 8, "Avance", 1, 0, "C", True); pdf.cell(42, 8, "Ult. Act.", 1, 0, "C", True); pdf.cell(45, 8, "Fase Actual", 1, 1, "L", True)
      pdf.set_font("Arial", "", 8); pdf.set_text_color(40, 40, 40)
      for _, row in dataframe.iterrows():
        pdf.cell(22, 7, str(row["folio"])[:12], 1, 0, "C"); pdf.cell(60, 7, str(row["nombre"])[:35], 1, 0, "L"); pdf.cell(30, 7, str(row["area_negocio"])[:18], 1, 0, "L"); pdf.cell(35, 7, str(row["lider_asignado"])[:22], 1, 0, "L"); pdf.cell(25, 7, str(row["estatus_tiempo"])[:15], 1, 0, "C"); pdf.cell(18, 7, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, "C"); pdf.set_font("Arial", "B", 8); pdf.cell(42, 7, str(row["ultima_actualizacion"])[:19], 1, 0, "C"); pdf.set_font("Arial", "", 8); pdf.cell(45, 7, str(row["etapa_actual"])[:25], 1, 1, "L")
      with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp: pdf.output(tmp.name); return tmp.name

    with open(generar_pdf(df), "rb") as file: st.download_button("Reporte PDF", data=file, file_name=f"Heading360_{datetime.now().strftime('%Y%m%d')}.pdf", use_container_width=True, type="secondary")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer: df.to_excel(writer, index=False, sheet_name="Proyectos")
    st.download_button("Exportar a Excel (.xlsx)", data=excel_buffer.getvalue(), file_name=f"Base_Datos_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="secondary")

  st.write("")
  if st.button("Cerrar Sesión", use_container_width=True): st.session_state.autenticado = False; st.rerun()

# --- HEADER EXECUTIVE Y TARJETAS KPI ---
st.markdown("<h2 style='margin-bottom: 4px; color:#0F172A;'>Visión General del Portafolio</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-bottom: 24px; font-size:0.95rem;'>Tablero de control estratégico y gobernanza de proyectos activos.</p>", unsafe_allow_html=True)

total_p = len(df); en_t = len(df[df["estatus_calculado"] == "En tiempo"]) if total_p > 0 else 0; ret = len(proyectos_retrasados) if total_p > 0 else 0
presupuesto_total = df["presupuesto"].sum() if total_p > 0 else 0.0
roi_total = df["roi_estimado"].sum() if total_p > 0 else 0.0

st.markdown(f"""
<div class='kpi-grid'>
    <div class='kpi-card'>
        <div class='kpi-title'>Proyectos Activos</div>
        <div class='kpi-num'>{total_p}</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-title'>En Tiempo (Baseline)</div>
        <div class='kpi-num' style='color:#047857;'>{en_t}</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-title'>Retrasados / Riesgo</div>
        <div class='kpi-num' style='color:#B91C1C;'>{ret}</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-title'>Presupuesto Invertido</div>
        <div class='kpi-num'>${presupuesto_total:,.2f}</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-title'>Impacto / ROI Estimado</div>
        <div class='kpi-num' style='color:#2563EB;'>${roi_total:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- PESTAÑAS CORPORATIVAS CON CONTROL DE ROL ---
if es_moderador: 
  tabs = st.tabs(["📈 Dashboard Analítico", "🚀 Seguimiento de Proyectos", "📋 Tablero Kanban", "➕ Nuevo Proyecto", "📜 Bitácora General", "👥 Accesos"])
else: 
  tabs = st.tabs(["📈 Dashboard Analítico", "🚀 Seguimiento de Proyectos", "📋 Tablero Kanban"])

# PESTAÑA 1: DASHBOARD
with tabs[0]:
  st.write("")
  if df.empty: st.info("Agrega algunos proyectos para visualizar los gráficos analíticos.")
  else:
    d_col1, d_col2 = st.columns(2)
    with d_col1:
      fig1 = px.pie(df, names="area_negocio", title="Distribución por Área Solicitante", hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism)
      fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Plus Jakarta Sans"), title_font=dict(size=16, color="#0F172A")); st.plotly_chart(fig1, use_container_width=True)
    with d_col2:
      df_status_count = df["estatus_calculado"].value_counts().reset_index(); df_status_count.columns = ["Estatus", "Volumen"]
      fig2 = px.bar(df_status_count, x="Estatus", y="Volumen", title="Estatus de Salud (Baseline vs. Real)", color="Estatus", color_discrete_map={"En tiempo": "#047857", "Retrasado": "#B91C1C", "Detenido": "#B45309", "Por iniciar": "#94A3B8"})
      fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Plus Jakarta Sans"), title_font=dict(size=16, color="#0F172A")); st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("<h4 style='color:#0F172A; margin-bottom:15px;'>Matriz de Carga de Trabajo por Líder Operativo</h4>", unsafe_allow_html=True)
    
    carga_df = df.groupby(["lider_asignado", "estatus_calculado"]).size().reset_index(name="Cantidad")
    fig_carga = px.bar(carga_df, x="lider_asignado", y="Cantidad", color="estatus_calculado", title="", barmode="stack", color_discrete_map={"En tiempo": "#047857", "Retrasado": "#B91C1C", "Detenido": "#B45309", "Por iniciar": "#94A3B8"})
    fig_carga.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Plus Jakarta Sans"), xaxis_title="Líder", yaxis_title="Número de Iniciativas")
    st.plotly_chart(fig_carga, use_container_width=True)

# PESTAÑA 2: SEGUIMIENTO DE PROYECTOS
with tabs[1]:
  if df.empty: st.info("No hay proyectos registrados todavía.")
  else:
    # 1. APROBACIONES PENDIENTES DE RE-BASELINE
    if es_moderador and not df_solicitudes_baseline.empty:
      sol_pendientes = df_solicitudes_baseline[df_solicitudes_baseline["estado"] == "Pendiente"]
      if not sol_pendientes.empty:
          st.markdown(f"### 📬 Control de Cambios: Solicitudes Pendientes ({len(sol_pendientes)})")
          for _, sol in sol_pendientes.iterrows():
              p_rel_df = df[df["id"] == sol["proyecto_id"]]
              p_rel = p_rel_df.iloc[0] if not p_rel_df.empty else None
              p_nom = p_rel["nombre"] if p_rel is not None else "Proyecto General"
              f_actual = p_rel["fecha_fin_baseline"] if (p_rel is not None and p_rel["fecha_fin_baseline"]) else "Sin Baseline"
              
              c_s1, c_s2, c_s3, c_s4 = st.columns([2.5, 2, 1, 1])
              c_s1.markdown(f"**Proyecto:** [{p_rel['folio'] if p_rel is not None else ''}] {p_nom}\n\n*Solicitante:* {sol['solicitante']} | *Motivo:* {sol['motivo']}")
              c_s2.markdown(f"**Fecha Actual:** `{f_actual}`\n\n**Nueva Propuesta:** `{sol['fecha_fin_propuesta']}`")
              
              if c_s3.button("✅ Aprobar", key=f"btn_aprb_{sol['id']}"):
                  ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  engine = obtener_engine()
                  with engine.begin() as conn:
                      conn.execute(sqlalchemy.text("UPDATE proyectos SET fecha_fin_baseline = :n_f WHERE id = :pid"),
                                   {"n_f": sol['fecha_fin_propuesta'], "pid": sol['proyecto_id']})
                      conn.execute(sqlalchemy.text("UPDATE solicitudes_baseline SET estado = 'Aprobado', aprobador = :ap WHERE id = :sid"),
                                   {"ap": st.session_state.nombre_actual, "sid": sol['id']})
                      conn.execute(sqlalchemy.text("INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:pid, :usr, :fh, :com)"),
                                   {"pid": sol['proyecto_id'], "usr": st.session_state.nombre_actual, "fh": ahora, "com": f"Aprobación de Re-baseline: Nueva fecha fin comprometida {sol['fecha_fin_propuesta']}."})
                  limpiar_cache_y_recargar(); st.success("¡Baseline actualizado!"); st.rerun()

              if c_s4.button("❌ Rechazar", key=f"btn_rchz_{sol['id']}"):
                  engine = obtener_engine()
                  with engine.begin() as conn:
                      conn.execute(sqlalchemy.text("UPDATE solicitudes_baseline SET estado = 'Rechazado', aprobador = :ap WHERE id = :sid"),
                                   {"ap": st.session_state.nombre_actual, "sid": sol['id']})
                  limpiar_cache_y_recargar(); st.info("Solicitud rechazada."); st.rerun()
              st.divider()

    # 2. BARRA SUPERIOR DE ACCIONES
    col_hdr1, col_hdr2, col_hdr3 = st.columns([2.5, 1, 1])
    with col_hdr1:
        st.markdown("<h3 style='margin:0;'>Seguimiento Operativo</h3>", unsafe_allow_html=True)
    with col_hdr2:
        pop_rebase = st.popover("📩 Solicitar Re-baseline", use_container_width=True)
        with pop_rebase:
            st.markdown("<b>Solicitar Ajuste de Fecha Compromiso</b>", unsafe_allow_html=True)
            df_mis_proyectos = df if es_moderador else df[df["lider_asignado"] == st.session_state.nombre_actual]
            if df_mis_proyectos.empty: st.info("No tienes proyectos asignados.")
            else:
                opciones_p_sol = df_mis_proyectos.apply(lambda x: f"{x['id']} - [{x['folio'] or 'S/F'}] {x['nombre']}", axis=1).tolist()
                with st.form("f_sol_baseline_central"):
                    p_sol_elegido = st.selectbox("Iniciativa", opciones_p_sol)
                    n_f_prop = st.date_input("Nueva Fecha Fin Propuesta")
                    n_motivo = st.text_area("Justificación del Ajuste *", placeholder="Motivo de la variación de tiempo...")
                    if st.form_submit_button("Enviar Solicitud", type="primary", use_container_width=True):
                        if n_motivo.strip() and p_sol_elegido:
                            pid_sol = int(p_sol_elegido.split(" - ")[0])
                            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            engine = obtener_engine()
                            with engine.begin() as conn:
                                conn.execute(sqlalchemy.text("""INSERT INTO solicitudes_baseline (proyecto_id, solicitante, fecha_fin_propuesta, motivo, estado, fecha_solicitud) 
                                                               VALUES (:pid, :sol, :ff, :mot, 'Pendiente', :fsol)"""),
                                             {"pid": pid_sol, "sol": st.session_state.nombre_actual, "ff": str(n_f_prop), "mot": n_motivo.strip(), "fsol": ahora})
                            limpiar_cache_y_recargar(); st.success("¡Solicitud enviada!"); st.rerun()
                        else: st.error("La justificación es obligatoria.")

    with col_hdr3:
        if es_moderador:
            pop_del = st.popover("🗑️ Borrado Masivo", use_container_width=True)
            with pop_del:
                st.markdown("<b>Eliminación Masiva de Proyectos</b>", unsafe_allow_html=True)
                opciones_proyectos_borrar = df.apply(lambda x: f"{x['id']} - [{x['folio'] or 'S/F'}] {x['nombre']}", axis=1).tolist()
                proyectos_a_borrar = st.multiselect("Marcar proyectos", opciones_proyectos_borrar)
                if st.button("Confirmar Borrado", type="primary", use_container_width=True):
                    if proyectos_a_borrar:
                        ids_borrar = [int(p.split(" - ")[0]) for p in proyectos_a_borrar]
                        engine = obtener_engine()
                        with engine.begin() as conn:
                            for pid in ids_borrar:
                                conn.execute(sqlalchemy.text("DELETE FROM tareas WHERE proyecto_id = :id"), {"id": pid})
                                conn.execute(sqlalchemy.text("DELETE FROM bitacora WHERE proyecto_id = :id"), {"id": pid})
                                conn.execute(sqlalchemy.text("DELETE FROM proyectos WHERE id = :id"), {"id": pid})
                        limpiar_cache_y_recargar(); st.success("Proyectos eliminados."); st.rerun()

    st.write("")

    # 3. BÚSQUEDA Y FILTROS LIMPIOS
    c_f1, c_f2, c_f3 = st.columns([2, 1.2, 1.2])
    txt_busqueda = c_f1.text_input("🔍 Buscar por Nombre o Folio...", label_visibility="collapsed", placeholder="🔍 Buscar por Nombre o Folio...")
    filtro_area = c_f2.selectbox("Área", ["Todas las Áreas"] + OPCIONES_AREAS, label_visibility="collapsed")
    filtro_lider = c_f3.selectbox("Responsable", ["Todos los Responsables"] + lista_lideres_registrados, label_visibility="collapsed")

    modo_filtro = st.pills("Filtro Rápido:", ["Todos", "🚨 Retrasados", "⚠️ Estancados (>20d)", "⭐ Mis Proyectos"], default="Todos")

    df_filtrado = df.copy()
    if modo_filtro == "🚨 Retrasados": df_filtrado = df_filtrado[df_filtrado["estatus_calculado"].isin(["Retrasado", "Detenido"])]
    elif modo_filtro == "⚠️ Estancados (>20d)": df_filtrado = df_filtrado[df_filtrado["es_estancado"] == True]
    elif modo_filtro == "⭐ Mis Proyectos": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == st.session_state.nombre_actual]

    if txt_busqueda.strip(): df_filtrado = df_filtrado[df_filtrado["nombre"].str.lower().str.contains(txt_busqueda.lower(), na=False) | df_filtrado["folio"].str.lower().str.contains(txt_busqueda.lower(), na=False)]
    if filtro_area != "Todas las Áreas": df_filtrado = df_filtrado[df_filtrado["area_negocio"] == filtro_area]
    if filtro_lider != "Todos los Responsables": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == filtro_lider]

    st.markdown(f"<p style='color: #64748B; font-size: 0.8rem; margin-top: 10px; margin-bottom: 20px;'>📌 Mostrando <b>{len(df_filtrado)}</b> de <b>{len(df)}</b> iniciativas.</p>", unsafe_allow_html=True)

    # 4. TARJETAS DE PROYECTO
    for _, row in df_filtrado.iterrows():
      p_id = row["id"]
      info_b = row.get("info_baseline") or calcular_metricas_baseline(row)
      
      badge_status = "status-green" if row["estatus_calculado"] == "En tiempo" else ("status-yellow" if row["estatus_calculado"] == "Detenido" else "status-red")
      tag_estancado = " <span class='status-badge status-red'>⚠️ Estancado</span>" if row.get("es_estancado", False) else ""

      desviacion_str = ""
      if info_b["tiene_baseline"]:
          desv_pct = int(info_b["desviacion"] * 100)
          signo = "+" if desv_pct >= 0 else ""
          desviacion_str = f" | Plan: {int(info_b['pct_planeado']*100)}% ({signo}{desv_pct}%)"

      es_mi_proyecto = (row["lider_asignado"] == st.session_state.nombre_actual)
      puedo_editar = es_moderador or es_mi_proyecto

      df_tareas_proj = df_tareas_all[df_tareas_all["proyecto_id"] == p_id]
      tiene_tareas = not df_tareas_proj.empty

      if tiene_tareas:
          avance_calculado_gantt = round(float(df_tareas_proj["porcentaje_avance"].mean() / 100.0), 4)
          avance_display = avance_calculado_gantt
      else:
          avance_display = float(row["avance_real"] or 0.0)

      with st.expander(f"[{row['folio'] or 'S/F'}] {row['nombre']} — Avance: {int(avance_display*100)}%{desviacion_str}"):
        st.progress(float(avance_display))

        st.markdown(f"""
        <div style='background-color:#F8FAFC; padding:18px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:16px;'>
            <div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:16px;'>
                <div><span style='color:#64748B; font-size:0.75rem; font-weight:700;'>RESPONSABLE</span><br/><b style='color:#0F172A; font-size:0.9rem;'>{row['lider_asignado']}</b></div>
                <div><span style='color:#64748B; font-size:0.75rem; font-weight:700;'>ÁREA</span><br/><b style='color:#0F172A; font-size:0.9rem;'>{row['area_negocio']}</b></div>
                <div><span style='color:#64748B; font-size:0.75rem; font-weight:700;'>FASE</span><br/><b style='color:#2563EB; font-size:0.9rem;'>{row['etapa_actual']}</b></div>
                <div><span style='color:#64748B; font-size:0.75rem; font-weight:700;'>ESTATUS</span><br/><span class='status-badge {badge_status}'>{row['estatus_calculado']}</span>{tag_estancado}</div>
                <div><span style='color:#64748B; font-size:0.75rem; font-weight:700;'>FECHA BASELINE</span><br/><b style='color:#0F172A; font-size:0.9rem;'>{info_b.get('fecha_fin_baseline', 'Sin Fecha')}</b></div>
                <div><span style='color:#64748B; font-size:0.75rem; font-weight:700;'>PRESUPUESTO / ROI</span><br/><b style='color:#047857; font-size:0.9rem;'>${float(row.get('presupuesto', 0.0)):,.2f} / ${float(row.get('roi_estimado', 0.0)):,.2f}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if puedo_editar:
          col_btn_edit, _ = st.columns([1, 4])
          with col_btn_edit:
              pop_edit = st.popover("✏️ Editar Proyecto", use_container_width=True)
              with pop_edit:
                  st.markdown(f"<b>Editar Proyecto [{row['folio'] or 'S/F'}]</b>", unsafe_allow_html=True)
                  with st.form(f"form_pop_edit_{p_id}"):
                      u_etapa = st.selectbox("Fase", OPCIONES_ETAPAS, index=(OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0))
                      u_estatus = st.selectbox("Estatus Declarado", OPCIONES_ESTATUS, index=(OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0))
                      
                      if tiene_tareas:
                          st.info(f"Avance auto-sincronizado con Gantt: **{int(avance_calculado_gantt*100)}%**")
                          u_avance = avance_calculado_gantt
                      else:
                          u_avance = st.slider("Progreso General (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
                      
                      f1, f2 = st.columns(2)
                      u_presupuesto = f1.number_input("Presupuesto ($)", min_value=0.0, value=float(row.get("presupuesto", 0.0)), step=1000.0)
                      u_roi = f2.number_input("ROI Estimado ($)", min_value=0.0, value=float(row.get("roi_estimado", 0.0)), step=1000.0)

                      u_comentario = st.text_input("Añadir Comentario a Bitácora Global", placeholder="Ej. Actualización de entregables...")
                      u_carpeta = st.text_input("Carpeta Drive (URL)", row["carpeta_url"] or "")
                      u_plan = st.text_input("Link a Plan Anexo", row["plan_url"] or "")
                      
                      st.write("")
                      if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
                          ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                          texto_bitacora = u_comentario.strip() or f"Actualización: Estatus '{u_estatus}', Fase '{u_etapa}' y Avance al {int(u_avance*100)}%."

                          engine = obtener_engine()
                          with engine.begin() as conn:
                              conn.execute(sqlalchemy.text("""UPDATE proyectos SET etapa_actual=:e, estatus_tiempo=:s, avance_real=:a, carpeta_url=:c, plan_url=:p, ultima_actualizacion=:u, presupuesto=:pr, roi_estimado=:ro WHERE id=:id"""), 
                                           {"e": u_etapa, "s": u_estatus, "a": u_avance, "c": u_carpeta, "p": u_plan, "u": ahora, "pr": u_presupuesto, "ro": u_roi, "id": p_id})
                              conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), 
                                           {"p_id": p_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": texto_bitacora})
                          limpiar_cache_y_recargar(); st.rerun()

                      if es_moderador and st.form_submit_button("Eliminar Proyecto", type="secondary", use_container_width=True):
                          engine = obtener_engine()
                          with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM proyectos WHERE id=:id"), {"id": p_id})
                          limpiar_cache_y_recargar(); st.rerun()
        else:
          st.info(f"🔒 **Modo Lectura:** Solo **{row['lider_asignado']}** o un Moderador pueden editar este proyecto.")

        # DIAGRAMA GANTT INTERCONECTADO
        st.markdown("<h4 style='color:#0F172A; margin-top: 16px; margin-bottom:12px; font-size:1.05rem;'>Plan de Trabajo (Gantt Interconectado)</h4>", unsafe_allow_html=True)
        df_tareas_calc = calcular_fechas_tarea_df(df_tareas_proj)

        if not df_tareas_calc.empty:
          fig = px.timeline(
              df_tareas_calc, x_start="fecha_inicio", x_end="fecha_fin", y="nombre_tarea",
              color="porcentaje_avance", text="avance_txt",
              color_continuous_scale=[[0, "#E2E8F0"], [0.5, "#3B82F6"], [1, "#0F172A"]],
              range_color=[0, 100], hover_data={"responsable": True, "porcentaje_avance": False, "avance_txt": False}
          )
          fig.update_yaxes(autorange="reversed")
          fig.update_traces(textposition='inside', insidetextanchor='middle', marker_line_color='rgba(0,0,0,0.1)', marker_line_width=1, opacity=0.95, textfont=dict(color='white', size=11, weight='bold'))
          fig.update_layout(height=160 + (len(df_tareas_calc) * 35), margin=dict(l=0, r=0, t=10, b=0), font=dict(family="Plus Jakarta Sans"), xaxis=dict(showgrid=True, gridcolor="#F1F5F9"), yaxis=dict(showgrid=False, title=""), coloraxis_colorbar=dict(title="% Avance"))
          st.plotly_chart(fig, use_container_width=True)

          if puedo_editar:
            st.markdown("<p style='font-size:0.8rem; font-weight:700; color:#2563EB;'>EDITAR AVANCE DE TAREA</p>", unsafe_allow_html=True)
            with st.form(f"upd_t_{p_id}", clear_on_submit=True):
              col_sel, col_val, col_btn = st.columns([2, 1, 1])
              opciones_tareas = df_tareas_calc.apply(lambda x: f"{x['id']} - {x['nombre_tarea']}", axis=1).tolist()
              t_sel = col_sel.selectbox("Selecciona la tarea", opciones_tareas)
              t_val = col_val.number_input("Nuevo Avance (%)", min_value=0, max_value=100, step=10)
              st.write("")
              if col_btn.form_submit_button("Guardar % Avance", type="secondary"):
                if t_sel:
                  t_id_real = int(t_sel.split(" - ")[0])
                  t_nombre_txt = t_sel.split(" - ")[1]
                  ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  engine = obtener_engine()
                  with engine.begin() as conn: 
                      conn.execute(sqlalchemy.text("UPDATE tareas SET porcentaje_avance=:a WHERE id=:id"), {"a": t_val, "id": t_id_real})
                      conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), 
                                   {"p_id": p_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": f"Se actualizó la tarea '{t_nombre_txt}' al {t_val}% de avance."})
                  
                  auto_sincronizar_avance_proyecto(engine, p_id)
                  limpiar_cache_y_recargar(); st.rerun()
        else: st.info("No has agregado tareas al plan de trabajo todavía.")

        if puedo_editar:
          with st.expander("➕ Agregar Nueva Tarea al Gantt"):
            with st.form(f"ft_{p_id}", clear_on_submit=True):
              t_nom = st.text_input("Nombre de la Tarea *")
              c_t1, c_t2, c_t3, c_t4 = st.columns(4)
              t_res = c_t1.selectbox("Responsable", lista_lideres_registrados)
              t_ini = c_t2.date_input("Fecha de Inicio")
              t_dur = c_t3.number_input("Duración (Días)", 1, value=5)
              t_pre = c_t4.text_input("Predecesoras (Ej. 1, 2)")
              if st.form_submit_button("Añadir a Gantt"):
                if t_nom.strip():
                  ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  engine = obtener_engine()
                  with engine.begin() as conn: 
                      conn.execute(sqlalchemy.text("""INSERT INTO tareas (proyecto_id, nombre_tarea, responsable, fecha_inicio, duracion_dias, fecha_fin, porcentaje_avance, predecesoras) VALUES (:pid, :n, :r, :fi, :d, :ff, 0.0, :p)"""), {"pid": p_id, "n": t_nom, "r": t_res, "fi": str(t_ini), "d": t_dur, "ff": str(pd.to_datetime(t_ini) + timedelta(days=t_dur - 1)), "p": t_pre})
                      conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), 
                                   {"p_id": p_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": f"Se añadió la nueva tarea '{t_nom}' al cronograma Gantt."})
                  
                  auto_sincronizar_avance_proyecto(engine, p_id)
                  limpiar_cache_y_recargar(); st.rerun()

# PESTAÑA 3: TABLERO KANBAN
with tabs[2]:
  st.write("")
  if df.empty: st.info("Agrega proyectos para verlos en el tablero.")
  else:
    k_cols = st.columns(len(OPCIONES_ESTATUS))
    for i, status in enumerate(OPCIONES_ESTATUS):
      with k_cols[i]:
        st.markdown(f"<div style='background-color:#FFFFFF; padding:10px; border-radius:10px; border:1px solid #E2E8F0; text-align:center; font-weight:800; color:#0F172A; font-size:0.85rem; margin-bottom:16px;'>{status.upper()}</div>", unsafe_allow_html=True)
        df_k = df[df["estatus_calculado"] == status]
        for _, k_row in df_k.iterrows():
          st.markdown(f"<div class='kanban-card'><div class='kanban-title'>{k_row['nombre']}</div><div class='kanban-meta'>👤 {k_row['lider_asignado']}</div><div class='kanban-meta'>📈 {int((k_row['avance_real'] or 0)*100)}% Completado</div><div class='kanban-meta' style='margin-top:6px;'><i>Folio: {k_row['folio'] or 'S/F'}</i></div></div>", unsafe_allow_html=True)

# PESTAÑAS ADMINISTRATIVAS (SOLO MODERADORES)
if es_moderador:
  # PESTAÑA 4: NUEVO PROYECTO
  with tabs[3]:
    st.write("")
    sub_tab1, sub_tab2 = st.tabs(["📝 Alta Individual", "📥 Carga Masiva desde Excel"])
    
    with sub_tab1:
      with st.form("f_nuevo", clear_on_submit=True):
        st.markdown("<h3 style='font-size:1.15rem; color:#0F172A; margin-bottom:15px;'>Dar de Alta Nuevo Proyecto</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3); folio = c1.text_input("Folio Interno"); nombre = c2.text_input("Nombre de la Iniciativa *"); lider = c3.selectbox("Responsable del Proyecto *", lista_lideres_registrados)
        c4, c5, c6 = st.columns(3); area = c4.selectbox("Área Solicitante", OPCIONES_AREAS); tipo = c5.selectbox("Categoría Principal", OPCIONES_TIPOS); subtipo = c6.selectbox("Sub-categoría", OPCIONES_SUBTIPOS)
        c7, c8, c9 = st.columns(3); gerente = c7.selectbox("Gerente Sponsor", OPCIONES_GERENTES); etapa = c8.selectbox("Fase de Arranque", OPCIONES_ETAPAS); estatus_inicial = c9.selectbox("Estado Inicial", OPCIONES_ESTATUS, index=0)
        
        st.markdown("<h5 style='font-size:0.9rem; color:#0F172A; margin-top:10px;'>Fechas Compromiso Baseline</h5>", unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        f_ini_b = cb1.date_input("Fecha Inicio Baseline", value=datetime.now())
        f_fin_b = cb2.date_input("Fecha Fin Baseline (Compromiso)", value=datetime.now() + timedelta(days=90))

        st.markdown("<h5 style='font-size:0.9rem; color:#0F172A; margin-top:10px;'>Estimación Financiera</h5>", unsafe_allow_html=True)
        cf1, cf2 = st.columns(2)
        presupuesto_in = cf1.number_input("Presupuesto Asignado ($)", min_value=0.0, value=0.0, step=1000.0)
        roi_in = cf2.number_input("Impacto / ROI Estimado ($)", min_value=0.0, value=0.0, step=1000.0)

        if st.form_submit_button("Crear Proyecto", type="primary"):
          if nombre.strip():
            engine = obtener_engine()
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with engine.begin() as conn: 
                res_ins = conn.execute(sqlalchemy.text("""INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real, ultima_actualizacion, presupuesto, roi_estimado, fecha_inicio_baseline, fecha_fin_baseline) VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, 0, :u, :pr, :ro, :fib, :ffb) RETURNING id"""), 
                                                     {"f": folio, "n": nombre, "a": area, "t": tipo, "s": subtipo, "g": gerente, "l": lider, "e": etapa, "st": estatus_inicial, "u": ahora, "pr": presupuesto_in, "ro": roi_in, "fib": str(f_ini_b), "ffb": str(f_fin_b)})
                
                new_id = res_ins.fetchone()[0] if res_ins.returns_rows else None
                if new_id:
                    conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), 
                                 {"p_id": new_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": f"Creación de expediente con Baseline comprometido al {f_fin_b}."})

            limpiar_cache_y_recargar(); st.success("¡Proyecto creado exitosamente!"); st.rerun()
          else: st.error("Por favor ingresa el nombre de la iniciativa.")

    with sub_tab2:
      st.markdown("<h3 style='font-size:1.15rem; color:#0F172A;'>📥 Cargar Portafolio desde Excel o CSV</h3>", unsafe_allow_html=True)
      st.write("Sube un archivo de Excel con múltiples iniciativas para importarlas masivamente.")
      
      df_plantilla = pd.DataFrame([{
          "folio": "INC-101",
          "nombre": "Proyecto Ejemplo Excel",
          "area_negocio": "Incentivos",
          "tipo_proyecto": "Esquema de Incentivos",
          "subtipo": "EI-Nuevo incentivo completo",
          "gerente": "Andres Avila",
          "lider_asignado": "Leonardo Castillo",
          "etapa_actual": "1. Planeación",
          "estatus_tiempo": "En tiempo",
          "avance_real": 0.10,
          "presupuesto": 50000.0,
          "roi_estimado": 120000.0,
          "fecha_inicio_baseline": "2026-01-01",
          "fecha_fin_baseline": "2026-06-30"
      }])
      
      excel_plantilla_buffer = io.BytesIO()
      with pd.ExcelWriter(excel_plantilla_buffer, engine="openpyxl") as writer:
          df_plantilla.to_excel(writer, index=False, sheet_name="Plantilla")
          
      st.download_button(
          "📄 Descargar Plantilla Excel Oficial",
          data=excel_plantilla_buffer.getvalue(),
          file_name="Plantilla_Importacion_Heading360.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          type="secondary"
      )
      st.divider()
      
      archivo_subido = st.file_uploader("Selecciona tu archivo de Excel o CSV", type=["xlsx", "xls", "csv"])
      if archivo_subido is not None:
          try:
              if archivo_subido.name.endswith(".csv"): df_excel = pd.read_csv(archivo_subido)
              else: df_excel = pd.read_excel(archivo_subido)
                  
              st.markdown("##### Previsualización de los Datos a Importar:")
              st.dataframe(df_excel, use_container_width=True)
              
              if st.button("🚀 Importar Proyectos a la Base de Datos", type="primary"):
                  engine = obtener_engine()
                  ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  registros_guardados = 0
                  with engine.begin() as conn:
                      for _, row in df_excel.iterrows():
                          res_imp = conn.execute(
                              sqlalchemy.text("""INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real, ultima_actualizacion, presupuesto, roi_estimado, fecha_inicio_baseline, fecha_fin_baseline) 
                                                 VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, :av, :u, :pr, :ro, :fib, :ffb) RETURNING id"""),
                              {
                                  "f": str(row.get("folio", "S/F")),
                                  "n": str(row.get("nombre", "Proyecto Importado")),
                                  "a": str(row.get("area_negocio", "Incentivos")),
                                  "t": str(row.get("tipo_proyecto", "Estratégicos")),
                                  "s": str(row.get("subtipo", "Otros")),
                                  "g": str(row.get("gerente", "Andres Avila")),
                                  "l": str(row.get("lider_asignado", "Leonardo Castillo")),
                                  "e": str(row.get("etapa_actual", "1. Planeación")),
                                  "st": str(row.get("estatus_tiempo", "En tiempo")),
                                  "av": float(row.get("avance_real", 0.0)),
                                  "u": ahora,
                                  "pr": float(row.get("presupuesto", 0.0)),
                                  "ro": float(row.get("roi_estimado", 0.0)),
                                  "fib": str(row.get("fecha_inicio_baseline", datetime.now().strftime("%Y-%m-%d"))),
                                  "ffb": str(row.get("fecha_fin_baseline", (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")))
                              }
                          )
                          imp_id = res_imp.fetchone()[0] if res_imp.returns_rows else None
                          if imp_id:
                              conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), 
                                           {"p_id": imp_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": "Importación masiva desde plantilla Excel."})
                          registros_guardados += 1
                  limpiar_cache_y_recargar()
                  st.success(f"¡Se importaron con éxito {registros_guardados} proyectos!")
                  st.rerun()
          except Exception as e:
              st.error(f"Error al leer el archivo. Usa la plantilla oficial. Detalle: {e}")

  # PESTAÑA 5: BITÁCORA GLOBAL
  with tabs[4]:
    st.write("")
    st.markdown("<h3 style='color:#0F172A;'>📜 Feed Global de Auditoría y Bitácora</h3>", unsafe_allow_html=True)
    st.write("Historial centralizado en tiempo real de todas las actualizaciones ejecutadas en el sistema.")
    
    if df_bitacora.empty:
        st.info("Aún no hay movimientos registrados en la bitácora global.")
    else:
        df_bitacora_ext = df_bitacora.merge(df[["id", "nombre", "folio"]], left_on="proyecto_id", right_on="id", how="left")
        for _, b_row in df_bitacora_ext.head(30).iterrows():
            p_nombre = b_row.get("nombre", "Proyecto General")
            p_folio = b_row.get("folio", "S/F")
            st.markdown(f"""
            <div style='background-color:#FFFFFF; border:1px solid #E2E8F0; padding:14px 18px; border-radius:12px; margin-bottom:10px;'>
                <div style='font-size:0.8rem; color:#64748B; font-weight:600;'>{b_row['fecha_hora']} | Autor: <b style='color:#0F172A;'>{b_row['usuario_nombre']}</b> | Proyecto: <b style='color:#2563EB;'>[{p_folio}] {p_nombre}</b></div>
                <div style='font-size:0.9rem; color:#334155; margin-top:4px;'>{b_row['comentario']}</div>
            </div>
            """, unsafe_allow_html=True)

  # PESTAÑA 6: DIRECTORIO Y GESTIÓN DE USUARIOS (SIMETRÍA PERFECTA)
  with tabs[5]:
    st.write("")
    df_users = df_users_raw.copy()
    df_users.columns = ["Colaborador", "Correo Corporativo", "Contraseña", "Nivel de Acceso"]

    col_table, col_forms = st.columns([1.3, 1])
    with col_table:
      st.markdown("<h4 style='margin-bottom:12px; font-size:1.1rem;'>👥 Directorio de Usuarios Activos</h4>", unsafe_allow_html=True)
      st.dataframe(
          df_users,
          use_container_width=True,
          hide_index=True,
          column_config={
              "Colaborador": st.column_config.TextColumn("Colaborador", width="medium"),
              "Correo Corporativo": st.column_config.TextColumn("Correo Corporativo", width="large"),
              "Contraseña": st.column_config.TextColumn("Contraseña", width="small"),
              "Nivel de Acceso": st.column_config.TextColumn("Rol", width="small"),
          }
      )

    with col_forms:
      st.markdown("<h4 style='margin-bottom:12px; font-size:1.1rem;'>⚙️ Gestión de Accesos</h4>", unsafe_allow_html=True)
      
      sub_u1, sub_u2, sub_u3 = st.tabs(["✏️ Editar Perfil", "➕ Nuevo Usuario", "🗑️ Revocar"])
      
      with sub_u1:
        lista_correos_all = df_users_raw["correo"].tolist() if not df_users_raw.empty else []
        u_sel_correo = st.selectbox("Seleccionar Usuario", ["Seleccionar..."] + lista_correos_all, key="sel_mod_user")
        
        if u_sel_correo != "Seleccionar...":
            u_info = df_users_raw[df_users_raw["correo"] == u_sel_correo].iloc[0]
            with st.form("f_edit_user"):
                e_nom = st.text_input("Nombre Completo", value=u_info["nombre"])
                e_pas = st.text_input("Contraseña", value=u_info["password"])
                e_rol = st.selectbox("Perfil de Seguridad", ["Usuario", "Moderador"], index=0 if u_info["rol"]=="Usuario" else 1)
                if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
                    engine = obtener_engine()
                    with engine.begin() as conn:
                        conn.execute(sqlalchemy.text("UPDATE usuarios SET nombre=:n, password=:p, rol=:r WHERE correo=:c"),
                                     {"n": e_nom, "p": e_pas, "r": e_rol, "c": u_sel_correo})
                    limpiar_cache_y_recargar(); st.success("¡Perfil actualizado!"); st.rerun()

      with sub_u2:
        with st.form("f_alta"):
          n_nom = st.text_input("Nombre Completo")
          n_cor = st.text_input("Correo (@coppel.com)")
          n_pas = st.text_input("Contraseña Inicial")
          n_rol = st.selectbox("Perfil de Seguridad", ["Usuario", "Moderador"])
          if st.form_submit_button("Registrar Usuario", type="primary", use_container_width=True):
            if n_cor and n_pas and n_nom:
              try:
                engine = obtener_engine()
                with engine.begin() as conn: conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES (:c, :p, :r, :n)"), {"c": n_cor.strip().lower(), "p": n_pas, "r": n_rol, "n": n_nom})
                limpiar_cache_y_recargar(); st.success("Usuario agregado."); st.rerun()
              except Exception: st.error("El correo ya se encuentra registrado.")

      with sub_u3:
        with st.form("f_baja"):
          lista_correos = df_users["Correo Corporativo"].tolist()
          if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
          correo_borrar = st.selectbox("Seleccionar a Eliminar:", ["Seleccionar..."] + lista_correos)
          if st.form_submit_button("Eliminar Acceso", type="secondary", use_container_width=True):
            if correo_borrar != "Seleccionar...":
              engine = obtener_engine()
              with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM usuarios WHERE correo=:c"), {"c": correo_borrar})
              limpiar_cache_y_recargar(); st.success("Acceso revocado."); st.rerun()


# ==============================================================================
# --- MOTOR NLP PROJECT IA ---
# ==============================================================================
def consultar_ia_ultra_rapido(prompt, dataframe, usuario_nombre="Colaborador"):
  p_lower = prompt.lower().strip()
  p_clean = p_lower.replace("?", "").replace("¿", "").replace("!", "").replace("¡", "").strip()
  
  if p_clean in ["gracias", "muchas gracias", "excelente", "perfecto", "ok", "entendido", "vale", "va", "listo"]:
      return "¡Con mucho gusto! 🚀 Quedo por aquí por si necesitas consultar algo más."
      
  if any(x == p_clean for x in ["como estas", "como andas", "todo bien", "que tal", "como te va"]):
      return f"¡Hola **{usuario_nombre}**, operando al 100%! ✨ ¿De qué proyecto, financiero o colaborador te gustaría conocer los avances hoy?"
      
  if any(x in p_clean for x in ["quien eres", "que haces", "para que sirves", "quien sos"]):
      return "Soy **Project IA**, tu asistente inteligente dentro de Heading 360. Mi función es ayudarte a consultar información en tiempo real, incluyendo análisis de riesgos y presupuestos.\n\nPuedes preguntarme:\n* *¿Qué proyectos están estancados o corren riesgo?*\n* *¿Cuál es el presupuesto total del portafolio?*\n* *¿En qué estatus están los proyectos?*"

  if p_clean in ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "saludos", "hola bot", "hola project ia"]:
      tot = len(dataframe)
      ret = len(dataframe[dataframe["estatus_calculado"].isin(["Retrasado", "Detenido"])]) if not dataframe.empty else 0
      resp = f"¡Hola, **{usuario_nombre}**! 👋 Qué gusto saludarte.\n\nActualmente administro **{tot} proyectos activos**. "
      if ret > 0: resp += f"⚠️ Noté que hay **{ret} proyectos retrasados vs. su Baseline**. ¿Te gustaría que te muestre cuáles son?"
      else: resp += "Por fortuna, no tenemos ningún proyecto retrasado. ¿Qué te gustaría consultar hoy?"
      return resp

  p_analizar = p_lower
  for s in ["hola ", "buenos dias ", "buenas tardes ", "por favor ", "dime ", "quiero saber ", "quisiera saber ", "me puedes decir "]:
      if p_analizar.startswith(s): p_analizar = p_analizar[len(s):].strip()

  if dataframe.empty: return "Actualmente no tenemos proyectos registrados en el portafolio."

  busca_riesgo_predictivo = any(k in p_analizar for k in ["riesgo", "estancado", "cuello de botella", "prediccion", "parado", "peligro"])
  if busca_riesgo_predictivo:
      estancados = dataframe[dataframe.get('es_estancado', False) == True]
      retrasados = dataframe[dataframe['estatus_calculado'].isin(["Retrasado", "Detenido"])]
      
      res = "🔮 **Diagnóstico Predictivo de Riesgos en el Portafolio:**\n\n"
      if estancados.empty and retrasados.empty:
          res += "🟢 **Estado Saludable:** No se detectan cuellos de botella ni desviaciones negativas vs Baseline."
      else:
          if not retrasados.empty:
              res += f"🚨 **{len(retrasados)} Proyecto(s) en Retraso Crítico vs Baseline:**\n"
              for _, r in retrasados.iterrows(): res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}** (`{r['estatus_calculado']}`)\n"
              res += "\n"
          if not estancados.empty:
              res += f"⚠️ **{len(estancados)} Proyecto(s) Estancado(s) (>20 días sin actualización):**\n"
              for _, r in estancados.iterrows(): res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}** (Últ. act: {r['ultima_actualizacion'] or 'N/A'})\n"
      return res

  busca_finanzas = any(k in p_analizar for k in ["presupuesto", "dinero", "costo", "roi", "inversion", "cuanto cuesta", "impacto financiero"])
  if busca_finanzas:
      p_tot = dataframe['presupuesto'].sum()
      r_tot = dataframe['roi_estimado'].sum()
      res = f"💰 **Análisis Financiero del Portafolio:**\n\n* **Presupuesto Total Invertido:** `${p_tot:,.2f}`\n* **Impacto / ROI Estimado:** `${r_tot:,.2f}`\n* **Retorno Neto Proyectado:** `${(r_tot - p_tot):,.2f}`\n\n"
      top_p = dataframe.sort_values(by="presupuesto", ascending=False).head(3)
      res += "📌 **Proyectos con Mayor Inversión:**\n"
      for _, r in top_p.iterrows(): res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**: `${r['presupuesto']:,.2f}` (ROI: `${r['roi_estimado']:,.2f}`)\n"
      return res

  busca_estatus_general = any(k in p_analizar for k in ["estatus", "estado", "etapa", "fase", "como van"])
  busca_retrasos = any(k in p_analizar for k in ["retras", "riesgo", "deteni", "critico", "problema", "urgente", "foco rojo"])
  
  if busca_estatus_general and not busca_retrasos and not any(a.lower() in p_analizar for a in OPCIONES_AREAS):
      res = f"📌 **Estatus actual de los proyectos en el portafolio ({len(dataframe)}):**\n\n"
      for _, r in dataframe.iterrows():
          pct = int((r['avance_real'] or 0) * 100)
          badge = "🟢" if r['estatus_calculado'] == "En tiempo" else ("⚠️" if r['estatus_calculado'] in ["Retrasado", "Detenido"] else "⚪")
          res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**\n  * {badge} **Estatus:** `{r['estatus_calculado']}` | 📍 **Fase:** {r['etapa_actual']}\n  * 👤 **Líder:** {r['lider_asignado']} | 📈 **Avance:** {pct}%\n\n"
      return res

  busca_top_lider = any(k in p_analizar for k in ["quien", "quién", "lider", "líder", "responsable", "persona", "encargado", "colaborador"]) and any(k in p_analizar for k in ["mas", "más", "mayor", "top", "tiene", "carga"])
  if busca_top_lider and not busca_retrasos:
      counts = dataframe["lider_asignado"].value_counts()
      if not counts.empty:
          top_l = counts.index[0]; top_val = counts.iloc[0]
          res = f"Analizando la base de datos, **{top_l}** es la persona con mayor carga operativa, teniendo **{top_val} iniciativas** asignadas.\n\n📌 **Distribución por líder:**\n"
          for l_name, val in counts.items(): res += f"* **{l_name}**: {val} proyecto(s)\n"
          return res

  busca_top_area = any(k in p_analizar for k in ["area", "área", "departamento"]) and any(k in p_analizar for k in ["mas", "más", "mayor", "top", "tiene"])
  if busca_top_area:
      counts = dataframe["area_negocio"].value_counts()
      if not counts.empty:
          top_a = counts.index[0]; top_val = counts.iloc[0]
          res = f"El área que concentra más proyectos es **{top_a}**, con **{top_val} iniciativas**.\n\n📌 **Desglose por área:**\n"
          for a_name, val in counts.items(): res += f"* **{a_name}**: {val} proyectos\n"
          return res

  area_obj = next((a for a in OPCIONES_AREAS if a.lower() in p_analizar), None)
  lideres_y_gerentes = set(obtener_lista_usuarios(df_users_raw) + OPCIONES_GERENTES)
  persona_obj = next((p for p in lideres_y_gerentes if len(p) > 3 and p.lower() in p_analizar), None)

  df_result = dataframe.copy()
  criterios = []
  
  if area_obj: df_result = df_result[df_result['area_negocio'] == area_obj]; criterios.append(f"Área: **{area_obj}**")
  if persona_obj: df_result = df_result[(df_result["lider_asignado"] == persona_obj) | (df_result["gerente"] == persona_obj)]; criterios.append(f"Involucrado: **{persona_obj}**")
  if busca_retrasos: df_result = df_result[df_result["estatus_calculado"].isin(["Retrasado", "Detenido"])]; criterios.append("Estatus: **Retrasado**")

  if len(criterios) > 0:
      if df_result.empty: return f"🔍 No encontré proyectos con tus filtros: " + " | ".join(criterios)
      res = f"🔍 **Resultados de la búsqueda** (" + " | ".join(criterios) + f"):\n\nEncontré **{len(df_result)}** proyectos:\n\n"
      for _, r in df_result.iterrows(): res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**\n  * 👤 **Líder:** {r['lider_asignado']} | 📌 **Estatus:** `{r['estatus_calculado']}` | 📈 **Avance:** {int((r['avance_real'] or 0)*100)}%\n\n"
      return res

  coincidencias = dataframe[dataframe["nombre"].str.lower().str.contains(p_analizar, na=False) | dataframe["folio"].str.lower().str.contains(p_analizar, na=False)]
  if not coincidencias.empty:
      res = f"🔍 Encontré **{len(coincidencias)} proyectos** asociados a tu consulta:\n\n"
      for _, r in coincidencias.iterrows(): res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**\n  * 👤 **Líder:** {r['lider_asignado']} | 📌 **Estatus:** `{r['estatus_calculado']}` | 📈 **Avance:** {int((r['avance_real'] or 0)*100)}%\n\n"
      return res

  res_general = f"📋 **Estatus general de tus proyectos ({len(dataframe)}):**\n\n"
  for _, r in dataframe.iterrows(): res_general += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}** — `{r['estatus_calculado']}` ({int((r['avance_real'] or 0)*100)}% avance)\n"
  return res_general

# --- WIDGET FLOTANTE FIJO EXCLUSIVO PROJECT IA (BOTTOM-RIGHT) ---
st.markdown('<div class="floating-ia-box">', unsafe_allow_html=True)
with st.popover("🤖 Project IA", help="Haz clic para consultar con tu asistente analítico"):
  col1, col2 = st.columns([3, 1])
  with col1: st.markdown("<h3 style='color:#0F172A; margin-bottom: 0px; font-weight:800;'>🤖 Project IA</h3>", unsafe_allow_html=True)
  with col2:
      if st.button("🧹 Borrar", help="Limpiar conversación"):
          st.session_state.chat_history_fast = []; st.rerun()
          
  st.caption("Asistente Analítico Heading 360.")
  st.divider()

  mensaje_bienvenida = {"role": "assistant", "content": f"¡Hola **{st.session_state.nombre_actual}**! 👋 Soy **Project IA**. ¿Qué te gustaría consultar del portafolio hoy?"}

  if "chat_history_fast" not in st.session_state or len(st.session_state.chat_history_fast) == 0:
    st.session_state.chat_history_fast = [mensaje_bienvenida]

  chat_box = st.container(height=350)
  prompt_fast = st.chat_input("Escribe tu consulta...", key="ia_fast_input")
  
  if prompt_fast:
      st.session_state.chat_history_fast.append({"role": "user", "content": prompt_fast})
      ans = consultar_ia_ultra_rapido(prompt_fast, df, st.session_state.nombre_actual)
      st.session_state.chat_history_fast.append({"role": "assistant", "content": ans})
  else:
      st.session_state.chat_history_fast = [mensaje_bienvenida]

  with chat_box:
    for msg in st.session_state.chat_history_fast:
      avatar_img = URL_ROBOT if msg["role"] == "assistant" else URL_USER
      with st.chat_message(msg["role"], avatar=avatar_img): st.markdown(msg["content"])
st.markdown('</div>', unsafe_allow_html=True)
