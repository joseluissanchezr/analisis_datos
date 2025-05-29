📊 AEMET Data Downloader y Visualizador Interactivo
Este proyecto permite consultar, descargar y visualizar de forma interactiva datos climatológicos proporcionados por la API de AEMET (Agencia Estatal de Meteorología de España). La herramienta es completamente interactiva desde la consola y está diseñada para facilitar el acceso a climatologías diarias, mensuales, valores normales y extremos registrados.

👥 Desarrollado por
Miguel Moure
Jinela Gonzalez
Javier Fauré
Lisa Culot
Maaja Smul

🚀 Características
🔍 Consulta por provincia y estación meteorológica.

📆 Soporte para rangos de fechas y fragmentación en intervalos menores para respetar la API.

📥 Descarga automática de datos en formato JSON y procesamiento a DataFrame (Pandas).

📊 Visualización interactiva con gráficos (requiere scripts externos).

🧼 Filtro y limpieza de datos personalizados a través de módulo externo.

🛠️ Requisitos
Python 3.8+

Conexión a internet

🗂️ Estructura del Proyecto
bash
Copy
Edit
📁 group3_data_analysis/
├── WIND DATA.py                         # Script principal
├── DATA_FILTER.py                       # Módulo para limpiar y guardar los datos
├── Graficas_interactivas_combinado.py   # Módulo para visualizar resultados
├── README.md                            # Este archivo

▶️ Cómo usar
Ejecuta el script principal:

WIND DATA.py
Sigue el menú interactivo:

Selecciona el tipo de datos:

Climatologías diarias

Climatologías mensuales/anuales

Extremos registrados

Valores normales

Elige la provincia y la estación meteorológica.

Introduce el rango de fechas o año según corresponda.

Espera a que se descarguen y procesen los datos.

Al finalizar, los datos se pueden guardar y visualizar mediante los módulos importados (DATA_FILTER.py y Graficas_interactivas_combinado.py).

🧠 Funcionalidades Clave del Código
División de fechas: evita errores en la API dividiendo solicitudes mayores a 6 meses.

Procesamiento por tipo de dato: adapta la transformación de los datos según el endpoint seleccionado.

Normalización de nombres: para guardar archivos con nombres limpios y compatibles con el sistema operativo.

Modularidad: se separan funciones de filtrado y visualización en archivos externos reutilizables.

🧼 Filtro y Limpieza
La limpieza personalizada se realiza mediante el archivo DATA_FILTER.py, que puedes adaptar a tus necesidades (por ejemplo, eliminar valores nulos, convertir unidades, etc.).

📈 Visualización
El módulo Graficas_interactivas_combinado.py permite realizar gráficos de los datos descargados. Asegúrate de que esté correctamente configurado y de tener instaladas las librerías necesarias.

