# contreras-capital-farmer-exam

Sistema web para generar cotizaciones legales con integración de IA.

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Haco31/contreras-capital-farmer-exam.git
   cd contreras-capital-farmer-exam

1. Asegúrate de tener Python 3 instalado.

2. Instala Flask si no lo tienes:
   pip install flask

3. Ejecuta el servidor:
   python app.py

4. Abre tu navegador y ve a:
   http://localhost:5000

5. Completa el formulario y presiona "Generar Cotización".
   Se mostrará la cotización en formato JSON.
   Cada cotización se guarda automáticamente en cotizaciones.db (SQLite).

## Características implementadas

- Sistema completo de cotizaciones con frontend y backend
- Integración con OpenAI para análisis de casos legales
- Base de datos SQLite para almacenamiento persistente
- Diseño responsive para móviles
- Validaciones básicas de formulario
- Generación de números de cotización únicos
- Visualización profesional de resultados

NOTA:
- Si deseas ver las cotizaciones guardadas, puedes usar un visor de SQLite como DB Browser for SQLite.
