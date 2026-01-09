# Azure Cognitive Services para OCR (reconocimiento óptico de caracteres)
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# PIL para manipulación de imágenes
from PIL import Image

# Librerías estándar de Python
import time  # Para manejo de tiempo (no usado actualmente)
import re   # Para expresiones regulares (no usado actualmente)
import os   # Para operaciones del sistema de archivos
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

def validate_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
            print("La imagen es válida.")
            return True
    except Exception as e:
        print(f"El archivo no es una imagen válida: {e}")
        return False

print("Endpoint:", endpoint)
print("Key cargada:", key[:5], "...")

def congnitive_azure_ocr(roi_name, computervision_client):
    """
    Ejecuta OCR sobre una imagen usando Azure Computer Vision (Read API)
    y devuelve el texto extraído como string.
    """

    try:
        if not os.path.exists(roi_name):
            raise FileNotFoundError(f"No existe el archivo: {roi_name}")

        if not validate_image(roi_name):
            raise ValueError("El archivo no es una imagen válida")

        # Abrir imagen en modo binario
        with open(roi_name, "rb") as image_stream:
            read_response = computervision_client.read_in_stream(
                image=image_stream,
                raw=True
            )

        # Obtener el ID de la operación
        operation_location = read_response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        # Esperar a que Azure termine el OCR
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ["notStarted", "running"]:
                break
            time.sleep(1)

        # Verificar resultado
        if read_result.status == OperationStatusCodes.succeeded:
            extracted_text = []

            for page in read_result.analyze_result.read_results:
                for line in page.lines:
                    extracted_text.append(line.text)

            return "\n".join(extracted_text)

        else:
            print("OCR falló. Estado:", read_result.status)
            return ""

    except Exception as e:
        print("ERROR OCR COGNITIVE AZURE:", e)
        return ""

texto = congnitive_azure_ocr("path/factura_edesur.jpeg", computervision_client)

print("Texto detectado:")
print(texto)
