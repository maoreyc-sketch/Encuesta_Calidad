# Encuesta_Calidad
"Aplicación web en Streamlit para actualización de datos y Encuesta de Calidad - MEN"
# 📊 Encuesta de Calidad en la Información - MEN

Aplicación web desarrollada en Python (Streamlit) para el **Ministerio de Educación Nacional**. Esta herramienta permite la validación, actualización y recolección estructurada de datos de los Establecimientos Educativos a nivel nacional, garantizando la calidad y consolidación de la información institucional.

## 🚀 Características Principales

* **Selección Guiada en Cascada:** El establecimiento se identifica mediante cuatro filtros encadenados (Departamento → Secretaría → Municipio → Establecimiento), de modo que cada nivel acota el siguiente y se evita cualquier confusión entre instituciones.
* **Identificación por Código DANE:** El establecimiento se resuelve internamente por su **Código DANE** (identificador único). El desplegable muestra el DANE junto al nombre, lo que permite diferenciar colegios con el mismo nombre dentro de un mismo municipio.
* **Control de Duplicidad:** Sistema de bloqueo automático que impide que un mismo establecimiento (validado por su Código DANE) registre la encuesta más de una vez, asegurando la integridad de la base consolidada.
* **Flujo Guiado (Fase 1 y Fase 2):** Separación lógica entre la verificación y actualización de datos básicos (Rector, Teléfono, DANE, etc.) y los bloques dinámicos de la encuesta de calidad.
* **Navegación Modular:** Interfaz amigable con botones de avance y retroceso, y scroll automático para facilitar el diligenciamiento de los 5 módulos (Infraestructura, Computadores, Recursos Pedagógicos, Programas y Docentes).
* **Almacenamiento Persistente:** Los registros se guardan en un repositorio de GitHub (persistente) con respaldo automático en CSV local.
* **Panel de Administración Seguro:** Acceso restringido con clave para que el área funcional pueda auditar, visualizar avances y descargar los datos en tiempo real.

---

## 📖 Instrucciones de Uso (Para el Establecimiento Educativo)

1. **Ingreso al Sistema:** Ingrese a la URL pública de la aplicación.
2. **Identificación del Establecimiento:** Seleccione en orden su **Departamento**, **Secretaría**, **Municipio** y, por último, su **Establecimiento Educativo**. En el desplegable de establecimientos verá el **Código DANE** junto al nombre; confirme que corresponde a su institución (esto es clave si existen colegios con el mismo nombre).
3. **Nombre de quien diligencia:** Escriba el nombre completo de quien diligencia la encuesta (rector u otro delegado) y haga clic en **"🚀 Iniciar Proceso"**.
4. **Fase 1 - Verificación de Datos:** Revise la información precargada de su institución. Si encuentra inconsistencias o datos faltantes, haga clic en **"✏️ Actualizar"**, modifique los campos necesarios y presione **"💾 Guardar Cambios"**. Si todo está correcto, simplemente haga clic en **"Continuar con Encuesta ➡️"**.
5. **Fase 2 - Encuesta:** Navegue por los módulos utilizando los botones inferiores. Todas las preguntas marcadas con `(*)` son de carácter obligatorio.
6. **Envío:** Al llegar al último bloque, haga clic en **"💾 FINALIZAR Y ENVIAR ENCUESTA"**. El sistema confirmará el guardado exitoso de sus respuestas.

> **Nota:** Si su establecimiento ya cuenta con un registro previo (validado por Código DANE), el sistema le informará que la encuesta ya fue diligenciada y no permitirá un segundo envío.

---

## 🔒 Panel de Control (Para el Área Funcional del Ministerio)

El equipo interno puede monitorear y descargar los resultados en cualquier momento sin necesidad de diligenciar una encuesta ni acceder al código fuente:

1. Ingrese a la URL pública de la aplicación.
2. Desplácese hasta la parte inferior de la pantalla inicial, donde encontrará la sección **"🔐 Acceso Administrador"**.
3. Despliegue el menú e ingrese la **Clave Maestra** asignada al equipo.
4. Si la clave es correcta, haga clic en **"📊 Abrir Panel de Administración Completo"**.
5. El panel muestra indicadores (KPIs) de avance, una barra de progreso general, y pestañas con: avance por Secretaría, establecimientos pendientes, todas las respuestas (con buscador y filtros) y otras descargas.
6. Use el botón **"📥 Descargar Base Completa en Excel (.xlsx)"** para exportar la base consolidada con cuatro hojas (Respuestas Completas, Resumen por Departamento, Establecimientos Pendientes y Estadísticas Generales). También hay descargas en formato `.csv` (codificación UTF-8) listas para análisis.

---

## ⚙️ Especificaciones Técnicas y Despliegue

### Requisitos del Sistema
Para la ejecución de este proyecto, el entorno (local o en la nube) debe contar con las dependencias listadas en el archivo `requirements.txt`:
* `streamlit`
* `pandas`
* `openpyxl`
* `requests`

### Estructura de Archivos Requerida
La aplicación requiere los siguientes archivos en su directorio raíz para funcionar correctamente:
* `app.py`: Archivo principal con la lógica de la aplicación.
* `EE 2026.xlsx`: Base de datos maestra de los establecimientos educativos. Debe contener, entre otras, las columnas `DEPARTAMENTO`, `SECRETARIA`, `MUNICIPIO`, `CODIGO_DANE`, `NOMBRE_ESTABLECIMIENTO`, `EMAIL`, `RECTOR`, `DIRECCION`, `BARRIO_VEREDA` y `TELEFONO`.
* `Encuesta_Calidad.xlsx`: Archivo con la estructura de las preguntas, organizado en pestañas por cada módulo.
* `logo_min.jpeg`: Logo institucional mostrado en el encabezado.

### Almacenamiento (opcional, recomendado para producción)
Para persistir los registros en GitHub, configure en **Streamlit > Settings > Secrets**:
```toml
github_token  = "ghp_xxxxxxxxxxxx"      # o github_pat_xxx (fine-grained)
github_repo   = "usuario/nombre-repositorio"
github_branch = "main"                   # opcional, por defecto "main"
```
Si no se configura, la aplicación funciona igual pero los datos se guardan solo en el CSV local de respaldo.

### Ejecución Local
Para ejecutar la aplicación en un entorno de desarrollo local, abra la terminal en la carpeta del proyecto y ejecute:
```bash
streamlit run app.py
```
