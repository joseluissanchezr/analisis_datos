import os  # Importar os para la manipulación de archivos y directorios

DATA_FOLDER = "../data"  # Carpeta para guardar los datos

def is_valid_line(line):
    """
    Verifica si una línea es válida. Puedes ajustar las condiciones según los errores que desees limpiar.
    Asumimos que una línea es válida si tiene al menos 5 columnas.
    """
    columns = line.split(";")
    return len(columns) > 5

def clean_file(file_path):
    """
    Limpia las líneas inválidas de un archivo y guarda el contenido limpio en un nuevo archivo.
    """
    cleaned_lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if is_valid_line(line):
                cleaned_lines.append(line)

    cleaned_file_path = file_path.replace(".txt", "_cleaned.txt")  # Crea un nombre de archivo para el archivo limpio
    with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
        cleaned_file.writelines(cleaned_lines)
    print(f"Limpió {file_path}, guardado como {cleaned_file_path}")

def clean_data_folder():
    """
    Limpia todos los archivos en la carpeta DATA_FOLDER.
    """
    for file_name in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".txt"):  # Ajusta según la extensión de tus archivos
            clean_file(file_path)
    print("Data cleaned !")

if __name__ == "__main__":
    clean_data_folder()
