import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================================================
# 1. CONFIGURACIÓN Y ESTILOS MEN
# =====================================================================
st.set_page_config(page_title="Encuesta Calidad MEN", layout="wide")

st.markdown("""
    <h1 style='font-family: Arial; font-size: 18pt; font-weight: bold; text-align: center;'>
        Ministerio de Educación Nacional
    </h1>
    <h2 style='font-family: Arial; font-size: 14pt; font-weight: bold; text-align: center;'>
        Encuesta de Calidad en la Información
    </h2>
    <hr>
""", unsafe_allow_html=True)

# =====================================================================
# 2. FUNCIONES DE CARGA Y LÓGICA DE NEGOCIO
# =====================================================================
@st.cache_data
def cargar_datos_ee():
    archivo_ee = "EE 2026.xlsx"
    try:
        df = pd.read_excel(archivo_ee, sheet_name=0, dtype=str)
        if 'EMAIL' in df.columns:
            df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error al cargar base maestra: {e}")
        return pd.DataFrame()

def verificar_duplicidad(email):
    if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
        try:
            df_h = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
            if 'EMAIL_VALIDADO' in df_h.columns:
                return email in df_h['EMAIL_VALIDADO'].values
        except:
            pass
    return False

# =====================================================================
# 3. GESTIÓN DE ESTADO DE SESIÓN
# =====================================================================
if 'iniciado' not in st.session_state:
    st.session_state.iniciado = False
if 'encuesta_iniciada' not in st.session_state:
    st.session_state.encuesta_iniciada = False
if 'paso_encuesta' not in st.session_state:
    st.session_state.paso_encuesta = 0
if 'editando' not in st.session_state:
    st.session_state.editando = False
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False

# =====================================================================
# 4. FLUJO DE USUARIO (ENCUESTA)
# =====================================================================

