from flask import Flask, json, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

app = Flask(__name__)

# Token de Siigo (coloca tu token aquí o usa variables de entorno)
SIIGO_TOKEN = os.getenv('SIIGO_TOKEN', {api_key})

# Función para procesar los detalles del cliente
def process_customer(customer):
  return {
    "indentification": customer.get('phone', '00000000'),
    "name": customer.get('name', 'Cliente Desconocido'),
    "address": customer.get('address', 'Dirección Desconocida'),
    "email": customer.get('email','correo@desconocido.com'),
    "branch_office": 0
  }

def process_items(items):
  return [
    {
      "code": item.get('name'),
      "description":item.get('name'),
      "quantity": item.get('quantity',1),
      "price": item.get('price','0'),
      "tax": {"id": 111}  # Cambia al ID del impuesto según tu configuración
    }
    for item in items
  ]

def create_invoice(order, customer, items, total_price):
  invoice = {
    "document": {"id": order['id']},
    "date": datetime.now().strftime('%y-%m-%d'),
    "customer": process_customer(customer),
    "items": process_items(items),
    "payments": [
        {
          "id": 0000, #Ajustar el metodo de pago
          "value": total_price
        }
    ]
  }

  response = request.post(
    'https://api.siigo.com/v1/invoices',
    json.invoice,
    headers={
      'Authorization': f'Bearer {SIIGO_TOKEN}',
      'Content-Type': 'application/json'
    }
  )
  return response

# Endpoint para recibir el webhook de GloriaFood
@app.route('/webhook/gloriafood', methods=['POST'])
def receive_webhook():
    try:
      order =  request.json.get('order', {})
      customer =  request.json.get('customer', {})
      items =  request.json.get('items', [])
      total_price =  request.json.get('total_price', 0)

      # Crear la factura en Sigo
      siigo_response = create_invoice(order, customer, items, total_price)

      # Verificar la respuesta de Siigo
      if siigo_response.status_code == 200:
        return jsonify({"success": True, "data": siigo_response.json()}), 201
      else:
        return jsonify({
          "success": False,
          "error": siigo_response.json()
        }), siigo_response.status_code
    except Exception as e:
      return jsonify({"success", False, "error", str(e)}), 500

# Correr la aplicación en el puerto 8080
if __name__ == '__main__':
    print("Iniciando servidor...")
    app.run(host='0.0.0.0', port=8080)

# Paso para ejecutar el servidor
# 1. Activar el venv con source venv/bin/activate
# 2. Ejecutar este código con python3 weebhook.py -> esto activa el local host en el puerto 8080
# 3. iniciar el servidor de ngrok para exponer el servidor con ngrok http http://localhost:8080
# 4. El endpoint que genere debe ser el que se ingresa en Gloria Food en la integración

# Estado:
# La integración quedó configurada en el lado de Gloria Foods.  Hay que verificar si al restablecer ngrok la enpoint cambia.
# Quedaría pendiente de ejecutar algunas pruebas y ver donde se generan.

# 1. Configuración Inicial
# Validar los datos de autenticación:
# - Confirmar que las credenciales (usuario, access_key) para Siigo están configuradas correctamente.
# - Probar el flujo de generación del token OAuth y verificar que es válido en el ambiente de pruebas.
#
# Preparar el ambiente de pruebas de GloriaFood:
# - [Done] Activar el modo de pruebas o simulación de órdenes en GloriaFood.
# - [Done] Configurar el webhook en GloriaFood con la URL generada por ngrok.
#
# Instalar dependencias necesarias en producción:
# - [Done] Configurar el entorno virtual (venv) e instalar dependencias requeridas (Flask, Requests, etc.).

# 2. Desarrollo y Pruebas
# Implementar manejo de errores robusto:
# - Validar datos faltantes o inconsistentes en las órdenes recibidas.
# - Capturar errores específicos al interactuar con la API de Siigo (e.g., token expirado, formato incorrecto).
#
# Probar el flujo completo en ambiente de pruebas:
# - Enviar órdenes simuladas desde GloriaFood y confirmar la recepción en el webhook.
# - Validar que las órdenes se conviertan en facturas en el entorno de pruebas de Siigo.
# - Revisar los logs para identificar y corregir puntos de fallo.
#
# Configurar logs en un archivo persistente:
# - Registrar todos los eventos relevantes en un archivo "app.log" para monitoreo y depuración.

# 3. Seguridad
# Proteger la URL del webhook:
# - Configurar autenticación básica (e.g., token en headers) para asegurarte de que solo GloriaFood pueda enviar datos.
#
# Sanitizar los datos recibidos:
# - Validar y filtrar los datos para evitar inyecciones o información maliciosa.
#
# Asegurar las comunicaciones:
# - Configurar HTTPS en el servidor donde se desplegará el webhook.
# - Garantizar que las llamadas a la API de Siigo también utilicen HTTPS.

# 4. Despliegue en Producción
# Seleccionar un servidor para producción:
# - Usar un servicio como AWS, Google Cloud, Azure o un servidor dedicado.
# - Configurar un servidor WSGI como Gunicorn o uWSGI para manejar solicitudes Flask.
#
# Configurar un proxy inverso:
# - Usar NGINX o Apache para enrutar las solicitudes al servidor Flask.
#
# Actualizar el webhook en GloriaFood:
# - Cambiar la URL del webhook al dominio o IP del servidor en producción.
#
# Habilitar supervisión del servicio:
# - Usar herramientas como PM2, Supervisor o systemd para mantener activo el servidor.
# - Configurar alertas con servicios como UptimeRobot para monitorear la disponibilidad.

# 5. Validación y Monitoreo
# Hacer pruebas en producción:
# - Realizar pedidos reales en GloriaFood para validar que las facturas se generen correctamente en Siigo.
# - Revisar los logs para asegurarte de que los datos se procesen sin errores.
#
# Configurar métricas y alertas:
# - Usar herramientas como Grafana o Prometheus para rastrear métricas clave (e.g., tiempo de respuesta, errores).
#
# Establecer políticas de respaldo:
# - Crear copias de seguridad regulares de configuraciones y logs.

# Extras Opcionales
# Documentación:
# - Crear un documento interno explicando el flujo de integración, manejo de errores y mantenimiento.
#
# Automatización de despliegue:
# - Usar Docker y CI/CD (GitHub Actions, Jenkins) para facilitar actualizaciones y despliegues futuros.
