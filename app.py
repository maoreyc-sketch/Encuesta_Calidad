import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================================================
# 1. ESTILOS MEN
# =====================================================================
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
# 2. FUNCIONES DE CARGA Y VALIDACIÓN
# =====================================================================
@st.cache_data
def cargar_datos_ee():
    archivo_ee = "EE 2026.xlsx"
    df = pd.read_excel(archivo_ee, sheet_name=0, dtype=str)
    if 'EMAIL' in df.columns:
        df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
    return df

def verificar_duplicidad(email):
    # Ajuste 2: Evitar duplicidad buscando en el consolidado histórico
    if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
        try:
            df_historico = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
            if 'EMAIL_VALIDADO' in df_historico.columns:
                if email in df_historico['EMAIL_VALIDADO'].values:
                    return True
        except Exception:
            pass
    return False

# =====================================================================
# 3. INICIO DE SESIÓN Y VARIABLES DE ESTADO
# =====================================================================
if 'iniciado' not in st.session_state:
    st.session_state.iniciado = False
if 'paso_encuesta' not in st.session_state:
    st.session_state.paso_encuesta = 0
if 'editando' not in st.session_state:
    st.session_state.editando = False
if 'encuesta_iniciada' not in st.session_state:
    st.session_state.encuesta_iniciada = False

# Ajustes 5 y 6: Pantalla inicial con campos de correo y nombre
if not st.session_state.iniciado:
    st.info("👋 Bienvenido. Por favor ingrese los datos para acceder al sistema.")
    
    col_ini1, col_ini2 = st.columns(2)
    with col_ini1:
        email_temp = st.text_input("Correo electrónico del establecimiento:")
    with col_ini2:
        nombre_temp = st.text_input("Nombre de quien diligencia:")
        
    if st.button("🚀 Iniciar Encuesta", use_container_width=True):
        if not email_temp or not nombre_temp:
            st.warning("⚠️ Debe ingresar tanto el correo como su nombre para continuar.")
        else:
            st.session_state.email_ingresado = email_temp.strip().lower()
            st.session_state.nombre_diligencia = nombre_temp.strip()
            st.session_state.iniciado = True
            st.rerun()

