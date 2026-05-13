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

            col1, col2 = st.columns(2)
            bloqueado = not st.session_state.editando
            
            with col1:
                nombre_act = st.text_input("Nombre", value=fila.get('NOMBRE_ESTABLECIMIENTO', ''), disabled=bloqueado)
                dane_act = st.text_input("Código DANE", value=fila.get('CODIGO_DANE', ''), disabled=bloqueado)
            with col2:
                rector_act = st.text_input("Rector", value=fila.get('RECTOR', ''), disabled=bloqueado)
                dir_act = st.text_input("Dirección", value=fila.get('DIRECCION', ''), disabled=bloqueado)

            if not st.session_state.editando:
                if st.button("Actualizar"):
                    st.session_state.editando = True
                    st.rerun()
            else:
                if st.button("Guardar Información"):
                    st.session_state.editando = False
                    st.session_state.encuesta_iniciada = True
                    st.success("Información actualizada exitosamente.")
                    st.rerun()

            # =====================================================================
            # 3. INICIO DE LA ENCUESTA (Fase 2)
            # =====================================================================
            if st.session_state.encuesta_iniciada:
                st.markdown("---")
                st.subheader("Fase 2: Diligenciamiento de Encuesta")
                
                hojas = ["Identificación", "Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "docentes"]
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
                                var = str(row.get('Variable', idx)).strip()
                                obligatorio = str(row.get('Obligatorio', '')).strip().lower() == 'sí'
                                
                                if preg and preg != 'nan':
                                    marca_req = " **(*)**" if obligatorio else ""
                                    st.markdown(f"**{preg}**{marca_req}")
                                    
                                    if obligatorio and var not in st.session_state.campos_obligatorios:
                                        st.session_state.campos_obligatorios.append(var)
                                    
                                    # Listas de selección
                                    if 'lista' in tipo or 'selección' in tipo:
                                        opciones = [o.strip() for o in opts.split(';')] if ';' in opts else [opts]
                                        opciones = ["Seleccionar..."] + opciones
                                        valor_actual = st.session_state.respuestas_encuesta.get(var, "Seleccionar...")
                                        idx_actual = opciones.index(valor_actual) if valor_actual in opciones else 0
                                        
                                        respuesta = st.selectbox("Seleccione:", opciones, index=idx_actual, key=f"sel_{var}", label_visibility="collapsed")
                                        st.session_state.respuestas_encuesta[var] = respuesta
                                        
                                    # Entradas numéricas (restringidas a enteros sin números negativos)
                                    elif 'numérico' in tipo:
                                        valor_actual = st.session_state.respuestas_encuesta.get(var, 0)
                                        respuesta = st.number_input("Cantidad:", min_value=0, step=1, value=int(valor_actual), key=f"num_{var}", label_visibility="collapsed")
                                        st.session_state.respuestas_encuesta[var] = respuesta
                                        
                                    # Texto libre
                                    else:
                                        valor_actual = st.session_state.respuestas_encuesta.get(var, "")
                                        respuesta = st.text_input("Respuesta:", value=valor_actual, key=f"txt_{var}", label_visibility="collapsed")
                                        st.session_state.respuestas_encuesta[var] = respuesta
                                        
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    
                        except Exception as e:
                            st.error(f"No se pudo cargar la hoja '{nombre_hoja}': {e}")

                # =====================================================================
                # 4. VALIDACIÓN Y GUARDADO DE ENCUESTA
                # =====================================================================
                st.markdown("---")
                
                def validar_formulario():
                    faltantes = []
                    for campo in st.session_state.campos_obligatorios:
                        valor = st.session_state.respuestas_encuesta.get(campo)
                        if valor is None or str(valor).strip() == "" or str(valor) == "Seleccionar...":
                            faltantes.append(campo)
                    return faltantes

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("💾 Finalizar y Enviar Encuesta", use_container_width=True):
                        campos_faltantes = validar_formulario()
                        
                        if campos_faltantes:
                            st.error(f"⚠️ Faltan preguntas obligatorias por responder (*). Por favor revise las pestañas.")
                        else:
                            datos_finales = {
                                'EMAIL_INSTITUCIONAL': email_ingresado,
                                'NOMBRE_ESTABLECIMIENTO': fila.get('NOMBRE_ESTABLECIMIENTO', ''),
                                'CODIGO_DANE': fila.get('CODIGO_DANE', '')
                            }
                            datos_finales.update(st.session_state.respuestas_encuesta)
                            
                            df_exportar = pd.DataFrame([datos_finales])
                            archivo_salida = 'Consolidado_Encuestas_MEN.csv'
                            
                            try:
                                df_exportar.to_csv(archivo_salida, mode='a', header=not pd.io.common.file_exists(archivo_salida), index=False, encoding='utf-8-sig')
                                st.success("✅ ¡Información procesada y almacenada con éxito!")
                                st.balloons()
                            except Exception as e:
                                st.error(f"Error al guardar datos: {e}")

        else:
            st.error("El correo no se encuentra en la base de datos.")

except Exception as e:
    st.error(f"Error técnico: {e}")