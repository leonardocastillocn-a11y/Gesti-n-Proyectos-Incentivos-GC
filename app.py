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
    page_title="Heading 360 | Project Steering Engine",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- AVATARES PREMIUM ---
URL_ROBOT = "https://cdn-icons-png.flaticon.com/512/8943/8943377.png" 
URL_USER = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# --- CSS UX FRIENDLY & SAAS PREMIUM ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp { 
        font-family: 'Inter', sans-serif !important; 
        background-color: #F4F6F9 !important; 
        color: #1E293B !important; 
    }
    
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0 !important; 
        box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important;
    }
    
    h1, h2, h3, h4, h5, h6 { 
        color: #0F172A !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.02em !important; 
    }
    
    label { 
        color: #64748B !important; 
        font-weight: 600 !important; 
        font-size: 0.8rem !important; 
        text-transform: uppercase; 
        letter-spacing: 0.03em; 
    }
    
    /* INPUTS LIMPIOS Y REDONDEADOS */
    .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div, .stNumberInput > div > div { 
        border-radius: 8px !important; 
        border: 1px solid #CBD5E1 !important; 
        background-color: #F8FAFC !important; 
        transition: all 0.2s ease; 
    }
    .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within, .stNumberInput > div > div:focus-within { 
        border-color: #05297A !important; 
        box-shadow: 0 0 0 2px rgba(5, 41, 122, 0.15) !important; 
        background-color: #FFFFFF !important; 
    }
    
    /* TARJETAS DE FORMULARIOS */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        padding: 24px !important;
    }

    /* BOTONES PRIMARIOS */
    div[data-testid="stFormSubmitButton"] button, .stButton > button[kind="primary"] { 
        background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important; 
        color: #FFFFFF !important; 
        border: none !important; 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        padding: 0.5rem 1rem !important; 
        box-shadow: 0 4px 6px -1px rgba(28, 66, 232, 0.2) !important; 
        transition: all 0.3s ease !important; 
    }
    div[data-testid="stFormSubmitButton"] button:hover, .stButton > button[kind="primary"]:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 8px 15px -3px rgba(28, 66, 232, 0.3) !important; 
    }
    
    /* BOTONES SECUNDARIOS */
    button[data-testid="baseButton-secondary"], .stButton > button[kind="secondary"] { 
        background-color: #FFFFFF !important; 
        border: 1px solid #CBD5E1 !important; 
        color: #334155 !important; 
        border-radius: 8px !important; 
        font-weight: 500 !important; 
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important; 
    }
    button[data-testid="baseButton-secondary"]:hover, .stButton > button[kind="secondary"]:hover { 
        border-color: #05297A !important; 
        color: #05297A !important; 
        background-color: #F8FAFC !important; 
    }
    
    /* MÉTRICAS SUAVES */
    div[data-testid="metric-container"] { 
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important; 
        border-top: 4px solid #05297A !important; 
        padding: 20px 24px !important; 
        border-radius: 12px !important; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03) !important; 
    }
    div[data-testid="metric-container"] label { color: #64748B !important; font-size: 0.85rem !important; font-weight: 600 !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] div { color: #0F172A !important; font-size: 2rem !important; font-weight: 800 !important; letter-spacing: -0.02em; }
    
    /* PESTAÑAS (TABS) AMIGABLES */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #05297A !important; font-weight: 700 !important; color: #05297A !important; background-color: transparent !important; }
    .stTabs [aria-selected="false"] { color: #64748B !important; font-weight: 500 !important; }
    
    /* ACORDEONES LIMPIOS */
    .streamlit-expanderHeader { background-color: #FFFFFF !important; color: #0F172A !important; font-weight: 600 !important; border-radius: 10px !important; border: 1px solid #E2E8F0 !important; padding: 1rem !important; box-shadow: 0 2px 4px rgba(0,0,0,0.01) !important; }
    .streamlit-expanderContent { border: 1px solid #E2E8F0 !important; border-top: none !important; background-color: #FFFFFF !important; padding: 24px !important; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }
    
    /* BADGES STATUS REDONDEADAS */
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; letter-spacing: 0.02em; }
    .status-green { background-color: #DCFCE7; color: #166534 !important; border: 1px solid #BBF7D0;}
    .status-yellow { background-color: #FEF9C3; color: #854D0E !important; border: 1px solid #FEF08A;}
    .status-red { background-color: #FEE2E2; color: #991B1B !important; border: 1px solid #FCA5A5;}
    .status-gray { background-color: #F1F5F9; color: #475569 !important; border: 1px solid #E2E8F0;}
    
    /* KANBAN CARDS */
    .kanban-card { background: #FFFFFF; padding: 16px; border-radius: 12px; border: 1px solid #E2E8F0; border-left: 4px solid #05297A; box-shadow: 0 2px 5px rgba(0,0,0,0.02); margin-bottom: 15px; transition: transform 0.2s; }
    .kanban-card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.05); }
    .kanban-title { font-weight: 700; color: #0F172A; font-size: 0.95rem; margin-bottom: 8px; }
    .kanban-meta { font-size: 0.8rem; color: #64748B; margin-bottom: 4px; }
    
    /* LOGIN LIMPIO */
    .login-box { background-color: #FFFFFF; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; }
    
    /* BOTÓN FLOTANTE "PROJECT IA" */
    div[data-testid="stPopover"] { position: fixed !important; bottom: 30px !important; right: 30px !important; z-index: 999999 !important; }
    div[data-testid="stPopover"] > button { 
        background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important; 
        color: #FFFFFF !important; 
        border-radius: 50px !important; 
        padding: 12px 24px !important; 
        box-shadow: 0 8px 20px rgba(5, 41, 122, 0.3) !important; 
        border: 2px solid #FFFFFF !important; 
        font-size: 0.95rem !important; 
        font-weight: 600 !important; 
        transition: all 0.3s ease !important; 
    }
    div[data-testid="stPopover"] > button:hover { 
        transform: scale(1.05) translateY(-3px) !important; 
        box-shadow: 0 12px 25px rgba(28, 66, 232, 0.4) !important; 
    }
    div[data-testid="stPopover"] > button p { color: #FFFFFF !important; font-weight: 600 !important; margin: 0; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONSTANTES ---
OPCIONES_AREAS = ["Incentivos", "Afore", "Banca Empresarial", "Banco", "CAT Cobranza", "CAT P&V", "CEDIS", "Cobranza Domiciliaria", "Credito Automotriz", "Inmobiliaria", "Retail", "Sale Vale"]
OPCIONES_TIPOS = ["Esquema de Incentivos", "Tecnología", "Estratégicos", "Procesos", "Campañas", "Auditorías"]
OPCIONES_SUBTIPOS = ["EI-Nuevo incentivo completo", "EI-Actualización completa de incentivo", "EI-Ajuste menor de incentivo", "EI-Ajuste mayor de incentivo", "EI-Casos especiales", "CA-Campaña", "CA-Concurso", "PR-Documentación oficial", "PR-Nuevo proceso", "TE-Software", "TE-Tableros", "Otros"]
OPCIONES_ETAPAS = ["1. Diseño (EI)", "2. Prueba piloto (EI)", "3. Escalamiento nacional (EI)", "4. Cierre (EI)", "1. Diseño (CA)", "2. Implementación (CA)", "3. Evaluación y cierre (CA)", "4. Cierre (CA)", "1. Planeación", "2. Ejecución", "3. Cierre"]
OPCIONES_ESTATUS = ["Por iniciar", "En tiempo", "Retrasado", "Detenido", "Cancelado"]
OPCIONES_GERENTES = ["Andres Avila", "Eduardo Rodriguez", "Heriberto Vega", "Janik Orozco", "Kurokusi Ochoa", "Noel Aquino", "Yahir Ramirez", "Giovanni Vallejo", "Ruben Rivera"]

# --- BASE DE DATOS Y CACHÉ ---
@st.cache_resource
def obtener_engine():
  db_url = st.secrets["postgres"]["url"] if "postgres" in st.secrets else "sqlite:///db_coppel_v5.db"
  return sqlalchemy.create_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)

def inicializar_db():
  engine = obtener_engine()
  with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS proyectos (id SERIAL PRIMARY KEY, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT, tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT, etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT, presupuesto REAL DEFAULT 0.0, roi_estimado REAL DEFAULT 0.0)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS tareas (id SERIAL PRIMARY KEY, proyecto_id INTEGER, nombre_tarea TEXT NOT NULL, responsable TEXT, fecha_inicio TEXT, duracion_dias INTEGER, fecha_fin TEXT, porcentaje_avance REAL, predecesoras TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS bitacora (id SERIAL PRIMARY KEY, proyecto_id INTEGER, usuario_nombre TEXT, fecha_hora TEXT, comentario TEXT)"""))
    
    try:
      conn.execute(sqlalchemy.text("ALTER TABLE proyectos ADD COLUMN presupuesto REAL DEFAULT 0.0"))
    except Exception: pass
    try:
      conn.execute(sqlalchemy.text("ALTER TABLE proyectos ADD COLUMN roi_estimado REAL DEFAULT 0.0"))
    except Exception: pass

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
  
  if 'presupuesto' not in df_p.columns: df_p['presupuesto'] = 0.0
  if 'roi_estimado' not in df_p.columns: df_p['roi_estimado'] = 0.0
  df_p['presupuesto'] = df_p['presupuesto'].fillna(0.0)
  df_p['roi_estimado'] = df_p['roi_estimado'].fillna(0.0)
  
  return df_p, df_b, df_t, df_u

def limpiar_cache_y_recargar():
  cargar_datos_completos.clear()

def obtener_lista_usuarios(df_u):
  return df_u["nombre"].tolist() if not df_u.empty else ["Leonardo Castillo"]

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
  if not fecha_actualizacion_str or str(fecha_actualizacion_str).strip() in ["", "None", "N/A"]:
    return True
  try:
    f_act = datetime.strptime(str(fecha_actualizacion_str)[:19], "%Y-%m-%d %H:%M:%S")
    dias = (datetime.now() - f_act).days
    return dias > 20
  except Exception:
    return False

# --- LOGIN GATEWAY ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False; st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
  col_izq, col_centro, col_der = st.columns([1, 1.4, 1])
  with col_centro:
    st.write(""); st.write(""); st.write("")
    st.markdown("<h1 style='text-align: center; color:#05297A !important; font-size: 2.5rem; letter-spacing: -1px;'>HEADING 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 30px; font-size: 1.1rem; font-weight: 500;'>Project Steering Engine</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
      st.markdown("<h3 style='color:#0F172A !important; font-size: 1.2rem; margin-bottom: 20px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
      correo_input = st.text_input("Correo Institucional", placeholder="tu.nombre@coppel.com")
      password_input = st.text_input("Contraseña", type="password")
      st.write("")
      if st.form_submit_button("Ingresar al sistema", type="primary", use_container_width=True):
        if correo_input.strip() == "": st.warning("Por favor ingresa tu correo.")
        else:
          engine = obtener_engine()
          with engine.connect() as conn:
            res = conn.execute(sqlalchemy.text("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=:c"), {"c": correo_input.strip().lower()}).fetchone()
            if res and res[0] == password_input:
              st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower(); st.session_state.rol = res[1]; st.session_state.nombre_actual = res[2]; st.rerun()
            else: st.error("Tus credenciales no coinciden. Intenta de nuevo.")
    
    st.write("")
    if st.button("¿Olvidaste tu contraseña?", type="secondary", use_container_width=True):
        st.info("🔒 **Seguridad de la cuenta:** Para recuperar tu contraseña, envía un correo al administrador del sistema (Leonardo Castillo) para que te asigne una nueva clave.")
  st.stop()

# --- CARGA DE DATOS EN MEMORIA ---
df, df_bitacora, df_tareas_all, df_users_raw = cargar_datos_completos()
es_moderador = st.session_state.rol == "Moderador"
lista_lideres_registrados = obtener_lista_usuarios(df_users_raw)

# Identificación de Proyectos Estancados (>20 días sin movimientos)
if not df.empty:
  df['es_estancado'] = df['ultima_actualizacion'].apply(evaluar_estancamiento) & (~df['etapa_actual'].str.contains("Cierre", case=False, na=False))
  proyectos_estancados = df[df['es_estancado']]
  proyectos_retrasados = df[df["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
  
  if not proyectos_retrasados.empty and "alerta_mostrada" not in st.session_state:
    st.toast(f"¡Hola! Tienes {len(proyectos_retrasados)} iniciativas que requieren atención por retraso.", icon="🚨")
    st.session_state.alerta_mostrada = True
else:
  df['es_estancado'] = False
  proyectos_estancados = pd.DataFrame()
  proyectos_retrasados = pd.DataFrame()

# --- SIDEBAR DE USUARIO ---
with st.sidebar:
  st.markdown(f"<div style='background-color:#FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);'><h3 style='margin:0 0 4px 0; font-size:1.1rem; color:#0F172A;'>👤 {st.session_state.nombre_actual}</h3><p style='margin:0 0 10px 0; color:#64748B; font-size:0.85rem;'>{st.session_state.correo_actual}</p><span class='status-badge {'status-green' if es_moderador else 'status-gray'}'>{st.session_state.rol}</span></div>", unsafe_allow_html=True)
  with st.expander("⚙️ Mi Perfil y Seguridad", expanded=False):
    with st.form("form_cambio_pass"):
      nueva_pass = st.text_input("Nueva Contraseña", type="password"); confirmar_pass = st.text_input("Confirmar Contraseña", type="password")
      if st.form_submit_button("Guardar Cambios", use_container_width=True):
        if nueva_pass == confirmar_pass and nueva_pass:
          engine = obtener_engine()
          with engine.begin() as conn: conn.execute(sqlalchemy.text("UPDATE usuarios SET password=:p WHERE correo=:c"), {"p": nueva_pass, "c": st.session_state.correo_actual})
          limpiar_cache_y_recargar(); st.success("¡Contraseña actualizada!")
        else: st.error("Las contraseñas no coinciden.")
  st.write("")
  st.markdown("<h4 style='color:#0F172A; font-size: 0.9rem;'>📥 Exportar Información</h4>", unsafe_allow_html=True)
  if not df.empty:
    def generar_pdf(dataframe):
      pdf = FPDF(orientation="L", unit="mm", format="A4"); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page(); pdf.set_font("Arial", "B", 16); pdf.set_text_color(5, 41, 122)
      pdf.cell(0, 8, "Heading 360 - Reporte de Portafolio", ln=True, align="L"); pdf.set_font("Arial", "", 9); pdf.set_text_color(100, 100, 100)
      pdf.cell(0, 6, f"Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", ln=True, align="L"); pdf.ln(4)
      pdf.set_font("Arial", "B", 8); pdf.set_fill_color(241, 245, 249); pdf.set_text_color(15, 23, 42)
      pdf.cell(22, 8, "Folio", 1, 0, "C", True); pdf.cell(60, 8, "Iniciativa", 1, 0, "L", True); pdf.cell(30, 8, "Area", 1, 0, "L", True); pdf.cell(35, 8, "Responsable", 1, 0, "L", True); pdf.cell(25, 8, "Estatus", 1, 0, "C", True); pdf.cell(18, 8, "Avance", 1, 0, "C", True); pdf.cell(42, 8, "Ult. Act.", 1, 0, "C", True); pdf.cell(45, 8, "Fase Actual", 1, 1, "L", True)
      pdf.set_font("Arial", "", 8); pdf.set_text_color(40, 40, 40)
      for _, row in dataframe.iterrows():
        pdf.cell(22, 7, str(row["folio"])[:12], 1, 0, "C"); pdf.cell(60, 7, str(row["nombre"])[:35], 1, 0, "L"); pdf.cell(30, 7, str(row["area_negocio"])[:18], 1, 0, "L"); pdf.cell(35, 7, str(row["lider_asignado"])[:22], 1, 0, "L"); pdf.cell(25, 7, str(row["estatus_tiempo"])[:15], 1, 0, "C"); pdf.cell(18, 7, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, "C"); pdf.set_font("Arial", "B", 8); pdf.cell(42, 7, str(row["ultima_actualizacion"])[:19], 1, 0, "C"); pdf.set_font("Arial", "", 8); pdf.cell(45, 7, str(row["etapa_actual"])[:25], 1, 1, "L")
      with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp: pdf.output(tmp.name); return tmp.name

    with open(generar_pdf(df), "rb") as file: st.download_button("Descargar PDF", data=file, file_name=f"Heading360_{datetime.now().strftime('%Y%m%d')}.pdf", use_container_width=True, type="secondary")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer: df.to_excel(writer, index=False, sheet_name="Proyectos")
    st.download_button("Exportar a Excel (.xlsx)", data=excel_buffer.getvalue(), file_name=f"Base_Datos_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="secondary")

  st.write("")
  if st.button("Cerrar Sesión", use_container_width=True): st.session_state.autenticado = False; st.rerun()

# --- HEADER Y MÉTRICAS GENERALES + FINANCIERAS ---
st.markdown("<h2 style='margin-bottom: 20px; color:#0F172A;'>📊 Visión General del Portafolio</h2>", unsafe_allow_html=True)
if not df.empty and not proyectos_retrasados.empty:
  st.markdown(f"<div style='background-color:#FEF2F2; border-left: 5px solid #EF4444; padding: 16px; border-radius: 8px; margin-bottom: 20px;'><p style='color:#991B1B; margin:0; font-weight:600;'>⚠️ Tienes {len(proyectos_retrasados)} iniciativas en Retraso y {len(proyectos_estancados)} estancadas sin movimientos recientes.</p></div>", unsafe_allow_html=True)

total_p = len(df); en_t = len(df[df["estatus_tiempo"] == "En tiempo"]) if total_p > 0 else 0; ret = len(proyectos_retrasados) if total_p > 0 else 0
presupuesto_total = df["presupuesto"].sum() if total_p > 0 else 0.0
roi_total = df["roi_estimado"].sum() if total_p > 0 else 0.0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("PROYECTOS ACTIVOS", total_p)
m2.metric("EN TIEMPO", en_t)
m3.metric("EN RETRASO", ret)
m4.metric("PRESUPUESTO", f"${presupuesto_total:,.2f}")
m5.metric("IMPACTO / ROI EST.", f"${roi_total:,.2f}")
st.write("")

# --- PESTAÑAS CORPORATIVAS ---
if es_moderador: tabs = st.tabs(["📈 Dashboard Analítico", "🚀 Seguimiento de Proyectos", "📋 Tablero Kanban", "➕ Nuevo Proyecto", "📜 Bitácora General", "👥 Directorio de Accesos"])
else: tabs = st.tabs(["📈 Dashboard Analítico", "🚀 Seguimiento de Proyectos", "📋 Tablero Kanban", "➕ Nuevo Proyecto", "📜 Bitácora General"])

# PESTAÑA 1: DASHBOARD CON MATRIZ DE CARGA
with tabs[0]:
  st.write("")
  if df.empty: st.info("Agrega algunos proyectos para visualizar los gráficos analíticos.")
  else:
    d_col1, d_col2 = st.columns(2)
    with d_col1:
      fig1 = px.pie(df, names="area_negocio", title="Distribución por Área Solicitante", hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism)
      fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", title_font=dict(size=18, family="Inter", color="#0F172A")); st.plotly_chart(fig1, use_container_width=True)
    with d_col2:
      df_status_count = df["estatus_tiempo"].value_counts().reset_index(); df_status_count.columns = ["Estatus", "Volumen"]
      fig2 = px.bar(df_status_count, x="Estatus", y="Volumen", title="Estatus de Salud del Portafolio", color="Estatus", color_discrete_map={"En tiempo": "#166534", "Retrasado": "#475569", "Detenido": "#854D0E", "Por iniciar": "#94A3B8"})
      fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", title_font=dict(size=18, family="Inter", color="#0F172A")); st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("<h4 style='color:#0F172A; margin-bottom:15px;'>👥 Matriz de Carga de Trabajo y Capacidad por Líder</h4>", unsafe_allow_html=True)
    
    carga_df = df.groupby(["lider_asignado", "estatus_tiempo"]).size().reset_index(name="Cantidad")
    fig_carga = px.bar(carga_df, x="lider_asignado", y="Cantidad", color="estatus_tiempo", title="Proyectos Asignados por Colaborador", barmode="stack", color_discrete_map={"En tiempo": "#166534", "Retrasado": "#EF4444", "Detenido": "#F59E0B", "Por iniciar": "#94A3B8"})
    fig_carga.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="Líder Operativo", yaxis_title="Número de Proyectos")
    st.plotly_chart(fig_carga, use_container_width=True)

# PESTAÑA 2: SEGUIMIENTO DE PROYECTOS (CON ELIMINACIÓN MASIVA)
with tabs[1]:
  if df.empty: st.info("No hay proyectos registrados todavía.")
  else:
    # PANEL DE ELIMINACIÓN MASIVA PARA MODERADORES
    if es_moderador:
      with st.expander("🗑️ Eliminación Masiva de Proyectos", expanded=False):
        st.write("Selecciona los proyectos que deseas eliminar de forma permanente de la base de datos:")
        opciones_proyectos_borrar = df.apply(lambda x: f"{x['id']} - [{x['folio'] or 'S/F'}] {x['nombre']}", axis=1).tolist()
        proyectos_a_borrar = st.multiselect("Marcar proyectos para eliminar", opciones_proyectos_borrar)
        if st.button("🗑️ Eliminar Proyectos Seleccionados", type="secondary"):
            if proyectos_a_borrar:
                ids_borrar = [int(p.split(" - ")[0]) for p in proyectos_a_borrar]
                engine = obtener_engine()
                with engine.begin() as conn:
                    for pid in ids_borrar:
                        conn.execute(sqlalchemy.text("DELETE FROM tareas WHERE proyecto_id = :id"), {"id": pid})
                        conn.execute(sqlalchemy.text("DELETE FROM bitacora WHERE proyecto_id = :id"), {"id": pid})
                        conn.execute(sqlalchemy.text("DELETE FROM proyectos WHERE id = :id"), {"id": pid})
                limpiar_cache_y_recargar()
                st.success(f"¡Se eliminaron {len(ids_borrar)} proyectos correctamente!")
                st.rerun()
            else:
                st.warning("Selecciona al menos un proyecto para borrar.")

    f_pills1, f_pills2, f_pills3, f_pills4 = st.columns([1.2, 1.2, 1.2, 2.4])
    modo_filtro = f_pills1.radio("Filtros Rápidos", ["Ver Todos", "🚨 Solo Retrasados", "⚠️ Estancados (>20d)", "⭐ Mis Proyectos"], horizontal=True)

    st.markdown("<h5 style='color:#334155; margin-top:15px; margin-bottom:15px; font-size:0.9rem;'>Filtros Avanzados</h5>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns(3)
    txt_busqueda = f_col1.text_input("Buscar por Nombre o Folio")
    filtro_area = f_col2.selectbox("Filtrar por Área", ["Todas las Áreas"] + OPCIONES_AREAS)
    filtro_lider = f_col3.selectbox("Responsable del Proyecto", ["Todos los Responsables"] + lista_lideres_registrados)

    f_col4, f_col5, f_col6 = st.columns(3)
    filtro_estatus = f_col4.selectbox("Estatus de Ejecución", ["Todos los Estatus"] + OPCIONES_ESTATUS)
    filtro_gerente = f_col5.selectbox("Gerente Sponsor", ["Todos los Gerentes"] + OPCIONES_GERENTES)
    filtro_etapa = f_col6.selectbox("Fase Actual", ["Todas las Fases"] + OPCIONES_ETAPAS)

    df_filtrado = df.copy()

    if modo_filtro == "🚨 Solo Retrasados": df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
    elif modo_filtro == "⚠️ Estancados (>20d)": df_filtrado = df_filtrado[df_filtrado["es_estancado"] == True]
    elif modo_filtro == "⭐ Mis Proyectos": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == st.session_state.nombre_actual]

    if txt_busqueda.strip(): df_filtrado = df_filtrado[df_filtrado["nombre"].str.lower().str.contains(txt_busqueda.lower(), na=False) | df_filtrado["folio"].str.lower().str.contains(txt_busqueda.lower(), na=False)]
    if filtro_area != "Todas las Áreas": df_filtrado = df_filtrado[df_filtrado["area_negocio"] == filtro_area]
    if filtro_lider != "Todos los Responsables": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == filtro_lider]
    if filtro_estatus != "Todos los Estatus": df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"] == filtro_estatus]
    if filtro_gerente != "Todos los Gerentes": df_filtrado = df_filtrado[df_filtrado["gerente"] == filtro_gerente]
    if filtro_etapa != "Todas las Fases": df_filtrado = df_filtrado[df_filtrado["etapa_actual"] == filtro_etapa]

    st.markdown(f"<p style='color: #64748B; font-size: 0.85rem; margin-top: 15px;'>📌 Mostrando <b>{len(df_filtrado)}</b> de <b>{len(df)}</b> proyectos según tus filtros.</p>", unsafe_allow_html=True)

    for _, row in df_filtrado.iterrows():
      p_id = row["id"]
      badge_status = "status-green" if row["estatus_tiempo"] == "En tiempo" else ("status-yellow" if row["estatus_tiempo"] == "Detenido" else "status-gray")
      tag_estancado = " <span class='status-badge status-red'>⚠️ Estancado (>20d)</span>" if row.get("es_estancado", False) else ""

      with st.expander(f"[{row['folio'] or 'S/F'}] {row['nombre']} — Avance: {int((row['avance_real'] or 0)*100)}%"):
        st.progress(float(row["avance_real"] or 0.0))

        with st.form(f"update_{p_id}"):
          c1, c2, c3 = st.columns(3)
          c1.markdown(f"<p style='margin:0; font-size:0.88rem;'><span style='color:#64748B;'>Responsable:</span> <b style='color:#0F172A;'>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
          c2.markdown(f"<p style='margin:0; font-size:0.88rem;'><span style='color:#64748B;'>Estatus Actual:</span> <span class='status-badge {badge_status}'>{row['estatus_tiempo']}</span>{tag_estancado}</p>", unsafe_allow_html=True)
          c3.markdown(f"<p style='margin:0; font-size:0.88rem; text-align:right;'><span style='color:#64748B;'>Últ. Actualización:</span> <b style='color:#05297A;'>{row['ultima_actualizacion'] or 'N/A'}</b></p>", unsafe_allow_html=True)
          st.divider()

          c_form1, c_form2, c_form3 = st.columns(3)
          u_etapa = c_form1.selectbox("Fase del Proyecto", OPCIONES_ETAPAS, index=(OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0))
          u_estatus = c_form2.selectbox("Estatus de Tiempo", OPCIONES_ESTATUS, index=(OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0))
          u_avance = c_form3.slider("Progreso General (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
          
          f1, f2 = st.columns(2)
          u_presupuesto = f1.number_input("Presupuesto Asignado ($)", min_value=0.0, value=float(row.get("presupuesto", 0.0)), step=1000.0)
          u_roi = f2.number_input("Impacto / ROI Estimado ($)", min_value=0.0, value=float(row.get("roi_estimado", 0.0)), step=1000.0)

          st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#334155; margin-top:8px; margin-bottom:4px;'>AÑADIR COMENTARIO A BITÁCORA</p>", unsafe_allow_html=True)
          u_comentario = st.text_input("Escribe el estatus de la semana...", placeholder="Ej. Se finalizó la fase de documentación...")
          
          l1, l2 = st.columns(2)
          u_carpeta = l1.text_input("Carpeta Drive (URL)", row["carpeta_url"] or "")
          u_plan = l2.text_input("Link a Plan Anexo (Opcional)", row["plan_url"] or "")
          
          st.write("")
          btn1, btn2, btn3 = st.columns([3, 3, 6])
          if btn1.form_submit_button("Guardar Cambios", type="primary"):
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            engine = obtener_engine()
            with engine.begin() as conn:
              conn.execute(sqlalchemy.text("""UPDATE proyectos SET etapa_actual=:e, estatus_tiempo=:s, avance_real=:a, carpeta_url=:c, plan_url=:p, ultima_actualizacion=:u, presupuesto=:pr, roi_estimado=:ro WHERE id=:id"""), 
                           {"e": u_etapa, "s": u_estatus, "a": u_avance, "c": u_carpeta, "p": u_plan, "u": ahora, "pr": u_presupuesto, "ro": u_roi, "id": p_id})
              if u_comentario.strip(): conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), {"p_id": p_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": u_comentario.strip()})
            limpiar_cache_y_recargar(); st.rerun()

          if es_moderador and btn2.form_submit_button("Eliminar Proyecto", type="secondary"):
            engine = obtener_engine()
            with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM proyectos WHERE id=:id"), {"id": p_id})
            limpiar_cache_y_recargar(); st.rerun()

        # Historial de Bitácora
        historial_proyecto = df_bitacora[df_bitacora["proyecto_id"] == p_id]
        if not historial_proyecto.empty:
          st.markdown("<h5 style='margin-top: 15px; color:#0F172A; font-size:1.05rem;'>📜 Historial de Comentarios</h5>", unsafe_allow_html=True)
          for _, h_row in historial_proyecto.iterrows():
            st.markdown(f"<div class='timeline-item'><div class='timeline-date'>{h_row['fecha_hora']} | Por: {h_row['usuario_nombre']}</div><div class='timeline-text'>{h_row['comentario']}</div></div>", unsafe_allow_html=True)

        # GANTT CHART
        st.markdown("<h4 style='color:#0F172A; margin-top: 30px; padding-top: 15px; border-top: 1px dashed #CBD5E1; font-size:1.1rem;'>📅 Plan de Trabajo (Gantt)</h4>", unsafe_allow_html=True)
        df_tareas_proj = df_tareas_all[df_tareas_all["proyecto_id"] == p_id]
        df_tareas_calc = calcular_fechas_tarea_df(df_tareas_proj)

        if not df_tareas_calc.empty:
          fig = px.timeline(
              df_tareas_calc, x_start="fecha_inicio", x_end="fecha_fin", y="nombre_tarea",
              color="porcentaje_avance", text="avance_txt",
              color_continuous_scale=[[0, "#E2E8F0"], [0.5, "#3B82F6"], [1, "#05297A"]],
              range_color=[0, 100], hover_data={"responsable": True, "porcentaje_avance": False, "avance_txt": False}
          )
          fig.update_yaxes(autorange="reversed")
          fig.update_traces(textposition='inside', insidetextanchor='middle', marker_line_color='rgba(0,0,0,0.1)', marker_line_width=1, opacity=0.95, textfont=dict(color='white', size=11, weight='bold'))
          fig.update_layout(height=160 + (len(df_tareas_calc) * 35), margin=dict(l=0, r=0, t=10, b=0), font=dict(family="Inter"), xaxis=dict(showgrid=True, gridcolor="#F1F5F9"), yaxis=dict(showgrid=False, title=""), coloraxis_colorbar=dict(title="% Avance"))
          st.plotly_chart(fig, use_container_width=True)

          st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#05297A;'>✏️ Actualizar Avance por Tarea</p>", unsafe_allow_html=True)
          with st.form(f"upd_t_{p_id}", clear_on_submit=True):
            col_sel, col_val, col_btn = st.columns([2, 1, 1])
            opciones_tareas = df_tareas_calc.apply(lambda x: f"{x['id']} - {x['nombre_tarea']}", axis=1).tolist()
            t_sel = col_sel.selectbox("Selecciona la tarea", opciones_tareas)
            t_val = col_val.number_input("Nuevo Avance (%)", min_value=0, max_value=100, step=10)
            st.write("")
            if col_btn.form_submit_button("Guardar % Avance", type="secondary"):
              if t_sel:
                t_id_real = int(t_sel.split(" - ")[0])
                engine = obtener_engine()
                with engine.begin() as conn: conn.execute(sqlalchemy.text("UPDATE tareas SET porcentaje_avance=:a WHERE id=:id"), {"a": t_val, "id": t_id_real})
                limpiar_cache_y_recargar(); st.rerun()
        else: st.info("No has agregado tareas al plan de trabajo todavía.")

        with st.expander("➕ Agregar Nueva Tarea"):
          with st.form(f"ft_{p_id}", clear_on_submit=True):
            t_nom = st.text_input("Nombre de la Tarea *")
            c_t1, c_t2, c_t3, c_t4 = st.columns(4)
            t_res = c_t1.selectbox("Responsable", lista_lideres_registrados)
            t_ini = c_t2.date_input("Fecha de Inicio")
            t_dur = c_t3.number_input("Duración (Días)", 1, value=5)
            t_pre = c_t4.text_input("Predecesoras (Ej. 1, 2)")
            if st.form_submit_button("Añadir a Gantt"):
              if t_nom.strip():
                engine = obtener_engine()
                with engine.begin() as conn: conn.execute(sqlalchemy.text("""INSERT INTO tareas (proyecto_id, nombre_tarea, responsable, fecha_inicio, duracion_dias, fecha_fin, porcentaje_avance, predecesoras) VALUES (:pid, :n, :r, :fi, :d, :ff, 0.0, :p)"""), {"pid": p_id, "n": t_nom, "r": t_res, "fi": str(t_ini), "d": t_dur, "ff": str(pd.to_datetime(t_ini) + timedelta(days=t_dur - 1)), "p": t_pre})
                limpiar_cache_y_recargar(); st.rerun()

# PESTAÑA 3: VISTA KANBAN
with tabs[2]:
  st.write("")
  if df.empty: st.info("Agrega proyectos para verlos en el tablero.")
  else:
    k_cols = st.columns(len(OPCIONES_ESTATUS))
    for i, status in enumerate(OPCIONES_ESTATUS):
      with k_cols[i]:
        st.markdown(f"<div style='background-color:#FFFFFF; padding:8px; border-radius:8px; border:1px solid #E2E8F0; border-top:3px solid #05297A; text-align:center; font-weight:700; color:#0F172A; font-size:0.85rem; margin-bottom:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>{status.upper()}</div>", unsafe_allow_html=True)
        df_k = df[df["estatus_tiempo"] == status]
        for _, k_row in df_k.iterrows():
          st.markdown(f"<div class='kanban-card'><div class='kanban-title'>{k_row['nombre']}</div><div class='kanban-meta'>👤 {k_row['lider_asignado']}</div><div class='kanban-meta'>📈 {int((k_row['avance_real'] or 0)*100)}% Completado</div><div class='kanban-meta' style='margin-top:6px;'><i>Folio: {k_row['folio'] or 'S/F'}</i></div></div>", unsafe_allow_html=True)

# PESTAÑA 4: NUEVO PROYECTO
with tabs[3]:
  st.write("")
  if es_moderador:
    sub_tab1, sub_tab2 = st.tabs(["📝 Alta Individual", "📥 Carga Masiva desde Excel"])
    
    with sub_tab1:
      with st.form("f_nuevo", clear_on_submit=True):
        st.markdown("<h3 style='font-size:1.2rem; color:#0F172A; margin-bottom:15px;'>Dar de Alta Nuevo Proyecto</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3); folio = c1.text_input("Folio Interno"); nombre = c2.text_input("Nombre de la Iniciativa *"); lider = c3.selectbox("Responsable del Proyecto *", lista_lideres_registrados)
        c4, c5, c6 = st.columns(3); area = c4.selectbox("Área Solicitante", OPCIONES_AREAS); tipo = c5.selectbox("Categoría Principal", OPCIONES_TIPOS); subtipo = c6.selectbox("Sub-categoría", OPCIONES_SUBTIPOS)
        c7, c8, c9 = st.columns(3); gerente = c7.selectbox("Gerente Sponsor", OPCIONES_GERENTES); etapa = c8.selectbox("Fase de Arranque", OPCIONES_ETAPAS); estatus_inicial = c9.selectbox("Estado Inicial", OPCIONES_ESTATUS, index=0)
        
        st.markdown("<h5 style='font-size:0.95rem; color:#0F172A; margin-top:10px;'>Estimación Financiera</h5>", unsafe_allow_html=True)
        cf1, cf2 = st.columns(2)
        presupuesto_in = cf1.number_input("Presupuesto Asignado ($)", min_value=0.0, value=0.0, step=1000.0)
        roi_in = cf2.number_input("Impacto / ROI Estimado ($)", min_value=0.0, value=0.0, step=1000.0)

        if st.form_submit_button("Crear Proyecto", type="primary"):
          if nombre.strip():
            engine = obtener_engine()
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with engine.begin() as conn: conn.execute(sqlalchemy.text("""INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real, ultima_actualizacion, presupuesto, roi_estimado) VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, 0, :u, :pr, :ro)"""), 
                                                     {"f": folio, "n": nombre, "a": area, "t": tipo, "s": subtipo, "g": gerente, "l": lider, "e": etapa, "st": estatus_inicial, "u": ahora, "pr": presupuesto_in, "ro": roi_in})
            limpiar_cache_y_recargar(); st.success("¡Proyecto creado y agregado exitosamente!"); st.rerun()
          else: st.error("Por favor ingresa el nombre de la iniciativa.")

    with sub_tab2:
      st.markdown("<h3 style='font-size:1.2rem; color:#0F172A;'>📥 Cargar Portafolio desde Excel o CSV</h3>", unsafe_allow_html=True)
      st.write("Sube un archivo de Excel con múltiples iniciativas para importarlas masivamente a la base de datos.")
      
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
          "roi_estimado": 120000.0
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
                  
              st.markdown("##### 🔍 Previsualización de los Datos a Importar:")
              st.dataframe(df_excel, use_container_width=True)
              
              if st.button("🚀 Importar Todos los Proyectos a la Base de Datos", type="primary"):
                  engine = obtener_engine()
                  ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  registros_guardados = 0
                  with engine.begin() as conn:
                      for _, row in df_excel.iterrows():
                          conn.execute(
                              sqlalchemy.text("""INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real, ultima_actualizacion, presupuesto, roi_estimado) 
                                                 VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, :av, :u, :pr, :ro)"""),
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
                                  "ro": float(row.get("roi_estimado", 0.0))
                              }
                          )
                          registros_guardados += 1
                  limpiar_cache_y_recargar()
                  st.success(f"¡Se importaron con éxito {registros_guardados} proyectos al portafolio!")
                  st.rerun()
          except Exception as e:
              st.error(f"Error al leer el archivo. Asegúrate de usar la plantilla oficial. Detalle: {e}")

# PESTAÑA 5: BITÁCORA GLOBAL DE ACTIVIDAD
with tabs[4]:
  st.write("")
  st.markdown("<h3 style='color:#0F172A;'>📜 Feed Global de Actividad y Auditoría</h3>", unsafe_allow_html=True)
  st.write("Historial centralizado en tiempo real de todas las actualizaciones ejecutadas en la plataforma.")
  
  if df_bitacora.empty:
      st.info("Aún no hay movimientos registrados en la bitácora global.")
  else:
      df_bitacora_ext = df_bitacora.merge(df[["id", "nombre", "folio"]], left_on="proyecto_id", right_on="id", how="left")
      for _, b_row in df_bitacora_ext.head(30).iterrows():
          p_nombre = b_row.get("nombre", "Proyecto General")
          p_folio = b_row.get("folio", "S/F")
          st.markdown(f"<div class='timeline-item'><div class='timeline-date'>{b_row['fecha_hora']} | Autor: <b>{b_row['usuario_nombre']}</b> | Proyecto: <b>[{p_folio}] {p_nombre}</b></div><div class='timeline-text'>{b_row['comentario']}</div></div>", unsafe_allow_html=True)

# PESTAÑA 6: USUARIOS (Solo Moderador)
if es_moderador:
  with tabs[5]:
    st.write("")
    df_users = df_users_raw.copy()
    df_users.columns = ["Colaborador", "Correo Corporativo", "Contraseña", "Nivel de Acceso"]

    col_table, col_forms = st.columns([1.5, 1])
    with col_table:
      st.markdown("<h4>Directorio de Usuarios</h4>", unsafe_allow_html=True)
      st.dataframe(df_users, use_container_width=True, hide_index=True)

    with col_forms:
      with st.form("f_alta"):
        st.markdown("<h4>Crear Nuevo Usuario</h4>", unsafe_allow_html=True)
        n_nom = st.text_input("Nombre Completo")
        n_cor = st.text_input("Correo Institucional (@coppel.com)")
        n_pas = st.text_input("Contraseña Inicial")
        n_rol = st.selectbox("Perfil de Seguridad", ["Usuario", "Moderador"])
        if st.form_submit_button("Registrar Usuario", type="primary"):
          if n_cor and n_pas and n_nom:
            try:
              engine = obtener_engine()
              with engine.begin() as conn: conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES (:c, :p, :r, :n)"), {"c": n_cor.strip().lower(), "p": n_pas, "r": n_rol, "n": n_nom})
              limpiar_cache_y_recargar(); st.success("Usuario agregado."); st.rerun()
            except: st.error("El correo ya se encuentra registrado.")

      with st.form("f_baja"):
        lista_correos = df_users["Correo Corporativo"].tolist()
        if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
        correo_borrar = st.selectbox("Revocar Acceso a:", ["Seleccionar..."] + lista_correos)
        if st.form_submit_button("Eliminar Usuario", type="secondary"):
          if correo_borrar != "Seleccionar...":
            engine = obtener_engine()
            with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM usuarios WHERE correo=:c"), {"c": correo_borrar})
            limpiar_cache_y_recargar(); st.success("Acceso revocado."); st.rerun()


# ==============================================================================
# --- MOTOR NLP PROJECT IA (AVANZADO & FLUIDO) ---
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
      ret = len(dataframe[dataframe["estatus_tiempo"].isin(["Retrasado", "Detenido"])]) if not dataframe.empty else 0
      resp = f"¡Hola, **{usuario_nombre}**! 👋 Qué gusto saludarte.\n\nActualmente administro **{tot} proyectos activos**. "
      if ret > 0: resp += f"⚠️ Noté que hay **{ret} proyectos retrasados**. ¿Te gustaría que te muestre cuáles son?"
      else: resp += "Por fortuna, no tenemos ningún proyecto retrasado. ¿Qué te gustaría consultar hoy?"
      return resp

  p_analizar = p_lower
  for s in ["hola ", "buenos dias ", "buenas tardes ", "por favor ", "dime ", "quiero saber ", "quisiera saber ", "me puedes decir "]:
      if p_analizar.startswith(s): p_analizar = p_analizar[len(s):].strip()

  if dataframe.empty:
      return "Actualmente no tenemos proyectos registrados en el portafolio."

  busca_riesgo_predictivo = any(k in p_analizar for k in ["riesgo", "estancado", "cuello de botella", "prediccion", "parado", "peligro"])
  if busca_riesgo_predictivo:
      estancados = dataframe[dataframe.get('es_estancado', False) == True]
      retrasados = dataframe[dataframe['estatus_tiempo'].isin(["Retrasado", "Detenido"])]
      
      res = "🔮 **Diagnóstico Predictivo de Riesgos en el Portafolio:**\n\n"
      if estancados.empty and retrasados.empty:
          res += "🟢 **Estado Saludable:** No se detectan cuellos de botella ni proyectos estancados sin movimiento por más de 20 días."
      else:
          if not retrasados.empty:
              res += f"🚨 **{len(retrasados)} Proyecto(s) en Retraso Crítico:**\n"
              for _, r in retrasados.iterrows(): res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}** (`{r['estatus_tiempo']}`)\n"
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
      for _, r in top_p.iterrows():
          res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**: `${r['presupuesto']:,.2f}` (ROI: `${r['roi_estimado']:,.2f}`)\n"
      return res

  busca_estatus_general = any(k in p_analizar for k in ["estatus", "estado", "etapa", "fase", "como van"])
  busca_retrasos = any(k in p_analizar for k in ["retras", "riesgo", "deteni", "critico", "problema", "urgente", "foco rojo"])
  
  if busca_estatus_general and not busca_retrasos and not any(a.lower() in p_analizar for a in OPCIONES_AREAS):
      res = f"📌 **Estatus actual de los proyectos en el portafolio ({len(dataframe)}):**\n\n"
      for _, r in dataframe.iterrows():
          pct = int((r['avance_real'] or 0) * 100)
          badge = "🟢" if r['estatus_tiempo'] == "En tiempo" else ("⚠️" if r['estatus_tiempo'] in ["Retrasado", "Detenido"] else "⚪")
          res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**\n"
          res += f"  * {badge} **Estatus:** `{r['estatus_tiempo']}` | 📍 **Fase:** {r['etapa_actual']}\n"
          res += f"  * 👤 **Líder:** {r['lider_asignado']} | 📈 **Avance:** {pct}%\n\n"
      return res

  busca_top_lider = any(k in p_analizar for k in ["quien", "quién", "lider", "líder", "responsable", "persona", "encargado", "colaborador"]) and any(k in p_analizar for k in ["mas", "más", "mayor", "top", "tiene", "carga"])
  if busca_top_lider and not busca_retrasos:
      counts = dataframe["lider_asignado"].value_counts()
      if not counts.empty:
          top_l = counts.index[0]; top_val = counts.iloc[0]
          res = f"¡Claro! Analizando la base de datos, **{top_l}** es la persona con mayor carga operativa, teniendo **{top_val} iniciativas** bajo su responsabilidad.\n\n📌 **Distribución de proyectos por líder:**\n"
          for l_name, val in counts.items(): res += f"* **{l_name}**: {val} proyecto(s)\n"
          return res

  busca_top_area = any(k in p_analizar for k in ["area", "área", "departamento"]) and any(k in p_analizar for k in ["mas", "más", "mayor", "top", "tiene"])
  if busca_top_area:
      counts = dataframe["area_negocio"].value_counts()
      if not counts.empty:
          top_a = counts.index[0]; top_val = counts.iloc[0]
          res = f"¡Listo! El área que actualmente concentra más proyectos es **{top_a}**, con **{top_val} iniciativas**.\n\n📌 **Desglose por área:**\n"
          for a_name, val in counts.items(): res += f"* **{a_name}**: {val} proyectos\n"
          return res

  area_obj = next((a for a in OPCIONES_AREAS if a.lower() in p_analizar), None)
  lideres_y_gerentes = set(obtener_lista_usuarios(df_users_raw) + OPCIONES_GERENTES)
  persona_obj = next((p for p in lideres_y_gerentes if len(p) > 3 and p.lower() in p_analizar), None)

  df_result = dataframe.copy()
  criterios = []
  
  if area_obj:
      df_result = df_result[df_result['area_negocio'] == area_obj]
      criterios.append(f"Área: **{area_obj}**")
  if persona_obj:
      df_result = df_result[(df_result["lider_asignado"] == persona_obj) | (df_result["gerente"] == persona_obj)]
      criterios.append(f"Involucrado: **{persona_obj}**")
  if busca_retrasos:
      df_result = df_result[df_result["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
      criterios.append("Estatus: **Retrasado**")

  if len(criterios) > 0:
      if df_result.empty:
          return f"🔍 Estuve buscando, pero no encontré proyectos que coincidan con tus filtros: " + " | ".join(criterios)
      
      res = f"🔍 **Resultados de la búsqueda** (" + " | ".join(criterios) + f"):\n\nEncontré **{len(df_result)}** proyectos:\n\n"
      for _, r in df_result.iterrows():
          res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**\n  * 👤 **Líder:** {r['lider_asignado']} | 🏢 **Área:** {r['area_negocio']}\n  * 📌 **Estatus:** `{r['estatus_tiempo']}` | 📍 **Fase:** {r['etapa_actual']} | 📈 **Avance:** {int((r['avance_real'] or 0)*100)}%\n\n"
      return res

  coincidencias = dataframe[dataframe["nombre"].str.lower().str.contains(p_analizar, na=False) | dataframe["folio"].str.lower().str.contains(p_analizar, na=False)]
  if not coincidencias.empty:
      res = f"🔍 Encontré **{len(coincidencias)} proyectos** asociados a tu consulta:\n\n"
      for _, r in coincidencias.iterrows():
          res += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}**\n  * 👤 **Líder:** {r['lider_asignado']} | 📌 **Estatus:** `{r['estatus_tiempo']}` | 📈 **Avance:** {int((r['avance_real'] or 0)*100)}%\n\n"
      return res

  res_general = f"📋 **Aquí está el desglose actual de tus proyectos ({len(dataframe)}):**\n\n"
  for _, r in dataframe.iterrows():
      pct = int((r['avance_real'] or 0) * 100)
      res_general += f"* **[{r['folio'] or 'S/F'}] {r['nombre']}** — `{r['estatus_tiempo']}` ({pct}% avance)\n"
  return res_general


# --- BOTÓN FLOTANTE "PROJECT IA" ---
with st.popover("🤖 Project IA", help="Haz clic para charlar con tu asistente inteligente"):
  col1, col2 = st.columns([3, 1])
  with col1:
      st.markdown("<h3 style='color:#05297A; margin-bottom: 0px; font-weight:800; letter-spacing:-1px;'>🤖 Project IA</h3>", unsafe_allow_html=True)
  with col2:
      if st.button("🧹 Borrar", help="Limpia la conversación"):
          st.session_state.chat_history_fast = []
          st.rerun()
          
  st.caption("Asistente Analítico Heading 360.")
  st.divider()

  mensaje_bienvenida = {"role": "assistant", "content": f"¡Hola **{st.session_state.nombre_actual}**! 👋 Soy **Project IA**, tu asistente en Heading 360. ¿Qué te gustaría consultar del portafolio hoy?"}

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
      with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])