else:
    # Si ya inició, verificamos si hay duplicidad antes de continuar
    if verificar_duplicidad(st.session_state.email_ingresado):
        st.error(f"❌ El establecimiento con correo '{st.session_state.email_ingresado}' ya registró una encuesta en el sistema.")
        st.warning("Para evitar duplicidad en la base de datos, no es posible diligenciarla nuevamente.")
        if st.button("Volver al inicio"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        try:
            df_ee = cargar_datos_ee()
            resultado = df_ee[df_ee['EMAIL'] == st.session_state.email_ingresado]
            
            if not resultado.empty:
                fila = resultado.iloc[0]
                
                # =====================================================================
                # FASE 1: VALIDACIÓN DE DATOS
                # =====================================================================
                if not st.session_state.encuesta_iniciada:
                    st.subheader("Fase 1: Verificación de Datos Institucionales")
                    bloqueado = not st.session_state.editando
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre_act = st.text_input("Nombre del Establecimiento", value=fila.get('NOMBRE_ESTABLECIMIENTO', ''), disabled=bloqueado)
                        dane_act = st.text_input("Código DANE", value=fila.get('CODIGO_DANE', ''), disabled=bloqueado)
                        depto_act = st.text_input("Departamento", value=fila.get('DEPARTAMENTO', ''), disabled=bloqueado)
                        muni_act = st.text_input("Municipio / Secretaría", value=fila.get('SECRETARIA', ''), disabled=bloqueado)
                        # Ajuste 7: Campo DANE Nuevo
                        dane_nuevo = st.text_input("Código DANE Nuevo (*Solo si aplica)", value="", disabled=bloqueado)
                    with col2:
                        rector_act = st.text_input("Rector", value=fila.get('RECTOR', ''), disabled=bloqueado)
                        dir_act = st.text_input("Dirección", value=fila.get('DIRECCION', ''), disabled=bloqueado)
                        barrio_act = st.text_input("Barrio / Vereda", value=fila.get('BARRIO_VEREDA', ''), disabled=bloqueado)
                        tel_act = st.text_input("Teléfono", value=fila.get('TELEFONO', ''), disabled=bloqueado)
                        # Ajuste 7: Campo Observaciones
                        observaciones = st.text_area("Observaciones", value="", disabled=bloqueado, height=68)

                    # Botones de Fase 1
                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        if not st.session_state.editando:
                            if st.button("Actualizar"):
                                st.session_state.editando = True
                                st.rerun()
                        else:
                            if st.button("Guardar Cambios"):
                                st.session_state.datos_temporales = {
                                    'NOMBRE': nombre_act, 'DANE': dane_act, 'DEPTO': depto_act, 'MUNI': muni_act,
                                    'RECTOR': rector_act, 'DIR': dir_act, 'BARRIO': barrio_act, 'TEL': tel_act,
                                    'DANE_NUEVO': dane_nuevo, 'OBSERVACIONES': observaciones
                                }
                                st.session_state.editando = False
                                st.session_state.encuesta_iniciada = True
                                st.success("Información actualizada.")
                                st.rerun()

                    with col_btn2:
                        if not st.session_state.editando:
                            if st.button("Continuar con Encuesta ➡️"):
                                st.session_state.datos_temporales = {
                                    'NOMBRE': nombre_act, 'DANE': dane_act, 'DEPTO': depto_act, 'MUNI': muni_act,
                                    'RECTOR': rector_act, 'DIR': dir_act, 'BARRIO': barrio_act, 'TEL': tel_act,
                                    'DANE_NUEVO': dane_nuevo, 'OBSERVACIONES': observaciones
                                }
                                st.session_state.encuesta_iniciada = True
                                st.rerun()

                # =====================================================================
                # FASE 2: DILIGENCIAMIENTO DINÁMICO (Ajustes 3 y 4)
                # =====================================================================
                if st.session_state.encuesta_iniciada:
                    st.markdown("---")
                    st.subheader("Fase 2: Módulos de la Encuesta")
                    
                    hojas = ["Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "docentes"]
                    
                    # Barra de progreso y menú de navegación que reemplaza st.tabs
                    progreso = (st.session_state.paso_encuesta + 1) / len(hojas)
                    st.progress(progreso)
                    
                    # Radio button horizontal que simula las pestañas
                    menu_modulos = st.radio("Navegación:", hojas, index=st.session_state.paso_encuesta, horizontal=True, label_visibility="collapsed")
                    if hojas.index(menu_modulos) != st.session_state.paso_encuesta:
                        st.session_state.paso_encuesta = hojas.index(menu_modulos)
                        st.rerun()

                    if 'respuestas_encuesta' not in st.session_state:
                        st.session_state.respuestas_encuesta = {}
                    if 'campos_obligatorios' not in st.session_state:
                        st.session_state.campos_obligatorios = []

                    nombre_hoja = hojas[st.session_state.paso_encuesta]
                    st.markdown(f"#### Bloque: {nombre_hoja}")
                    
                    try:
                        df_preguntas = pd.read_excel("Encuesta_Calidad.xlsx", sheet_name=nombre_hoja, skiprows=2)
                        
                        for idx, row in df_preguntas.iterrows():
                            preg = str(row.get('Pregunta / campo', row.get('Pregunta', '')))
                            tipo = str(row.get('Tipo de respuesta', row.get('Tipo', ''))).lower()
                            opts = str(row.get('Opciones o criterio', row.get('Opciones', '')))
                            var = str(row.get('Variable', f"{nombre_hoja}_{idx}")).strip()
                            obligatorio = str(row.get('Obligatorio', '')).strip().lower() == 'sí'
                            
                            if preg and preg != 'nan':
                                marca_req = " **(*)**" if obligatorio else ""
                                st.write(f"**{preg}**{marca_req}")
                                
                                if obligatorio and var not in st.session_state.campos_obligatorios:
                                    st.session_state.campos_obligatorios.append(var)
                                
                                if 'lista' in tipo or 'selección' in tipo:
                                    opciones = [o.strip() for o in opts.split(';')] if ';' in opts else [opts]
                                    opciones = ["Seleccionar..."] + opciones
                                    v_actual = st.session_state.respuestas_encuesta.get(var, "Seleccionar...")
                                    idx_act = opciones.index(v_actual) if v_actual in opciones else 0
                                    
                                    respuesta = st.selectbox("Seleccione:", opciones, index=idx_act, key=f"sel_{var}", label_visibility="collapsed")
                                    st.session_state.respuestas_encuesta[var] = respuesta
                                    
                                elif 'numérico' in tipo:
                                    v_actual = st.session_state.respuestas_encuesta.get(var, 0)
                                    respuesta = st.number_input("Cantidad:", min_value=0, step=1, value=int(v_actual), key=f"num_{var}", label_visibility="collapsed")
                                    st.session_state.respuestas_encuesta[var] = respuesta
                                    
                                else:
                                    v_actual = st.session_state.respuestas_encuesta.get(var, "")
                                    respuesta = st.text_input("Respuesta:", value=v_actual, key=f"txt_{var}", label_visibility="collapsed")
                                    st.session_state.respuestas_encuesta[var] = respuesta
                                    
                                st.markdown("<br>", unsafe_allow_html=True)
                                
                    except Exception as e:
                        st.error(f"Error cargando el bloque '{nombre_hoja}': {e}")

                    # =====================================================================
                    # BOTONES DE NAVEGACIÓN Y GUARDADO FINAL
                    # =====================================================================
                    st.markdown("---")
                    col_nav_izq, col_nav_cen, col_nav_der = st.columns([1, 1, 1])
                    
                    with col_nav_izq:
                        if st.session_state.paso_encuesta > 0:
                            if st.button("⬅️ Anterior Módulo", use_container_width=True):
                                st.session_state.paso_encuesta -= 1
                                st.rerun()
                                
                    with col_nav_der:
                        if st.session_state.paso_encuesta < len(hojas) - 1:
                            if st.button("Siguiente Módulo ➡️", use_container_width=True):
                                st.session_state.paso_encuesta += 1
                                st.rerun()
                        else:
                            # Ajuste 4: Botón de finalizar solo visible en el último bloque
                            if st.button("💾 Finalizar y Enviar Encuesta", use_container_width=True):
                                faltan = [c for c in st.session_state.campos_obligatorios if not st.session_state.respuestas_encuesta.get(c) or str(st.session_state.respuestas_encuesta.get(c)).strip() == "" or str(st.session_state.respuestas_encuesta.get(c)) == "Seleccionar..."]
                                
                                if faltan:
                                    st.error(f"⚠️ Faltan preguntas obligatorias (*). Navegue por los módulos para completarlas.")
                                else:
                                    # Ajuste 1: Registro de fecha y hora actual
                                    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    final_data = {
                                        'FECHA_REGISTRO': fecha_registro,
                                        'NOMBRE_DILIGENCIADOR': st.session_state.nombre_diligencia,
                                        'EMAIL_VALIDADO': st.session_state.email_ingresado,
                                        **st.session_state.datos_temporales,
                                        **st.session_state.respuestas_encuesta
                                    }
                                    df_final = pd.DataFrame([final_data])
                                    try:
                                        df_final.to_csv('Consolidado_Encuestas_MEN.csv', mode='a', header=not pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'), index=False, encoding='utf-8-sig')
                                        st.success("✅ ¡Encuesta procesada exitosamente! Gracias por su participación.")
                                        st.balloons()
                                        
                                        # Limpiar sesión para permitir nueva captura si se desea
                                        if st.button("Volver al Inicio para registrar otra institución"):
                                            for key in list(st.session_state.keys()):
                                                del st.session_state[key]
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al guardar: {e}")

            else:
                st.error("❌ El correo no se encuentra en la base maestra EE 2026. Por favor verifique.")
                if st.button("Intentar con otro correo"):
                    st.session_state.iniciado = False
                    st.rerun()

        except Exception as e:
            st.error(f"Error técnico conectando a la base: {e}")

# =====================================================================
# 4. PANEL DE ADMINISTRACIÓN (ACCESO RESTRINGIDO)
# =====================================================================
st.markdown("---")
st.subheader("🔒 Panel de Administración de Datos")
clave_acceso = st.text_input("Ingrese la clave maestra para visualizar o descargar la base de datos consolidada:", type="password")

if clave_acceso == "AdminMEN2026": 
    with st.expander("Ver base de datos consolidada (Acceso Autorizado)", expanded=True):
        try:
            if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
                df_revisar = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
                st.dataframe(df_revisar)
                
                csv = df_revisar.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Descargar Base Completa (.csv)",
                    data=csv,
                    file_name='Consolidado_Encuestas_MEN.csv',
                    mime='text/csv',
                )
            else:
                st.info("Aún no hay encuestas registradas en la base de datos.")
        except Exception as e:
            st.error(f"No se pudo cargar la vista previa: {e}")
elif clave_acceso != "":
    st.error("❌ Clave incorrecta. Acceso denegado a la base de datos.")