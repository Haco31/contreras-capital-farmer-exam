from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import openai
import os
from dotenv import load_dotenv
import random

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Precios de los servicios
PRECIOS = {
    "Constitución de empresa": 1500,
    "Defensa laboral": 2000,
    "Consultoría tributaria": 800
}

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cotizaciones
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  numero_cotizacion TEXT,
                  nombre_cliente TEXT,
                  email TEXT,
                  tipo_servicio TEXT,
                  descripcion TEXT,
                  precio REAL,
                  fecha TEXT,
                  complejidad TEXT,
                  ajuste_precio INTEGER,
                  servicios_adicionales TEXT,
                  propuesta_texto TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Generar número de cotización único
def generar_numero_cotizacion():
    year = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"COT-{year}-{random_num}"

# Función para analizar con IA
def analizar_con_ia(descripcion, tipo_servicio):
    try:
        prompt = f"""
        Eres un asistente legal experto. Analiza este caso legal:

        Descripción: {descripcion}
        Tipo de servicio: {tipo_servicio}

        Proporciona un análisis con:
        1. Nivel de complejidad (Baja, Media o Alta)
        2. Ajuste de precio recomendado (0%, 25% o 50%)
        3. Servicios adicionales necesarios (si aplica)
        4. Genera una propuesta profesional de 2-3 párrafos para el cliente, incluyendo servicios incluidos, tiempo estimado y condiciones básicas.

        Devuelve la respuesta en formato JSON con las claves: complejidad, ajuste_precio, servicios_adicionales, propuesta_texto.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente legal experto que analiza casos y genera cotizaciones profesionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parsear la respuesta JSON del modelo
        content = response.choices[0].message.content
        return eval(content)
    
    except Exception as e:
        print(f"Error al conectar con la API de IA: {e}")
        return {
            'complejidad': 'Media',
            'ajuste_precio': 0,
            'servicios_adicionales': [],
            'propuesta_texto': 'Propuesta estándar generada debido a un error en el análisis de IA.'
        }

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para generar cotización
@app.route('/generar-cotizacion', methods=['POST'])
def generar_cotizacion():
    try:
        # Obtener datos del formulario
        data = request.form
        nombre_cliente = data['nombre']
        email = data['email']
        tipo_servicio = data['tipo_servicio']
        descripcion = data['descripcion']
        
        # Generar cotización básica
        numero_cotizacion = generar_numero_cotizacion()
        precio_base = PRECIOS[tipo_servicio]
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Analizar con IA
        analisis_ia = analizar_con_ia(descripcion, tipo_servicio)
        
        # Calcular precio final con ajuste
        precio_final = precio_base * (1 + analisis_ia['ajuste_precio'] / 100)
        
        # Guardar en base de datos
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO cotizaciones 
                    (numero_cotizacion, nombre_cliente, email, tipo_servicio, descripcion, precio, fecha,
                     complejidad, ajuste_precio, servicios_adicionales, propuesta_texto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (numero_cotizacion, nombre_cliente, email, tipo_servicio, descripcion, precio_final, fecha,
                  analisis_ia['complejidad'], analisis_ia['ajuste_precio'], 
                  ', '.join(analisis_ia['servicios_adicionales']) if isinstance(analisis_ia['servicios_adicionales'], list) else analisis_ia['servicios_adicionales'],
                  analisis_ia['propuesta_texto']))
        conn.commit()
        conn.close()
        
        # Preparar respuesta
        cotizacion = {
            'numero_cotizacion': numero_cotizacion,
            'nombre_cliente': nombre_cliente,
            'email': email,
            'tipo_servicio': tipo_servicio,
            'descripcion': descripcion,
            'precio_base': precio_base,
            'ajuste_precio': analisis_ia['ajuste_precio'],
            'precio_final': precio_final,
            'fecha': fecha,
            'complejidad': analisis_ia['complejidad'],
            'servicios_adicionales': analisis_ia['servicios_adicionales'],
            'propuesta_texto': analisis_ia['propuesta_texto']
        }
        
        return render_template('resultado.html', cotizacion=cotizacion)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)