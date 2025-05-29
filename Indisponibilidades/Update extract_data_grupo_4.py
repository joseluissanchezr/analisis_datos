import os
import zipfile
import requests
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd

URL = "https://www.omie.es/es/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Mercado%20Diario&parents%5B2%5D=7.%20Indisponibilidades&dir=Declaraci%C3%B3n%20de%20indisponibilidades%20de%20unidades%20espa%C3%B1olas&realdir=indisp"
DATA_FOLDER = "../data"  # Carpeta para guardar los datos

# Función para obtener el contenido de la URL
def get_content(url):
    try:
        response = requests.get(url, verify=False)  # Obtener el contenido de la URL
        response.raise_for_status()  # Verificar si hay errores en la solicitud
        html_content = response.text  # Obtener el contenido HTML
        return BeautifulSoup(html_content, 'html.parser')  # Analizar el HTML con BeautifulSoup
    except requests.RequestException as e:
        print(f"Error al obtener el contenido de la URL: {e}")
        return None

# Función para descargar un archivo
def download_file(file_url, file_name):
    try:
        filename = os.path.join(DATA_FOLDER, file_name)  # Ruta completa del archivo
        urllib.request.urlretrieve(file_url, filename)  # Descargar el archivo
        print(f"Downloaded {file_name}")

        if file_name.endswith(".zip"):  # Verificar si el archivo es un ZIP
            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(DATA_FOLDER)  # Extraer el contenido del ZIP
            print(f"Extracted contents of {file_name}")
            os.remove(filename)  # Eliminar el archivo ZIP

    except Exception as e:
        print(f"Error al descargar o extraer el archivo: {e}")

# Obtener y analizar el contenido de la URL
html_soup = get_content(URL)
if html_soup:
    links = html_soup.find_all("td")  # Encontrar todas las etiquetas <td>

    # Buscar el enlace al archivo ZIP del último mes
    last_month_zip_link = None
    for link in links:
        href_tag = link.find("a")
        if href_tag:
            href = href_tag.get("href", "")
            if "indisp_" in href:
                last_month_zip_link = "https://www.omie.es" + href
                break

    # Descargar el archivo ZIP del último mes y extraer los archivos relevantes
    if last_month_zip_link:
        print(f"Downloading and extracting {last_month_zip_link}")
        download_file(last_month_zip_link, "last_month.zip")
    else:
        print("No se encontró el enlace al archivo ZIP del último mes.")
else:
    print("No se pudo obtener el contenido de la URL.")

# Leer archivos descargados con pandas
dataframes = []  # Lista para almacenar DataFrames

for file_name in os.listdir(DATA_FOLDER):
    if file_name.endswith(".xls") or file_name.endswith(".xlsx"):
        file_path = os.path.join(DATA_FOLDER, file_name)
        df = pd.read_excel(file_path)
        print(f"Contenido de {file_name}:")
        print(df.head())
        dataframes.append(df)  # Agregar el DataFrame a la lista
