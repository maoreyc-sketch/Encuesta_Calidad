import streamlit as st
import pandas as pd

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
# 2. CARGA DE BASE DE DATOS (Fase 1)
# =====================================================================
@st.cache_data
def cargar_datos_ee():
    archivo_ee = "EE 2026.xlsx"
    df = pd.read_excel(archivo_ee, sheet_name=0, dtype=str)
    if 'EMAIL' in df.columns:
        df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
    return df

try:
    df_ee = cargar_datos_ee()
    
    email_ingresado = st.text_input("Ingrese el correo electrónico del establecimiento:").strip().lower()

    if email_ingresado:
        resultado = df_ee[df_ee['EMAIL'] == email_ingresado]
        
        if not resultado.empty:
            fila = resultado.iloc[0]
            
            if 'editando' not in st.session_state:
                st.session_state.editando = False
            if 'encuesta_iniciada' not in st.session_state:
                st.session_state.encuesta_iniciada = False

            # Ajuste 1: Adición de campos solicitados (Barrio, Teléfono, Depto, Municipio)
            col1, col2 = st.columns(2)
            bloqueado = not st.session_state.editando
            
            with col1:
                nombre_act = st.text_input("Nombre del Establecimiento", value=fila.get('NOMBRE_ESTABLECIMIENTO', ''), disabled=bloqueado)
                dane_act = st.text_input("Código DANE", value=fila.get('CODIGO_DANE', ''), disabled=bloqueado)
                depto_act = st.text_input("Departamento", value=fila.get('DEPARTAMENTO', ''), disabled=bloqueado)
                muni_act = st.text_input("Municipio / Secretaría", value=fila.get('SECRETARIA', ''), disabled=bloqueado)
            with col2:
                rector_act = st.text_input("Rector", value=fila.get('RECTOR', ''), disabled=bloqueado)
                dir_act = st.text_input("Dirección", value=fila.get('DIRECCION', ''), disabled=bloqueado)
                barrio_act = st.text_input("Barrio / Vereda", value=fila.get('BARRIO_VEREDA', ''), disabled=bloqueado)
                tel_act = st.text_input("Teléfono", value=fila.get('TELEFONO', ''), disabled=bloqueado)

            # Ajuste 2: Lógica de botones (Actualizar vs Continuar)
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                if not st.session_state.editando:
                    if st.button("Actualizar Datos"):
                        st.session_state.editando = True
                        st.rerun()
                else:
                    if st.button("Guardar Cambios"):
                        st.session_state.datos_temporales = {
                            'NOMBRE': nombre_act, 'DANE': dane_act, 'DEPTO': depto_act, 'MUNI': muni_act,
                            'RECTOR': rector_act, 'DIR': dir_act, 'BARRIO': barrio_act, 'TEL': tel_act
                        }
                        st.session_state.editando = False
                        st.session_state.encuesta_iniciada = True
                        st.success("Información actualizada y guardada.")
                        st.rerun()

            with col_btn2:
                # Botón de continuar si los datos son correctos de entrada
                if not st.session_state.editando and not st.session_state.encuesta_iniciada:
                    if st.button("Continuar con Encuesta"):
                        # Se guardan los datos existentes sin modificaciones
                        st.session_state.datos_temporales = {
                            'NOMBRE': nombre_act, 'DANE': dane_act, 'DEPTO': depto_act, 'MUNI': muni_act,
                            'RECTOR': rector_act, 'DIR': dir_act, 'BARRIO': barrio_act, 'TEL': tel_act
                        }
                        st.session_state.encuesta_iniciada = True
                        st.rerun()

            # =====================================================================
            # 3. INICIO DE LA ENCUESTA (Fase 2)
            # =====================================================================
            if st.session_state.encuesta_iniciada:
                st.markdown("---")
                st.subheader("Fase 2: Diligenciamiento de Encuesta")
                
                # Ajuste 3: Se remueve "Identificación" de la lista de bloques
                hojas = ["Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "Docentes"]
                tabs = st.tabs(hojas)
                
                if 'respuestas_encuesta' not in st.session_state:
                    st.session_state.respuestas_encuesta = {}
                if 'campos_obligatorios' not in st.session_state:
                    st.session_state.campos_obligatorios = []

                for i, nombre_hoja in enumerate(hojas):
                    with tabs[i]:
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
                                    st.markdown(f"**{preg}**{marca_req}")
                                    
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
                                        # Restricción: Números enteros, no negativos
                                        respuesta = st.number_input("Cantidad:", min_value=0, step=1, value=int(v_actual), key=f"num_{var}", label_visibility="collapsed")
                                        st.session_state.respuestas_encuesta[var] = respuesta
                                        
                                    else:
                                        v_actual = st.session_state.respuestas_encuesta.get(var, "")
                                        respuesta = st.text_input("Respuesta:", value=v_actual, key=f"txt_{var}", label_visibility="collapsed")
                                        st.session_state.respuestas_encuesta[var] = respuesta
                                        
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    
                        except Exception as e:
                            st.error(f"Error en bloque '{nombre_hoja}': {e}")

                # =====================================================================
                # 4. VALIDACIÓN Y GUARDADO FINAL
                # =====================================================================
                st.markdown("---")
                
                def validar_faltantes():
                    faltan = []
                    for c in st.session_state.campos_obligatorios:
                        val = st.session_state.respuestas_encuesta.get(c)
                        if val is None or str(val).strip() == "" or str(val) == "Seleccionar...":
                            faltan.append(c)
                    return faltan

                col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
                with col_f2:
                    if st.button("💾 Finalizar y Enviar Encuesta", use_container_width=True):
                        err = validar_faltantes()
                        if err:
                            st.error(f"⚠️ Por favor complete todas las preguntas obligatorias (*).")
                        else:
                            final_data = {
                                'EMAIL_VALIDADO': email_ingresado,
                                **st.session_state.datos_temporales,
                                **st.session_state.respuestas_encuesta
                            }
                            df_final = pd.DataFrame([final_data])
                            try:
                                df_final.to_csv('Consolidado_Encuestas_MEN.csv', mode='a', header=not pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'), index=False, encoding='utf-8-sig')
                                st.success("✅ Encuesta enviada correctamente.")
                                st.balloons()
                            except Exception as e:
                                st.error(f"Error al guardar: {e}")

        else:
            st.error("Correo no encontrado.")

except Exception as e:
    st.error(f"Error de carga: {e}")
    # =====================================================================
# 5. PANEL DE ADMINISTRACIÓN (ACCESO RESTRINGIDO)
# =====================================================================
st.markdown("---")
st.subheader("🔒 Panel de Administración de Datos")

# Campo de texto que oculta los caracteres ingresados
clave_acceso = st.text_input("Ingrese la clave maestra para visualizar o descargar la base de datos consolidada:", type="password")

# Aquí defines tu contraseña segura
if clave_acceso == "AdminMEN2026": 
    with st.expander("Ver base de datos consolidada (Acceso Autorizado)", expanded=True):
        try:
            if pd.io.common.file_exists('Consolidado_Encuestas_MEN.csv'):
                df_revisar = pd.read_csv('Consolidado_Encuestas_MEN.csv', encoding='utf-8-sig')
                st.dataframe(df_revisar) # Muestra la tabla interactiva
                
                # Botón para descargar el archivo directamente desde la web
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
    # Si ingresan texto pero no es la clave correcta
    st.error("❌ Clave incorrecta. Acceso denegado a la base de datos.")