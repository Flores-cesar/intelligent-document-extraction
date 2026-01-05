import PyPDF2  # Para leer pdf
import re  # Para implementar expresiones regulares
import os  # Para listar y mover archivos locales

def extract_invoice_info(pdf_file_path):
    """
    FUNCIÓN PRINCIPAL: Extrae datos clave de una factura PDF usando expresiones regulares.
    
    Esta función realiza los siguientes pasos:
    1. Abre y lee el archivo PDF
    2. Extrae todo el texto del documento
    3. Busca patrones específicos usando expresiones regulares
    4. Procesa y calcula valores financieros
    5. Retorna toda la información estructurada
    
    Parámetros:
    - pdf_file_path: Ruta del archivo PDF a procesar
    
    Retorna:
    - Tupla con: número de factura, cliente, subtotal, total, descuento, impuesto, notas y términos
    """
    
    # Abre el archivo PDF en modo lectura binaria
    #rb= r:read; b: binary, Indica a Python que lea en crudo, sin convertirlo a strings.
    with open(pdf_file_path, 'rb') as file:
        # MÉTODO: Crear un lector PDF usando PyPDF2.PdfReader
        # El objeto PdfReader permite acceder a las páginas y contenido del PDF
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Variable para acumular todo el texto del PDF
        text = ''

        # Recorre todas las páginas del PDF
        for page_num in range(len(pdf_reader.page)):
            # MÉTODO: Accede a cada página individualmente
            page = pdf_reader.pages[page_num]
            # MÉTODO: Extrae el texto de la página actual
            text += page.extract_text()
        
        # Imprime el texto extraído para depuración
        print(text)

        # PATRONES DE EXPRESIONES REGULARES:
        # Cada patrón busca información específica en el texto del PDF
        
        # Busca el número de factura después de "INVOICE #"
        invoice_number_pattern = r'INVOICE\s*#\s*(\d+)'
        
        # Busca la información del cliente después de "Bill To:"
        bill_to_pattern = r'Bill\s*To\s*:\s*(.*)'
        
        # Busca los ítems de la factura: descripción, cantidad, precio unitario, total
        items_pattern = r'(.*?)\s*(\d+)\s*(\d+)\s*(€\d+\.\d{2})'
        
        # Busca las notas y términos de la factura
        notes_terms_pattern = r'Notes\s*:\s*(.*?)\s*Terms\s*:\s*(.*)'
        
        # Busca los porcentajes de descuento e impuesto
        discount_tax_pattern = r'Discount\s*\((\d+)%\)\s*\|\s*Tax\s*\((\d+)%\)'

        # APLICACIÓN DE EXPRESIONES REGULARES:

        # MÉTODO re.search(): Busca la primera coincidencia del patrón en el texto
        invoice_number_match = re.search(invoice_number_pattern, text)
        bill_to_match = re.search(bill_to_pattern, text)
        notes_terms_match = re.search(notes_terms_pattern, text)
        match = re.search(discount_tax_pattern, text)
        
        # MÉTODO re.findall(): Busca TODAS las coincidencias del patrón en el texto
        items_matches = re.findall(items_pattern, text)

        # NORMALIZACIÓN DE DATOS:
        # Convierte las coincidencias en valores utilizables
        
        # MÉTODO group(): Extrae grupos capturados por los paréntesis en la regex
        # group(1) obtiene el primer grupo, group(2) el segundo, etc.
        invoice_number = invoice_number_match.group(1) if invoice_number_match else None
        bill_to = bill_to_match.group(1) if bill_to_match else None
        
        # Para notas y términos, se extraen ambos grupos
        if notes_terms_match:
            notes, terms = notes_terms_match.groups()  # MÉTODO groups(): retorna todos los grupos
        else:
            notes, terms = (None, None)
        
        # Extrae porcentajes de descuento e impuesto
        discount_percentage = match.group(1) if match else None
        tax_percentage = match.group(2) if match else None

        # Variables para cálculos
        i = 0
        subtotal = 0
        total = 0

        # CÁLCULO DEL SUBTOTAL:
        # Suma los montos de todos los ítems (excluyendo el último si es el total)
        for item in items_matches:
            if len(items_matches) - 1 != i:
                # item[3] contiene el precio total del ítem (ej: "€100.00")
                # Se elimina el símbolo de euro y se convierte a float
                subtotal = subtotal + float(item[3].replace('€', ''))
            i = i + 1

        # CÁLCULOS FINANCIEROS:
        # Aplica descuento y luego impuesto al subtotal
        if discount_percentage:
            total_discount = subtotal - (subtotal * int(discount_percentage) / 100)
        else:
            total_discount = subtotal
        
        if tax_percentage:
            total = total_discount + (total_discount * int(tax_percentage) / 100)
        else:
            total = total_discount

        # Retorna todos los datos extraídos y calculados
        return invoice_number, bill_to, subtotal, total, discount_percentage, tax_percentage, notes, terms

def get_files_in_folder(folder_path):
    """
    FUNCIÓN: Obtiene lista de archivos en una carpeta y sus subcarpetas.
    
    Parámetros:
    - folder_path: Ruta de la carpeta a explorar
    
    Retorna:
    - Lista con las rutas completas de todos los archivos encontrados
    """
    files = []
    
    # MÉTODO os.walk(): Recorre recursivamente directorios y subdirectorios
    # Retorna: directorio actual, subdirectorios, y archivos en cada nivel
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            # MÉTODO os.path.join(): Une rutas de forma segura entre sistemas operativos
            files.append(os.path.join(root, filename))
    return files

if __name__ == "__main__":
    """
    BLOQUE PRINCIPAL DEL PROGRAMA:
    - Procesa todos los archivos PDF en la carpeta 'documents'
    - Extrae información de cada factura
    - Mueve los archivos procesados a 'processed_documents'
    """
    
    # Ruta de la carpeta con documentos a procesar
    folder_path = 'documents'
    
    # Obtiene lista de archivos
    files = get_files_in_folder(folder_path)

    # Procesa cada archivo encontrado
    for file in files:
        print("File:", file)

        # Llama a la función principal para extraer información
        invoice_number, bill_to, subtotal, total, discount, tax, notes, terms = extract_invoice_info(file)

        # Muestra la información extraída
        print("Invoice Number:", invoice_number)
        print("Bill To:", bill_to)
        print("Subtotal:", subtotal)
        print("Tax (%):", tax)
        print("Discount (%):", discount)
        print("Total:", total)
        print("Notes:", notes)
        print("Terms:", terms)

        # PROCESAMIENTO DE ARCHIVOS:
        # Mueve el archivo procesado a una carpeta diferente
        
        # Carpeta destino para archivos procesados
        processed_folder = 'processed_documents'
        
        # MÉTODO os.makedirs(): Crea directorios si no existen
        # exist_ok=True evita error si la carpeta ya existe
        os.makedirs(processed_folder, exist_ok=True)
        
        # Construye la nueva ruta para el archivo
        # MÉTODO os.path.basename(): Extrae solo el nombre del archivo de una ruta completa
        new_file_path = os.path.join(processed_folder, os.path.basename(file))
        
        # MÉTODO os.rename(): Mueve el archivo a la nueva ubicación
        os.rename(file, new_file_path)