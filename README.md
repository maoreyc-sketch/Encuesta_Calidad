# Encuesta_Calidad
"Aplicación web en Streamlit para actualización de datos y Encuesta de Calidad - MEN"
# 📊 Encuesta de Calidad en la Información - MEN

Aplicación web desarrollada en Python (Streamlit) para el **Ministerio de Educación Nacional**. Esta herramienta permite la validación, actualización y recolección estructurada de datos de los Establecimientos Educativos a nivel nacional, garantizando la calidad y consolidación de la información institucional.

## 🚀 Características Principales

* **Autenticación Institucional:** Validación de acceso mediante cruce directo con la base de datos oficial (`EE 2026.xlsx`).
* **Control de Duplicidad:** Sistema de bloqueo automático que impide que un mismo establecimiento registre la encuesta más de una vez, asegurando la integridad de la base consolidada.
* **Flujo Guiado (Fase 1 y Fase 2):** Separación lógica entre la actualización de datos básicos (Rector, Teléfono, DANE, etc.) y los bloques dinámicos de la encuesta de calidad.
* **Navegación Modular:** Interfaz amigable con botones de avance y retroceso, y scroll automático para facilitar el diligenciamiento de los 5 módulos (Infraestructura, Computadores, Recursos Pedagógicos, Programas y Docentes).
* **Panel de Administración Seguro:** Acceso restringido con credenciales para que el área funcional pueda auditar y descargar los datos en tiempo real.

---

## 📖 Instrucciones de Uso (Para el Establecimiento Educativo)

1. **Ingreso al Sistema:** Ingrese a la URL pública de la aplicación.
2. **Validación:** Digite el **Correo electrónico institucional** (registrado en el Ministerio) y el **Nombre de quien diligencia**. Haga clic en "Iniciar Proceso".
3. **Fase 1 - Actualización de Datos:** Revise la información precargada de su institución. Si encuentra inconsistencias o datos faltantes, haga clic en **"✏️ Actualizar"**, modifique los campos necesarios y presione **"💾 Guardar Cambios"**. Si todo está correcto, simplemente haga clic en **"Continuar con Encuesta ➡️"**.
4. **Fase 2 - Encuesta:** Navegue por los módulos utilizando los botones inferiores. Todas las preguntas marcadas con `(*)` son de carácter obligatorio.
5. **Envío:** Al llegar al último bloque, haga clic en **"💾 FINALIZAR Y ENVIAR ENCUESTA"**. El sistema confirmará el guardado exitoso de sus respuestas.

---

## 🔒 Panel de Control (Para el Área Funcional del Ministerio)

El equipo interno puede monitorear y descargar los resultados en cualquier momento sin necesidad de diligenciar una encuesta ni acceder al código fuente:

1. Ingrese a la URL pública de la aplicación.
2. Desplácese hasta la parte inferior de la pantalla inicial, donde encontrará la sección **"🔐 Panel de Administración (Uso Interno)"**.
3. Haga clic para desplegar el menú e ingrese la **Clave Maestra** asignada al equipo.
4. Si la clave es correcta, el sistema mostrará una vista previa de la tabla con todos los registros recolectados hasta el momento.
5. Haga clic en el botón **"📥 Descargar Excel de Respuestas"** para exportar inmediatamente la base de datos consolidada en formato `.csv` (codificación UTF-8), lista para ser procesada en herramientas de análisis de datos o inteligencia de negocios.

---

## ⚙️ Especificaciones Técnicas y Despliegue

### Requisitos del Sistema
Para la ejecución de este proyecto, el entorno (local o en la nube) debe contar con las dependencias listadas en el archivo `requirements.txt`:
* `streamlit`
* `pandas`
* `openpyxl`

### Estructura de Archivos Requerida
La aplicación requiere los siguientes archivos en su directorio raíz para funcionar correctamente:
* `app.py`: Archivo principal con la lógica de la aplicación.
* `EE 2026.xlsx`: Base de datos maestra de los establecimientos educativos.
* `Encuesta_Calidad.xlsx`: Archivo con la estructura de las preguntas, organizado en pestañas por cada módulo.

### Ejecución Local
Para ejecutar la aplicación en un entorno de desarrollo local, abra la terminal en la carpeta del proyecto y ejecute:
```bash
streamlit run app.py
