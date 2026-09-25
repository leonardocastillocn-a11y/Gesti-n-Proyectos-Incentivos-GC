import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="Portafolio de Incentivos", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# --- CSS PREMIUM LIMPIO (Sin recuadros fantasma) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #F8FAFC; } /* Fondo ligeramente gris para contraste limpio */
    
    /* 1. Tarjetas de métricas (Simplificadas para evitar errores de renderizado) */
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] > label { font-size: 0.85rem !important; color: #64748B !important; font-weight: 600 !important; }
    div[data-testid="metric-container"] > div > div { font-size: 2rem !important; color: #0F172A !important; font-weight: 700 !important; }
    
    /* 2. Badges */
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-flex; }
    .bg-green { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0;}
    .bg-red { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA;}
    .bg-yellow { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A;}
    .bg-gray { background-color: #F1F5F9; color: #475569; border: 1px solid #E2E8F0;}
    .bg-blue { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE;}
    
    /* 3. Inputs, Botones y Formularios */
    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stTextArea > div > div > textarea { 
        border-radius: 8px !important; border: 1px solid #CBD5E1 !important; background-color: white !important;
    }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s !important; }
    .stButton > button[kind="primary"] { background-color: #2563EB !important; border: none !important; color: white !important;}
    .stButton > button[kind="primary"]:hover { background-color: #1D4ED8 !important; }
    
    /* 4. Tabs limpias */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #E2E8F0;}
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #2563EB !important; font-weight: 700 !important; color: #1E293B !important;}
    
    /* 5. Títulos */
    h1, h2, h3, h4 { color: #0F172A; font-weight: 700 !important; }
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
    conn = obtener_conexion(); cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS proyectos (id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT, tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT, etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT)""")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)")
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')")
        cursor.execute("INSERT INTO usuarios VALUES ('ivan.salazar@coppel.com', 'Coppel2026', 'Usuario', 'Oscar Ivan Salazar')")
    conn.commit(); conn.close()
inicializar_db()

# --- LOGIN LIMPIO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False; st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
    col_izq, col_centro, col_der = st.columns([1, 1.2, 1])
    with col_centro:
        st.write(""); st.write(""); st.write("")
        st.markdown("<h1 style='text-align: center;'>💼 Incentivos Hub</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 30px;'>Centro de Excelencia • Coppel</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Iniciar Sesión")
            correo_input = st.text_input("Correo Corporativo", placeholder="tu.nombre@coppel.com")
            password_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
            st.write("")
            submit = st.form_submit_button("Ingresar al Portal", type="primary", use_container_width=True)
            
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

# --- SIDEBAR LIMPIO ---
es_moderador = st.session_state.rol == "Moderador"
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.markdown(f"<h3 style='margin-bottom:0;'>{st.session_state.nombre_actual}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B; font-size:0.85rem; margin-top:0;'>{st.session_state.correo_actual}</p>", unsafe_allow_html=True)
    badge_color = "bg-blue" if es_moderador else "bg-gray"
    st.markdown(f"<span class='badge {badge_color}'>{st.session_state.rol}</span>", unsafe_allow_html=True)
    
    st.divider()
    with st.expander("🔑 Seguridad de la Cuenta", expanded=False):
        with st.form("form_cambio_pass"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar_pass = st.text_input("Confirmar", type="password")
            if st.form_submit_button("Actualizar", use_container_width=True):
                if nueva_pass == confirmar_pass and nueva_pass:
                    conn = obtener_conexion(); cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET password=? WHERE correo=?", (nueva_pass, st.session_state.correo_actual))
                    conn.commit(); conn.close(); st.success("Guardado.")
                else: st.error("Las contraseñas no coinciden.")
    
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False; st.rerun()

# --- DATOS GLOBALES ---
conn = obtener_conexion()
df = pd.read_sql_query("SELECT * FROM proyectos", conn)

# --- HEADER Y MÉTRICAS (USANDO st.metric NATIVO) ---
st.markdown("<h2 style='margin-bottom: 20px;'>Visión General del Portafolio</h2>", unsafe_allow_html=True)

if not df.empty:
    # Usamos st.metric que es 100% nativo y nunca falla ni deja recuadros blancos
    m1, m2, m3, m4 = st.columns(4)
    total = len(df); en_tiempo = len(df[df['estatus_tiempo'] == 'En tiempo'])
    retrasados = len(df[df['estatus_tiempo'] == 'Retrasado']); prom_avance = df['avance_real'].mean() * 100
    
    m1.metric(label="📂 Iniciativas Activas", value=total)
    m2.metric(label="✅ Ejecución en Tiempo", value=en_tiempo)
    m3.metric(label="⚠️ En Riesgo / Retraso", value=retrasados)
    m4.metric(label="🚀 Avance Global", value=f"{prom_avance:.1f}%")
    st.write("")

# --- GENERADOR PDF (Moderador) ---
if es_moderador and not df.empty:
    def generar_pdf(dataframe):
        pdf = FPDF(orientation="L", unit="mm", format="A4"); pdf.add_page()
        pdf.set_font("Arial", 'B', 20); pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 10, "Reporte Ejecutivo de Portafolio", ln=True, align="L")
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 8, f"Generado el: {datetime.now().strftime('%d/%m/%Y')} | Clasificación: Uso Interno", ln=True, align="L"); pdf.ln(8)
        
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(241, 245, 249); pdf.set_text_color(15, 23, 42)
        pdf.cell(20, 10, "Folio", 0, 0, 'L', True); pdf.cell(70, 10, "Proyecto", 0, 0, 'L', True)
        pdf.cell(45, 10, "Lider Asignado", 0, 0, 'L', True); pdf.cell(25, 10, "Estatus", 0, 0, 'C', True)
        pdf.cell(20, 10, "Avance", 0, 0, 'C', True); pdf.cell(50, 10, "Etapa Actual", 0, 0, 'L', True); pdf.cell(45, 10, "Ult. Act.", 0, 1, 'L', True)
        
        pdf.set_font("Arial", '', 8); pdf.set_text_color(51, 65, 85)
        for _, row in dataframe.iterrows():
            pdf.cell(20, 10, str(row['folio'])[:10], 'B'); pdf.cell(70, 10, str(row['nombre'])[:40], 'B')
            pdf.cell(45, 10, str(row['lider_asignado'])[:25], 'B'); pdf.cell(25, 10, str(row['estatus_tiempo']), 'B', 0, 'C')
            pdf.cell(20, 10, f"{int((row['avance_real'] or 0)*100)}%", 'B', 0, 'C'); pdf.cell(50, 10, str(row['etapa_actual'])[:30], 'B', 0, 'L'); pdf.cell(45, 10, str(row['ultima_actualizacion'])[:16], 'B', 1, 'L')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp: pdf.output(tmp.name); return tmp.name

    with st.sidebar:
        st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#64748B;'>📥 EXPORTAR DATOS</p>", unsafe_allow_html=True)
        pdf_path = generar_pdf(df)
        with open(pdf_path, "rb") as file: st.download_button("Descargar Informe (PDF)", data=file, file_name="Portafolio_Incentivos.pdf", use_container_width=True)

# --- PESTAÑAS DINÁMICAS ---
if es_moderador: tabs = st.tabs(["📋 Tablero de Control", "➕ Registrar Iniciativa", "👥 Administración de Accesos"])
else: tabs = st.tabs(["📋 Tablero de Control", "➕ Registrar Iniciativa"])

# PESTAÑA 1: LISTADO Y EDICIÓN
with tabs[0]:
    if df.empty:
        st.info("El portafolio está vacío. Comienza registrando una iniciativa en la siguiente pestaña.")
    else:
        st.write("")
        for _, row in df.iterrows():
            p_id = row["id"]
            if row["estatus_tiempo"] == "En tiempo": css_class = "bg-green"; icon="✅"
            elif row["estatus_tiempo"] == "Retrasado": css_class = "bg-red"; icon="⚠️"
            elif row["estatus_tiempo"] == "Detenido": css_class = "bg-yellow"; icon="⏸️"
            else: css_class = "bg-gray"; icon="⏱️"
            
            with st.expander(f"{row['folio'] or 'S/F'} | {row['nombre']} — Avance: {int((row['avance_real'] or 0)*100)}%"):
                st.progress(float(row['avance_real'] or 0.0))
                
                with st.form(f"update_{p_id}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"<p style='margin:0; font-size:0.9rem;'><span style='color:#64748B;'>Responsable:</span> <b>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
                    c2.markdown(f"<p style='margin:0; font-size:0.9rem; text-align:right;'><span style='color:#64748B;'>Actualizado:</span> <b>{row['ultima_actualizacion'] or 'N/A'}</b></p>", unsafe_allow_html=True)
                    st.divider()
                    
                    c_form1, c_form2, c_form3 = st.columns(3)
                    u_etapa = c_form1.selectbox("Fase Actual", OPCIONES_ETAPAS, index=OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0)
                    u_estatus = c_form2.selectbox("Estado de Ejecución", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0)
                    u_avance = c_form3.slider("Progreso Validado (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
                    
                    u_resumen = st.text_area("Bitácora de Estatus y Bloqueos", row["resumen_estatus"] or "", height=80)
                    
                    l1, l2 = st.columns(2)
                    u_carpeta = l1.text_input("🔗 Repositorio Drive", row["carpeta_url"] or "", placeholder="https://drive.google.com/...")
                    u_plan = l2.text_input("🔗 Plan de Trabajo", row["plan_url"] or "", placeholder="https://docs.google.com/spreadsheets/...")
                    
                    st.write("")
                    btn1, btn2, btn3 = st.columns([2, 2, 6])
                    if btn1.form_submit_button("Actualizar Registro", type="primary"):
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
            st.markdown("<h3 style='margin-top:0;'>Alta de Iniciativa</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#2563EB; font-weight:600; font-size:0.85rem; text-transform:uppercase;'>1. Identificación Principal</p>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            folio = c1.text_input("Folio Interno")
            nombre = c2.text_input("Nombre de la Iniciativa *")
            lider = c3.text_input("Líder Asignado")
            
            st.write("")
            st.markdown("<p style='color:#2563EB; font-weight:600; font-size:0.85rem; text-transform:uppercase;'>2. Taxonomía Organizacional</p>", unsafe_allow_html=True)
            c4, c5, c6 = st.columns(3)
            area = c4.selectbox("Área Solicitante", OPCIONES_AREAS)
            tipo = c5.selectbox("Categoría General", OPCIONES_TIPOS)
            subtipo = c6.selectbox("Subcategoría Específica", OPCIONES_SUBTIPOS)
            
            st.write("")
            st.markdown("<p style='color:#2563EB; font-weight:600; font-size:0.85rem; text-transform:uppercase;'>3. Parámetros de Gestión</p>", unsafe_allow_html=True)
            c7, c8, c9 = st.columns(3)
            gerente = c7.selectbox("Patrocinador (Sponsor)", OPCIONES_GERENTES)
            etapa = c8.selectbox("Fase de Arranque", OPCIONES_ETAPAS)
            estatus_inicial = c9.selectbox("Estado Inicial", OPCIONES_ESTATUS, index=4)
            
            st.divider()
            if st.form_submit_button("Registrar en el Portafolio Oficial", type="primary"):
                if nombre.strip():
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)", (folio, nombre, area, tipo, subtipo, gerente, lider, etapa, estatus_inicial))
                    conn.commit(); st.success("✅ Iniciativa creada exitosamente."); st.rerun()
                else: st.error("El Nombre de la Iniciativa es obligatorio.")
    else:
        st.warning("🔒 Alta de proyectos restringida al perfil de Moderador.")

# PESTAÑA 3: USUARIOS
if es_moderador:
    with tabs[2]:
        st.write("")
        st.markdown("### Centro de Administración de Identidades")
        
        # Mostramos la tabla limpia sin necesidad de divs extraños
        df_users = pd.read_sql_query("SELECT nombre as Colaborador, correo as Correo, rol as Permisos FROM usuarios", conn)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        st.write("")
        
        c_add, c_del = st.columns(2)
        with c_add:
            with st.form("form_alta_usuario", clear_on_submit=True):
                st.markdown("#### ➕ Habilitar Accesos")
                n_nombre = st.text_input("Nombre Completo")
                n_correo = st.text_input("Correo Corporativo")
                n_pass = st.text_input("Clave Temporal", type="password")
                n_rol = st.selectbox("Nivel de Permisos", ["Usuario", "Moderador"])
                st.write("")
                if st.form_submit_button("Dar de Alta", type="primary"):
                    if n_correo and n_pass and n_nombre:
                        try:
                            cursor = conn.cursor(); cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", (n_correo.strip().lower(), n_pass, n_rol, n_nombre))
                            conn.commit(); st.success(f"Cuenta activada."); st.rerun()
                        except: st.error("El correo ya existe.")
                    else: st.warning("Se requieren todos los campos.")
            
        with c_del:
            with st.form("form_baja_usuario"):
                st.markdown("#### 🚫 Revocar Accesos")
                st.caption("Selecciona un colaborador para desactivar su cuenta de forma permanente.")
                lista_correos = df_users['Correo'].tolist()
                if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
                correo_borrar = st.selectbox("Colaborador a eliminar", ["Seleccionar..."] + lista_correos)
                st.write("")
                st.write("")
                st.write("")
                if st.form_submit_button("Eliminar Cuenta"):
                    if correo_borrar != "Seleccionar...":
                        cursor = conn.cursor(); cursor.execute("DELETE FROM usuarios WHERE correo=?", (correo_borrar,)); conn.commit(); st.success(f"Cuenta eliminada."); st.rerun()
                    else: st.warning("Selecciona una cuenta.")

conn.close()
