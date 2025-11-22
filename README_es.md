# USDA Crop Insights — ETL y Análisis con Python y MySQL

Este proyecto desarrolla un **pipeline ETL completo** para **extraer, transformar y cargar** datos agrícolas desde la **API Quick Stats del USDA** hacia una **base de datos MySQL**, con el objetivo de generar **análisis e insights sobre las tendencias de precios agrícolas** en los distintos estados de EE. UU.

---

## Descripción General

- **Objetivo:** Automatizar la recolección y el análisis de estadísticas agrícolas (por ejemplo, precios de soja o maíz).
- **Fuente de datos:** [USDA NASS Quick Stats API](https://quickstats.nass.usda.gov/api)
- **Tecnologías utilizadas:** Python · Pandas · SQLAlchemy · MySQL · Matplotlib
- **Enfoque:** Automatización ETL real y análisis exploratorio de datos (EDA)


⚙️ Instrucciones de Instalación

1 - Clonar este repositorio
git clone https://github.com/tuusuario/usda-crop-insights.git
cd usda-crop-insights

2 - Crear y activar un entorno virtual
python3 -m venv venv
source venv/bin/activate   # En macOS/Linux
venv\Scripts\activate      # En Windows

3 - Instalar dependencias
pip install -r requirements.txt

4 - Configurar las variables de entorno
Crear un archivo .env dentro de la carpeta config/ con el siguiente contenido:
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_HOST=localhost
MYSQL_DATABASE=usda_data
USDA_API_KEY=tu_api_key


5 - Ejecutar el pipeline ETL
python src/run_etl.py


📊 Ejemplo de Resultados

Después de ejecutar el ETL, los datos limpios se almacenan en la tabla usda_observations en MySQL.
Esto permite generar consultas y análisis como:

Promedio de precios por cultivo y año
Variación interanual de precios
Comparación regional entre estados
Ejemplo de consulta SQL:

SELECT year, commodity_desc, AVG(price) AS precio_promedio
FROM usda_observations
WHERE commodity_desc = 'SOYBEANS'
GROUP BY year, commodity_desc
ORDER BY year;

## API (FastAPI)

Una vez que el pipeline ETL almacena los datos limpios del USDA en la base de datos MySQL, este servicio FastAPI permite consultar los resultados procesados

📈 Mejoras Futuras

Integrar un panel interactivo de visualización de datos (Streamlit o Plotly Dash).
Agregar filtros fáciles de usar y estadísticas resumidas.
Opcionalmente desplegar en línea todo el sistema ETL + API + Dashboard para demostración.

👨‍💻 Autor

Emanuel Pernice
Analista de Datos & Desarrollador Python
📧 [perniceemanuel@gmail.com]