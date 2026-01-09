# IMPORTACIONES Y CONFIGURACIÓN INICIAL
# Librerías necesarias para el procesamiento de facturas con OCR y IA

# Azure Cognitive Services para OCR (reconocimiento óptico de caracteres)
from azure.cognitiveservices.vision.computervision.models import OperationsStatusCodes
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# PIL para manipulación de imágenes
from PIL import Image

# Librerías estándar de Python
import os   
import csv  # Para manejo de archivos CSV
import json # Para manejo de datos JSON

# Variables de entorno y APIs externas
from dotenv import load_dotenv  # Para cargar variables de entorno desde .env
from openai import OpenAI  # Cliente para API de OpenAI GPT

# Módulo personalizado para convertir PDFs a imágenes
import convert_to_img

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configurar cliente de Azure Computer Vision
key = os.getenv("AZURE_VISION_KEY")  # Clave API de Azure
endpoint = os.getenv("AZURE_VISION_ENDPOINT")  # Endpoint de Azure Cognitive Services
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

# Configurar cliente de OpenAI
client = OpenAI()  # Cliente para hacer llamadas a la API de OpenAI GPT

# Función que valida si un archivo es una imagen válida
# Parámetros:
#   - file_path: ruta del archivo a validar
# Retorna:
#   - True si el archivo es una imagen válida
#   - False si no es válido o hay error
def validate_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
            print("La imagen es válida.")
            return True
    except Exception as e:
        print(f"El archivo no es una imagen válida: {e}")
        return False

# Función que realiza OCR (Optical Character Recognition) usando Azure Cognitive Services
# Parámetros:
#   - roi_name: ruta de la imagen a procesar
#   - computervision_client: cliente de Azure Computer Vision
# Retorna:
#   - cleaned_ocr_text: texto extraído limpio de la imagen
#   - ocr_emails: lista de emails encontrados (actualmente no implementada)
# NOTA: Esta función está incompleta - el bloque try está vacío
def cognitive_azure_ocr(roi_name, computervision_client):
    cleaned_ocr_text = ""
    ocr_emails = []

    try:
        '''
        try vacío
        '''
    except Exception as e:
        print("ERROR OCR COGNITIVE AZURE: ", e)

    return cleaned_ocr_text, ocr_emails

# Función que utiliza OpenAI GPT para extraer datos estructurados de una factura
# Parámetros:
#   - texto_factura: texto plano extraído de la imagen de la factura
# Retorna:
#   - datos_factura_str: cadena JSON con los datos extraídos de la factura
#   Incluye campos como: Fecha, Número, Cliente, Domicilio, Ciudad, NIF, Subtotal, IVA, Total a pagar
def extraer_datos_factura(texto_factura):
    prompt = f"""
    Extrae los siguientes campos del texto proporcionado y devuelve los resultados en formato JSON:
    - Fecha
    - Número
    - Cliente
    - Domicilio
    - Ciudad
    - NIF
    - Subtotal
    - IVA
    - Total a pagar

    Texto:
    {texto_factura}
    """
    # MÉTODO: Envía la solicitud a la API de OpenAI
    # client.chat.completions.create() crea una completación (respuesta) del chat
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Modelo de IA a utilizar
        messages=[{"role": "system", "content": "Eres un experto en análisis estructurado."},
                  {"role": "user", "content": prompt}],  # Historial del chat
        max_tokens=300  # Máximo número de tokens (palabras/piezas) en la respuesta
    )

    # Obtener la respuesta y limpiar la cadena JSON
    datos_factura_str = response.choices[0].message.content.strip()
    datos_factura_str = datos_factura_str.replace('```json', '').replace('```', '').strip()

    return datos_factura_str

