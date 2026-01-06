from docling.document_converter import DocumentConverter

# ==========================================
# 1. CONFIGURACIÓN Y CONVERSIÓN
# ==========================================

# Definimos la fuente del documento (puede ser una ruta local o una URL)
source = "sample-invoice2.pdf" 

# Inicializamos el convertidor de documentos de Docling
converter = DocumentConverter()

# Ejecutamos la conversión: esto analiza el PDF y extrae su estructura
result = converter.convert(source)

# Exportamos el resultado a un diccionario de Python, que puede contener listas.
# ejemplo:
#      (1) Diccionario    (2) Lista     (3) Diccionario
#            |                |               |
# valor = data["texts"]        [0]           ["text"]
data = result.document.export_to_dict()

# ==========================================
# 2. LÓGICA DE EXTRACCIÓN
# ==========================================

def extract_value(texts, key):
    """
    Busca una etiqueta (key) en una lista de textos y devuelve el valor que le sigue.
    
    Args:
        texts (list): Lista de diccionarios donde cada uno tiene una clave "text".
        key (str): La etiqueta que estamos buscando (ej: "Invoice Number").
        
    Returns:
        str o None: El texto del siguiente elemento si encuentra la clave, o None.
    """
    # 'enumerate' nos da el índice (i) y el objeto (item) al mismo tiempo
    for i, item in enumerate(texts):
        
        # Lógica principal:
        # 1. ¿El texto actual coincide con lo que busco (ej: "Invoice Number")?
        # 2. ¿Existe un elemento siguiente? (i + 1 < len) para evitar errores de índice.
        if item["text"] == key and i + 1 < len(texts):
            
            # Si ambas son verdad, devolvemos el texto del SIGUIENTE elemento.
            # Asume que el PDF lee: [Etiqueta] [Valor]
            return texts[i + 1]["text"]
            
    return None

# ==========================================
# 3. EXTRACCIÓN DE DATOS ESPECÍFICOS
# ==========================================

# Aquí asumimos que 'data["texts"]' contiene la lista secuencial de todo el texto del PDF.
# Llamamos a nuestra función para cada campo que nos interesa recuperar.

invoice_number = extract_value(data["texts"], "Invoice Number")
order_number   = extract_value(data["texts"], "Order Number")
invoice_date   = extract_value(data["texts"], "Invoice Date")
due_date       = extract_value(data["texts"], "Due Date")
total_due      = extract_value(data["texts"], "Total Due")

# Nota: En el código original 'from' es una palabra reservada en Python, 
# así que usamos 'from_how' o similar para evitar errores de sintaxis.
from_how       = extract_value(data["texts"], "From:")
to             = extract_value(data["texts"], "To:")

# ==========================================
# 4. MOSTRAR RESULTADOS
# ==========================================

print("Invoice Number:", invoice_number)
print("Order Number:", order_number)
print("Invoice Date:", invoice_date)
print("Due Date:", due_date)
print("Total Due:", total_due)
print("From:", from_how)
print("To:", to)
"""
ejemplo de lo que hace docling
data = {
    # "texts" es la LISTA (los corchetes [])
    "texts": [
        
        # Cada elemento de la lista es un DICCIONARIO (las llaves {})
        # Elemento 0
        {
            "text": "Invoice Number",   # <--- El texto que vemos
            "page": 1,                # <--- Info extra que la librería agrega
            "x": 100, "y": 200        # <--- Coordenadas
        },
        
        # Elemento 1 (El valor que queremos)
        {
            "text": "INV-99999",      # <--- El número de factura real
            "page": 1,
            "x": 100, "y": 220
        },

        # Elemento 2
        {
            "text": "Total Due",
            "page": 1,
            "x": 100, "y": 300
        },

        # Elemento 3 (El valor que queremos)
        {
            "text": "$ 500.00",
            "page": 1,
            "x": 150, "y": 300
        }
    ]
}

"""