# Pantalla de éxito final (Ajuste 2: Sin botón de repetir, solo reset al inicio)
if st.session_state.finalizado:
    st.success("✅ ¡Encuesta procesada exitosamente! Gracias por su participación.")
    st.balloons()
    if st.button("Volver al Inicio y Salir"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# Inicio de sesión
if not st.session_state.iniciado:
    st.info("👋 Bienvenido. Ingrese los datos para acceder.")
    c1, c2 = st.columns(2)
    with c1:
        email_t = st.text_input("Correo electrónico del establecimiento:")
    with c2:
        nombre_t = st.text_input("Nombre de quien diligencia:")
        
    if st.button("🚀 Iniciar Encuesta", use_container_width=True):
        if not email_t or not nombre_t:
            st.warning("Debe ingresar correo y nombre.")
        elif verificar_duplicidad(email_t.strip().lower()):
            st.error("❌ Este establecimiento ya registró su encuesta.")
        else:
            st.session_state.email_ingresado = email_t.strip().lower()
            st.session_state.nombre_diligencia = nombre_t.strip()
            st.session_state.iniciado = True
            st.rerun()

else:
    df_ee = cargar_datos_ee()
    res = df_ee[df_ee['EMAIL'] == st.session_state.email_ingresado]
    
    if not res.empty:
        fila = res.iloc[0]
        
        # Fase 1: Actualización de datos
        if not st.session_state.encuesta_iniciada:
            st.subheader("Fase 1: Verificación de Datos")
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
                    if st.button("Actualizar"):
                        st.session_state.editando = True
                        st.rerun()
                else:
                    if st.button("Guardar Cambios"):
                        st.session_state.datos_temporales = {'NOMBRE':nom,'DANE':dan,'DEPTO':dep,'MUNI':mun,'RECTOR':rec,'DIR':dir_e,'BARRIO':bar,'TEL':tel,'DANE_N':dan_n,'OBS':obs}
                        st.session_state.editando = False
                        st.session_state.encuesta_iniciada = True
                        st.rerun()
            with cb:
                if not st.session_state.editando:
                    if st.button("Continuar con Encuesta ➡️"):
                        st.session_state.datos_temporales = {'NOMBRE':nom,'DANE':dan,'DEPTO':dep,'MUNI':mun,'RECTOR':rec,'DIR':dir_e,'BARRIO':bar,'TEL':tel,'DANE_N':dan_n,'OBS':obs}
                        st.session_state.encuesta_iniciada = True
                        st.rerun()

        # Fase 2: Bloques dinámicos
        else:
            st.markdown("---")
            hojas = ["Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "Docentes"]
            
            # Ajuste 1: Radio button para navegación (al cambiar, st.rerun() manda al top)
            st.radio("Progreso:", hojas, index=st.session_state.paso_encuesta, horizontal=True, key="nav_radio")
            
            if 'resp_enc' not in st.session_state: st.session_state.resp_enc = {}
            if 'oblig' not in st.session_state: st.session_state.oblig = []

            hoja_act = hojas[st.session_state.paso_encuesta]
            st.subheader(f"Módulo: {hoja_act}")
            
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
                        if ob and v not in st.session_state.oblig: st.session_state.oblig.append(v)
                        
                        if 'lista' in t or 'selección' in t:
                            opts = ["Seleccionar..."] + [x.strip() for x in o.split(';')] if ';' in o else ["Seleccionar...", o]
                            curr = st.session_state.resp_enc.get(v, "Seleccionar...")
                            st.session_state.resp_enc[v] = st.selectbox("Elija:", opts, index=opts.index(curr) if curr in opts else 0, key=f"s_{v}", label_visibility="collapsed")
                        elif 'numérico' in t:
                            curr = st.session_state.resp_enc.get(v, 0)
                            st.session_state.resp_enc[v] = st.number_input("Cant:", min_value=0, step=1, value=int(curr), key=f"n_{v}", label_visibility="collapsed")
                        else:
                            curr = st.session_state.resp_enc.get(v, "")
                            st.session_state.resp_enc[v] = st.text_input("Resp:", value=curr, key=f"t_{v}", label_visibility="collapsed")
                        st.write("")
            except Exception as e:
                st.error(f"Error en bloque: {e}")

            st.markdown("---")
            c_iz, c_de = st.columns(2)
            with c_iz:
                if st.session_state.paso_encuesta > 0:
                    if st.button("⬅️ Anterior"):
                        st.session_state.paso_encuesta -= 1
                        st.rerun() # Ajuste 1: Forzar scroll al top
            with c_de:
                if st.session_state.paso_encuesta < len(hojas) - 1:
                    if st.button("Siguiente ➡️"):
                        st.session_state.paso_encuesta += 1
                        st.rerun() # Ajuste 1: Forzar scroll al top
                else:
                    if st.button("💾 Finalizar y Enviar"):
                        faltan = [c for c in st.session_state.oblig if not st.session_state.resp_enc.get(c) or str(st.session_state.resp_enc.get(c)) in ["","Seleccionar..."]]
                        if faltan:
                            st.error("⚠️ Faltan preguntas obligatorias (*).")
                        else:
                            final = {'FECHA': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'DILIGENCIADOR': st.session_state.nombre_diligencia, 'EMAIL_VALIDADO': st.session_state.email_ingresado, **st.session_state.datos_temporales, **st.session_state.resp_enc}
                            pd.DataFrame([final]).to_csv('Consolidado_Encuestas_MEN.csv', mode='a', header=not pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'), index=False, encoding='utf-8-sig')
                            st.session_state.finalizado = True
                            st.rerun()

    else:
        st.error("Correo no encontrado en base EE 2026.")
        if st.button("Regresar"):
            st.session_state.clear()
            st.rerun()

# =====================================================================
# 5. PANEL DE ADMINISTRACIÓN INDEPENDIENTE (Ajuste 3)
# =====================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("🔒 Panel de Control - Área Funcional")
pw = st.text_input("Clave administrativa:", type="password")
if pw == "AdminMEN2026":
    if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
        df_v = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
        st.write(f"Total registros: {len(df_v)}")
        st.dataframe(df_v)
        st.download_button("📥 Descargar Consolidado (.csv)", data=df_v.to_csv(index=False).encode('utf-8-sig'), file_name='Consolidado_Encuestas_MEN.csv', mime='text/csv')
    else:
        st.info("Sin registros aún.")
elif pw != "":
    st.error("Acceso denegado.")