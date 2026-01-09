import os
import fitz # PyMuPDF

def pdf_to_images(pdf_path, output_folder):
    """
    Convierte un archivo PDF en imágenes PNG, una por cada página.

    Parámetros:
    pdf_path (str): Ruta completa al archivo PDF de entrada
    output_folder (str): Directorio donde se guardarán las imágenes

    Funcionalidad:
    - Abre el PDF usando PyMuPDF (fitz)
    - Extrae cada página como imagen
    - Guarda cada página como archivo PNG separado
    """
    # El PDF está abierto, pero las páginas individuales están en disco
    pdf_document = fitz.open(pdf_path)

    # Extrae el nombre del archivo sin extensión para usar como prefijo
    # os.path.basename() obtiene solo el nombre del archivo de la ruta completa
    # os.path.splitext() separa nombre y extensión, [0] toma solo el nombre
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Verifica si el directorio de salida existe, si no, lo crea
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Itera sobre cada página del PDF
    for page_num in range(len(pdf_document)):
        # Carga la página específica del PDF ram, para manipularlo se crea objeto asociado page
        page = pdf_document.load_page(page_num) # Objeto page contiene puntero a datos en RAM

        # Convierte la página a un mapa de píxeles (imagen)
        pix = page.get_pixmap()

        # Construye la ruta completa para el archivo de salida
        # Formato: nombre_archivo_page_N.png
        output_path = os.path.join(output_folder, f'{file_name}_page_{page_num + 1}.png')

        # Guarda la imagen como archivo PNG
        pix.save(output_path)

        # Línea comentada para debug: mostrar archivos guardados
        #print(f'saved: {output_path}')

def main(input_folder, output_folder):
    """
    Función principal que procesa todos los PDFs en una carpeta de entrada.

    Parámetros:
    input_folder (str): Directorio que contiene los archivos PDF a procesar
    output_folder (str): Directorio donde se guardarán todas las imágenes generadas

    Funcionalidad:
    - Lista todos los archivos en la carpeta de entrada
    - Para cada archivo PDF encontrado, llama a pdf_to_images()
    """
    # Obtiene la lista de todos los archivos en el directorio de entrada
    pdf_files = os.listdir(input_folder)

    # Itera sobre cada archivo encontrado
    for pdf_file in pdf_files:
        # Construye la ruta completa al archivo PDF
        pdf_path = os.path.join(input_folder, pdf_file)

        # Llama a la función que convierte el PDF a imágenes
        pdf_to_images(pdf_path, output_folder)