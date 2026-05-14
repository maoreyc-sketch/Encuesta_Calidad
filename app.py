import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================================================
# 1. CONFIGURACIÓN VISUAL Y "PUNTO MEDIO" DE PANTALLA
# =====================================================================
st.set_page_config(page_title="Encuesta Calidad MEN", layout="wide")

# CSS para limitar el ancho y mejorar la estética
st.markdown("""
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# ENCABEZADO INSTITUCIONAL CON LOGO
# =====================================================================
col_logo, col_tit = st.columns([1, 4]) # Crea dos columnas (una pequeña para el logo y otra para el texto)

with col_logo:
    # Reemplaza "tu_imagen.png" por el nombre real de tu archivo de imagen
    st.image("logo_min.png", width=200) 

with col_tit:
    st.markdown("""
        <div style='text-align: left;'>
            <h1 style='font-family: Arial; font-size: 20pt; font-weight: bold; margin-bottom: 0;'>
                Ministerio de Educación Nacional
            <h2 style='font-family: Arial; font-size: 16pt; font-weight: bold; color: #C935B7;'>
                Encuesta de Calidad en la Información
            </h2>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Función para forzar el scroll al inicio de la página
def scroll_al_inicio():
    js = "<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>"
    st.components.v1.html(js, height=0)

# =====================================================================
# 2. LÓGICA DE DATOS Y ESTADO
# =====================================================================
@st.cache_data
def cargar_maestra():
    try:
        df = pd.read_excel("EE 2026.xlsx", sheet_name=0, dtype=str)
        if 'EMAIL' in df.columns:
            df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
        return df
    except:
        return pd.DataFrame()

def es_duplicado(email):
    if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
        try:
            df_hist = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
            return email in df_hist['EMAIL_VALIDADO'].values
        except: return False
    return False

# Inicialización de estados para no perder información
hojas = ["Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "Docentes"]

if 'iniciado' not in st.session_state: st.session_state.iniciado = False
if 'encuesta_iniciada' not in st.session_state: st.session_state.encuesta_iniciada = False
if 'paso' not in st.session_state: st.session_state.paso = 0
if 'editando' not in st.session_state: st.session_state.editando = False
if 'finalizado' not in st.session_state: st.session_state.finalizado = False
if 'resp_enc' not in st.session_state: st.session_state.resp_enc = {}

# =====================================================================
# 3. FLUJO PRINCIPAL
# =====================================================================

# Pantalla de éxito final
if st.session_state.finalizado:
    st.success("✅ ¡Encuesta procesada exitosamente! Los datos han sido registrados en la base del Ministerio.")
    st.balloons()
    if st.button("Finalizar Sesión"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# Acceso inicial
if not st.session_state.iniciado:
    st.info("👋 Bienvenida/o. Ingrese los datos para validar su institución.")
    c1, c2 = st.columns(2)
    with c1: email_t = st.text_input("Correo electrónico institucional:")
    with c2: nombre_t = st.text_input("Nombre de quien diligencia:")
    
    if st.button("🚀 Iniciar Proceso", use_container_width=True):
        if email_t and nombre_t:
            email_clean = email_t.strip().lower()
            if es_duplicado(email_clean):
                st.error("❌ Esta institución ya cuenta con un registro en el sistema.")
            else:
                st.session_state.email_ingresado = email_clean
                st.session_state.nombre_diligencia = nombre_t.strip()
                st.session_state.iniciado = True
                st.rerun()
        else: st.warning("Por favor complete ambos campos.")

else:
    df_ee = cargar_maestra()
    res = df_ee[df_ee['EMAIL'] == st.session_state.email_ingresado]
    
    if not res.empty:
        fila = res.iloc[0]
        
        # --- FASE 1: ACTUALIZACIÓN ---
        if not st.session_state.encuesta_iniciada:
            st.subheader("Fase 1: Verificación de Datos del Establecimiento")
            bloq = not st.session_state.editando
            col_a, col_b = st.columns(2)
            with col_a:
                nom = st.text_input("Nombre", value=fila.get('NOMBRE_ESTABLECIMIENTO',''), disabled=bloq)
                dan = st.text_input("Código DANE", value=fila.get('CODIGO_DANE',''), disabled=bloq)
                dep = st.text_input("Departamento", value=fila.get('DEPARTAMENTO',''), disabled=bloq)
                mun = st.text_input("Municipio", value=fila.get('SECRETARIA',''), disabled=bloq)
                dan_n = st.text_input("Código DANE Nuevo (Si aplica)", value="", disabled=bloq)
            with col_b:
                rec = st.text_input("Rector", value=fila.get('RECTOR',''), disabled=bloq)
                dir_e = st.text_input("Dirección", value=fila.get('DIRECCION',''), disabled=bloq)
                bar = st.text_input("Barrio / Vereda", value=fila.get('BARRIO_VEREDA',''), disabled=bloq)
                tel = st.text_input("Teléfono", value=fila.get('TELEFONO',''), disabled=bloq)
                obs = st.text_area("Observaciones", value="", disabled=bloq, height=68)

            ca, cb = st.columns(2)
            with ca:
                if not st.session_state.editando:
                    if st.button("✏️ Actualizar"):
                        st.session_state.editando = True
                        st.rerun()
                else:
                    if st.button("💾 Guardar Cambios"):
                        st.session_state.datos_temp = {'NOMBRE':nom,'DANE':dan,'DEPTO':dep,'MUNI':mun,'RECTOR':rec,'DIR':dir_e,'BARRIO':bar,'TEL':tel,'DANE_N':dan_n,'OBS':obs}
                        st.session_state.editando = False
                        st.session_state.encuesta_iniciada = True
                        st.rerun()
            with cb:
                if not st.session_state.editando:
                    if st.button("Continuar con Encuesta ➡️"):
                        st.session_state.datos_temp = {'NOMBRE':nom,'DANE':dan,'DEPTO':dep,'MUNI':mun,'RECTOR':rec,'DIR':dir_e,'BARRIO':bar,'TEL':tel,'DANE_N':dan_n,'OBS':obs}
                        st.session_state.encuesta_iniciada = True
                        st.rerun()

        # --- FASE 2: ENCUESTA ---
        else:
            scroll_al_inicio() # Se ejecuta al cargar el bloque
            st.markdown("### Fase 2: Diligenciamiento de Encuesta")
            
            # Navegación Visual Sincronizada
            paso_actual = st.radio("Módulos:", hojas, index=st.session_state.paso, horizontal=True)
            if hojas.index(paso_actual) != st.session_state.paso:
                st.session_state.paso = hojas.index(paso_actual)
                st.rerun()

            hoja_act = hojas[st.session_state.paso]
            st.info(f"📍 Usted está en el bloque: **{hoja_act}**")
            
            try:
                df_p = pd.read_excel("Encuesta_Calidad.xlsx", sheet_name=hoja_act, skiprows=2)
                for idx, r in df_p.iterrows():
                    p = str(r.get('Pregunta / campo', r.get('Pregunta','')))
                    t = str(r.get('Tipo de respuesta', r.get('Tipo',''))).lower()
                    o = str(r.get('Opciones o criterio', r.get('Opciones','')))
                    v = str(r.get('Variable', f"{hoja_act}_{idx}")).strip()
                    ob = str(r.get('Obligatorio','')).strip().lower() == 'sí'
                    
                    if p and p != 'nan':
                        st.write(f"**{p}** {'(*)' if ob else ''}")
                        if 'lista' in t or 'selección' in t:
                            opts = ["Seleccionar..."] + [x.strip() for x in o.split(';')] if ';' in o else ["Seleccionar...", o]
                            curr = st.session_state.resp_enc.get(v, "Seleccionar...")
                            st.session_state.resp_enc[v] = st.selectbox("Elegir:", opts, index=opts.index(curr) if curr in opts else 0, key=f"s_{v}", label_visibility="collapsed")
                        elif 'numérico' in t:
                            curr = st.session_state.resp_enc.get(v, 0)
                            st.session_state.resp_enc[v] = st.number_input("Valor:", min_value=0, step=1, value=int(curr), key=f"n_{v}", label_visibility="collapsed")
                        else:
                            curr = st.session_state.resp_enc.get(v, "")
                            st.session_state.resp_enc[v] = st.text_input("Escriba:", value=curr, key=f"t_{v}", label_visibility="collapsed")
                        st.write("")
            except Exception as e:
                st.error(f"Error al cargar las preguntas: {e}")

            st.markdown("---")
            c_iz, c_de = st.columns(2)
            with c_iz:
                if st.session_state.paso > 0:
                    if st.button("⬅️ Bloque Anterior"):
                        st.session_state.paso -= 1
                        st.rerun()
            with c_de:
                if st.session_state.paso < len(hojas) - 1:
                    if st.button("Siguiente Bloque ➡️"):
                        st.session_state.paso += 1
                        st.rerun()
                else:
                    if st.button("💾 FINALIZAR Y ENVIAR ENCUESTA"):
                        # Validación de obligatorios simplificada
                        fecha_f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        final = {'FECHA': fecha_f, 'DILIGENCIADOR': st.session_state.nombre_diligencia, 'EMAIL_VALIDADO': st.session_state.email_ingresado, **st.session_state.datos_temp, **st.session_state.resp_enc}
                        pd.DataFrame([final]).to_csv('Consolidado_Encuestas_MEN.csv', mode='a', header=not pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'), index=False, encoding='utf-8-sig')
                        st.session_state.finalizado = True
                        st.rerun()
    else:
        st.error("Correo no registrado. Por favor verifique.")
        if st.button("Reintentar"): st.session_state.clear(); st.rerun()

# =====================================================================
# 4. PANEL DE CONTROL (SIEMPRE ACCESIBLE AL FINAL)
# =====================================================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
with st.expander("🔐 Panel de Administración (Uso Interno)"):
    pw = st.text_input("Clave Maestra:", type="password")
    if pw == "AdminMEN2026":
        if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
            df_v = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
            st.dataframe(df_v)
            st.download_button("📥 Descargar Excel de Respuestas", data=df_v.to_csv(index=False).encode('utf-8-sig'), file_name='Consolidado_MEN.csv', mime='text/csv')
        else: st.info("No hay registros todavía.")
    elif pw != "": st.error("Acceso denegado.")