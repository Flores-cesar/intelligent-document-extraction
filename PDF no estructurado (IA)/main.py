import PyPDF2  # Biblioteca para leer y manipular archivos PDF
import json    # Biblioteca para trabajar con datos en formato JSON (JavaScript Object Notation)
import os      # Biblioteca para interactuar con el sistema operativo (archivos, directorios)
from openai import OpenAI  # Cliente para interactuar con la API de OpenAI (GPT)
from dotenv import load_dotenv  # Para cargar variables de entorno desde archivo .env

# Carga las variables de entorno desde el archivo .env (generalmente contiene la API key de OpenAI)
load_dotenv()

# Crea una instancia del cliente de OpenAI para hacer solicitudes a la API
client = OpenAI()

def extraer_datos_factura(texto_factura):
    """
    FUNCIÓN: Extrae datos estructurados de una factura usando inteligencia artificial (GPT-3.5).
    
    Esta función:
    1. Construye un prompt (instrucción) para GPT con el texto de la factura
    2. Envía el prompt a la API de OpenAI
    3. Recibe la respuesta en formato JSON
    4. Limpia y procesa la respuesta
    
    Parámetros:
    - texto_factura: Texto completo extraído de un PDF de factura
    
    Retorna:
    - Cadena de texto en formato JSON con los datos extraídos
    """

    # Construye el prompt (instrucción) para GPT
    prompt = f"""
    Extrae los siguientes campos del texto proporcionado y devuelve los resultados en formato JSON:
    - Date
    - Invoice number
    - Client
    - Subtotal
    - tax
    - Discount
    - Notes
    - Terms
    - Total

    Texto: 
    {texto_factura}
    """
    
    # MÉTODO: Envía la solicitud a la API de OpenAI
    # client.chat.completions.create() crea una completación (respuesta) del chat
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Modelo de IA a utilizar
        messages=[{"role": "system", "content": "Eres un experto en analisis estructurado."},
                  {"role": "user", "content": prompt}],  # Historial del chat
        max_tokens=300  # Máximo número de tokens (palabras/piezas) en la respuesta
    )

    # Obtener la respuesta y limpiar la cadena JSON
    # MÉTODO: Accede al contenido del primer mensaje de respuesta
    datos_factura_str = response.choices[0].message.content.strip()

    # MÉTODO: Elimina marcas de código (```json y ```) que GPT podría añadir
    datos_factura_str = datos_factura_str.replace('```json','').replace('```','').strip()
    
    return datos_factura_str  # Retorna el JSON como cadena de texto

def extract_invoice_info(pdf_file_path):
    """
    FUNCIÓN: Extrae información de una factura PDF, despues los extructura usando IA en lugar de regex.
    
    Esta función:
    1. Abre y lee el archivo PDF
    2. Extrae todo el texto del documento
    3. Envía el texto a GPT para extracción estructurada
    4. Convierte la respuesta JSON a un diccionario Python
    5. Extrae campos individuales del diccionario
    
    Parámetros:
    - pdf_file_path: Ruta completa al archivo PDF
    
    Retorna:
    - Tupla con 8 valores: número de factura, cliente, subtotal, total, 
      descuento, impuesto, notas y términos
    """
    
    # Abre el archivo PDF en modo lectura binaria
    with open(pdf_file_path,'rb') as file: 
        # MÉTODO: Crea un objeto lector PDF
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''  # Variable para acumular todo el texto

        # Recorre todas las páginas del PDF
        for page_num in range(len(pdf_reader.pages)):
            # MÉTODO: Accede a cada página
            page = pdf_reader.pages[page_num]
            # MÉTODO: Extrae texto de la página y lo añade al texto total
            text += page.extract_text()
        
        # Llama a la función de IA para extraer datos estructurados
        datos_factura_str = extraer_datos_factura(text)
        
        # MÉTODO json.loads(): Convierte una cadena JSON en un diccionario Python
        datos_factura = json.loads(datos_factura_str)

        # MÉTODO .get(): Obtiene valores del diccionario de forma segura
        # (retorna None si la clave no existe, en lugar de dar error)
        invoice_number = datos_factura.get('Invoice number')
        bill_to = datos_factura.get('Client')
        subtotal = datos_factura.get('Subtotal')
        total = datos_factura.get('Total')
        discount = datos_factura.get('Discount')
        tax = datos_factura.get('tax')
        notes = datos_factura.get('Notes')
        terms = datos_factura.get('Terms')

        # Retorna todos los valores como una tupla
        return invoice_number, bill_to, subtotal, total, discount, tax, notes, terms

def get_files_in_folder(folder_path):
    """
    FUNCIÓN: Obtiene lista de todos los archivos en una carpeta y sus subcarpetas.
    
    Parámetros:
    - folder_path: Ruta de la carpeta a explorar
    
    Retorna:
    - Lista con rutas completas de todos los archivos encontrados
    """
    files = []  # Lista para almacenar rutas de archivos
    
    # MÉTODO os.walk(): Recorre recursivamente la estructura de carpetas
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames: 
            # MÉTODO os.path.join(): Une rutas de forma segura
            files.append(os.path.join(root, filename))
    return files

if __name__ == '__main__':
    """
    PUNTO DE ENTRADA PRINCIPAL DEL PROGRAMA:
    - Procesa todas las facturas en la carpeta 'documents'
    - Extrae información usando IA
    - Muestra resultados en consola
    - Mueve archivos procesados a 'processed_documents'
    """
    
    # Ruta de la carpeta con documentos a procesar
    folder_path = 'documents'
    
    # Obtiene lista de todos los archivos
    files = get_files_in_folder(folder_path)

    # Procesa cada archivo uno por uno
    for file in files: 
        print('File:', file)  # Muestra qué archivo se está procesando
        
        # Llama a la función principal para extraer información
        invoice_number, bill_to, subtotal, total, discount, tax, notes, terms = extract_invoice_info(file)

        # Muestra la información extraída
        print("Invoice Number:", invoice_number)
        print("Bill To:", bill_to)
        print("Subtotal:", subtotal)
        print("Total:", total)
        print("Discount:", discount)
        print("Tax:", tax)
        print("Notes:", notes)
        print("Terms:", terms)

        # PROCESAMIENTO POST-EXTRACCIÓN:
        # Mueve el archivo ya procesado a otra carpeta
        
        processed_folder = 'processed_documents'  # Carpeta destino
        
        # MÉTODO os.makedirs(): Crea la carpeta si no existe
        # exist_ok=True evita error si la carpeta ya existe
        os.makedirs(processed_folder, exist_ok=True)
        
        # Construye la nueva ruta para el archivo
        # MÉTODO os.path.basename(): Obtiene solo el nombre del archivo (sin carpetas)
        new_file_path = os.path.join(processed_folder, os.path.basename(file))
        
        # MÉTODO os.rename(): Mueve el archivo a la nueva ubicación
        os.rename(file, new_file_path)
        
        # Confirma que el archivo fue movido
        print(f"Archivo movido a: {new_file_path}\n")