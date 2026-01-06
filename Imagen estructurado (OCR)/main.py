from PIL import Image, ImageEnhance, ImageFilter  # PIL para manipular imágenes
import pytesseract  # Librería OCR
import re  # Expresiones regulares para extraer datos
import cv2  # OpenCV para procesamiento de imágenes
import numpy as np  # Numpy para manejo numérico (no se usa explícito aquí)
import os  # Para interacción con el sistema operativo

# Configura la ruta ejecutable de Tesseract para OCR
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Función para mejorar la calidad de la imagen antes del OCR
def preprocesar_imagen(ruta_imagen):
    """Mejora la imagen para mejor reconocimiento OCR"""
    # Lee la imagen con OpenCV desde la ruta
    img = cv2.imread(ruta_imagen)
    
    # Verifica si la imagen se cargó correctamente
    if img is None:
        # Si no se pudo cargar, lanza un error
        raise FileNotFoundError(f"No se pudo cargar la imagen: {ruta_imagen}")
    
    # Convierte la imagen a escala de grises para simplificar el procesamiento
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aumenta el tamaño al doble para mejorar la precisión del OCR
    escala = 2
    ancho = int(gris.shape[1] * escala)
    alto = int(gris.shape[0] * escala)
    gris = cv2.resize(gris, (ancho, alto), interpolation=cv2.INTER_CUBIC)
    
    # Aplica umbralización adaptativa para resaltar los caracteres
    umbral = cv2.adaptiveThreshold(
        gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Reduce el ruido de la imagen processed (mejora OCR)
    denoised = cv2.fastNlMeansDenoising(umbral, None, 10, 7, 21)
    
    # imwrite: escribir imagen en disco duro, toma los datos que están en la memoria RAM (dentro de la variable denoised) 
    # los guarda físicamente en tu disco duro como un archivo de imagen real.
    # denoised es una matriz numerica, con esto OpenCV (cv2) procesa mucho mas rapido que procesar "objetos de imagen".
    cv2.imwrite("imagen_procesada.png", denoised)
    
    # Convierte el array de Numpy a objeto PIL y lo retorna
    # Los empaqueta en un formato de "Imagen" que otras librerías (como Tesseract para OCR) entienden mejor.
    return Image.fromarray(denoised)

# ==== COMIENZA EL FLUJO DE EXTRACCIÓN DE DATOS ====

# Muestra mensaje de inicio
print("Procesando imagen...")
# Muestra el directorio actual para referencia
print(f"Directorio actual: {os.getcwd()}")

# Verifica que el archivo de imagen de entrada exista en el directorio de trabajo
if not os.path.exists("captura.png"):
    # Si no encuentra la imagen, muestra mensaje de error
    print("ERROR: No se encuentra 'captura.png' en el directorio actual")
    # Muestra archivos de imagen disponibles para ayuda
    print("Archivos en el directorio:")
    print([f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.jpeg'))])
    # Termina la ejecución por error
    exit(1)

# Procesa la imagen para mejorarla de cara al OCR
img_procesada = preprocesar_imagen("captura.png")

# Prepara la configuración personalizada para Tesseract (OCR Engine Mode y Page Segmentation Mode)
custom_config = r'--oem 3 --psm 6'

# Intenta reconocimiento primero en español; si da error, prueba inglés
print("Intentando extraer texto…")
try:
    # Intenta identificar texto en español
    text = pytesseract.image_to_string(img_procesada, lang='spa', config=custom_config)
    print("✓ Usando idioma: Español")
except pytesseract.TesseractError:
    # Si hay error de idioma, usa inglés
    print("⚠ Idioma español no disponible, usando inglés")
    text = pytesseract.image_to_string(img_procesada, lang='eng', config=custom_config)

# Muestra el texto detectado por OCR
print("=== TEXTO EXTRAÍDO ===")
print(text)
# Linea divisoria en consola
print("\n" + "="*50 + "\n")

# Define patrones flexibles para buscar campos específicos (maneja errores OCR)
patterns = {
    # Busca fechas (soporta variaciones y caracteres confusos por OCR)
    "fecha": [
        r"F[ea]ch?a[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",  # Fecha tipo 01/12/2022 o similares
        r"(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})"  # Alternativa simple: 02/03/2022
    ],
    # Número de factura
    "numero": [
        r"N[uú]mero[:\s]+(\d+)",
        r"Numero[:\s]+(\d+)"  # Considera también sin tilde
    ],
    # Nombre del cliente
    "cliente": [
        r"Cliente[:\s]+([^\n]+?)(?=\n|Domicilio)",
        r"Cliente[:\s]+(.+?)(?=\n)"
    ],
    # Domicilio
    "domicilio": [
        r"Domicilio[:\s]+([^\n]+?)(?=\n|Ciudad)",
        r"Dom[ie]cilio[:\s]+(.+?)(?=\n)"  # Soporta posibles errores de OCR en la palabra
    ],
    # Ciudad del cliente
    "ciudad": [
        r"Ciudad[:\s]+([^\n]+?)(?=\n|DNI|NIF)",
        r"Ciudad[:\s]+(.+?)(?=\n)"
    ],
    # NIF o documento
    "nif": [
        r"DNI[/\s]?NIF[:\s]+([A-Z0-9]+)",
        r"IE\s+([A-Z0-9]{7,})"
    ],
    # Concepto de la factura
    "concepto": [
        r"Publicidad[^\n]+(?:\n|$)"  # Busca cualquier línea que comience con 'Publicidad'
    ],
    # Subtotal
    "subtotal": [
        r"SUBTOTAL[:\s]+([\d.,]+)",
        r"(?:SUBTOTAL|Subtotal)[:\s]*([\d\s.,]+?)(?=\n|IVA)"
    ],
    # IVA
    "iva": [
        r"IVA[^0-9]+([\d.,]+)",
        r"(?:IVA|iva)[^\d]+([\d\s.,]+?)(?=\n)"
    ],
    # Total a pagar
    "total_a_pagar": [
        r"TOTAL\s*A?\s*PAGAR[:\s]+([\d.,]+)",
        r"TOTAL[:\s]+([\d.,]+)"
    ]
}

# Función para buscar el valor de un campo usando patrones
# campo: el nombre del campo que se busca (por claridad, pero no se usa en el match directo)
# lista_patrones: patrones predefinidos para cada campo
# texto: texto sobre el cual buscar

def extraer_valor(campo, lista_patrones, texto):
    """Intenta múltiples patrones hasta encontrar uno que funcione"""
    for patron in lista_patrones:
        # Busca usando el patrón con flags para ignorar mayúsculas/minúsculas y saltos de línea
        match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
        if match:
            valor = match.group(1).strip()  # Extrae y limpia el valor
            # Elimina espacios y caracteres erróneos extra
            valor = re.sub(r'\s+', ' ', valor)
            return valor
    # Si no encuentra, retorna "No encontrado"
    return "No encontrado"

# Diccionario para guardar los resultados extraídos
resultados = {}

# Itera sobre los patrones y extrae valores del texto detectado
for campo, lista_patrones in patterns.items():
    resultados[campo] = extraer_valor(campo, lista_patrones, text)

# Muestra en consola los resultados extraídos de la factura
print("=== DATOS EXTRAÍDOS ===")
for campo, valor in resultados.items():
    print(f"{campo.upper()}: {valor}")

# Guarda los resultados en un archivo de texto plano
with open("factura_extraida.txt", "w", encoding="utf-8") as f:
    f.write("DATOS EXTRAÍDOS DE LA FACTURA\n")
    f.write("="*50 + "\n\n")
    for campo, valor in resultados.items():
        f.write(f"{campo.upper()}: {valor}\n")

# Notificaciones en consola de los archivos generados
print("\n✓ Resultados guardados en 'factura_extraida.txt'")
print("✓ Imagen procesada guardada en 'imagen_procesada.png'")