# Función que agrega una fila de datos de factura a un archivo CSV
# Parámetros:
#   - file_name: nombre del archivo CSV donde guardar los datos
#   - data: diccionario con los datos extraídos de la factura
# Funcionalidad:
#   - Si el archivo no existe, crea los encabezados del CSV
#   - Agrega una nueva fila con los datos de la factura
def add_row_csv(file_name, data):
    file_exists = os.path.isfile(file_name)

    # Abre el archivo en modo 'a' (append/agregar), crea el archivo si no existe.
    # Parámetros:
    # - "a": modo agregar (append), si el archivo no existe lo crea.
    # - newline='': evita agregar líneas vacías extras al escribir en CSV.
    with open(file_name, "a", newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Fecha", "Número", "Cliente", "Domicilio", "Ciudad", "NIF", "Subtotal", "IVA", "Total a pagar"])
        row = [
            data.get('Fecha', ''),
            data.get('Número', ''),
            data.get('Cliente', ''),
            data.get('Domicilio', ''),
            data.get('Ciudad', ''),
            data.get('NIF', ''),
            data.get('Subtotal', ''),
            data.get('IVA', ''),
            data.get('Total a pagar', '')
        ]
        writer.writerow(row)

# Función que registra errores de procesamiento en un archivo CSV
# Parámetros:
#   - file_name: nombre del archivo CSV donde guardar los errores
#   - data: diccionario con información del error (nombre factura, texto, datos GPT, error)
# Funcionalidad:
#   - Si el archivo no existe, crea los encabezados del CSV de errores
#   - Agrega una nueva fila con los detalles del error encontrado
def add_row_csv_errors(file_name, data):
    file_exists = os.path.isfile(file_name)

    # Abre el archivo en modo 'a' (append/agregar), crea el archivo si no existe.
    # Parámetros:
    # - "a": modo agregar (append), si el archivo no existe lo crea.
    # - newline='': evita agregar líneas vacías extras al escribir en CSV.
    # - encoding='utf-8': asegura que se usen caracteres UTF-8.
    with open(file_name, "a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Nombre factura", "Texto factura", "DatosGPT", "Error"])
        writer.writerow([data['Nombre factura'], data['Texto factura'], data['DatosGPT'], data['Error']])

"""
Sample data:

datos = {
    "Fecha": "20/02/2021",
    "Número": "10940",
    "Cliente": "jhael Paola Usatarez Avila", 
    "Domicilio": "C.Bolivar y 6 de octubre N° 567",
    "Ciudad": "Oruro",
    "NIF": "3540679019",
    "Subtotal": "52.00",
    "IVA": "21",
    "Total a pagar": "52.00"
    }
"""
# BLOQUE PRINCIPAL DEL PROGRAMA
# Flujo principal que procesa todas las facturas:
# 1. Convierte PDFs a imágenes
# 2. Procesa cada imagen con OCR
# 3. Extrae datos estructurados con GPT
# 4. Guarda resultados en CSV o registra errores
if __name__ == "__main__":
    # Configurar rutas de archivos y carpetas
    facturas_folder = 'facturas'  # Carpeta con archivos PDF de facturas
    output_folder = 'output_images'  # Carpeta donde se guardarán las imágenes convertidas
    db_facturas = 'facturas_new.csv'  # Archivo CSV para guardar datos exitosos
    db_errors_log = 'facturas_errors.csv'  # Archivo CSV para registrar errores

    # Paso 1: Convertir PDFs a imágenes
    convert_to_img.main(facturas_folder, output_folder)

    # Paso 2: Listar todas las imágenes generadas
    img_files = os.listdir(output_folder)
    print("Número de facturas a extraer:", len(img_files))

    # Paso 3: Procesar cada imagen de factura
    for img_file in img_files:
        img_path = os.path.join(output_folder, img_file)

        # Extraer texto de la imagen usando OCR de Azure
        clean_text, emails = cognitive_azure_ocr(img_path, computervision_client)

        # Verificar si se pudo extraer texto
        if clean_text == "":
            print("No se ha podido extraer texto de la imagen.")
        else:
            # Extraer datos estructurados usando GPT
            datos = extraer_datos_factura(clean_text)

            if datos:
                try:
                    # Convertir respuesta de GPT a JSON
                    datos_json = json.loads(datos)
                    # Guardar datos exitosos en CSV
                    add_row_csv(db_facturas, datos_json)
                except json.JSONDecodeError as e:
                    # Manejar errores de formato JSON
                    print(f"Error al decodificar JSON: {e}")
                    print(datos)
                    print("Factura que ha fallado la extracción de datos: ", img_file)
                    # Registrar error en CSV de errores
                    add_row_csv_errors(db_errors_log, {"Nombre factura": img_file, "Texto factura": clean_text, "DatosGPT": datos, "Error": str(e)})
            else:
                print("La respuesta de extraer_datos_factura está vacía.")