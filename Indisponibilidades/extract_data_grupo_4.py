"""
    1.4 Extraccion de las indisponibilidades del ultimo mes. “indisp2024_0X”
"""

import os  
import zipfile  
import requests  
from bs4 import BeautifulSoup  
import urllib.request  

URL = "https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Intraday%20Auction%20Market&parents%5B2%5D=7.%20Unavailability&dir=Unavailability%20declaration%20of%20spanish%20bid%20units&realdir=indisp"
DATA_FOLDER = "../data"  # Carpeta para guardar los datos


def get_content(url):
    response = requests.get(url, verify=False)  # Obtener el contenido de la URL
    html_content = response.text  # Obtener el contenido HTML
    return BeautifulSoup(html_content)  # Analizar el HTML con BeautifulSoup


def download_file(file_url, file_name):
    filename = os.path.join(DATA_FOLDER, file_name)  # Ruta completa del archivo
    urllib.request.urlretrieve(file_url, filename)  # Descargar el archivo
    print(f"Downloaded {file_name}")

    if file_name.endswith(".zip"):  # Verificar si el archivo es un ZIP
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(DATA_FOLDER)  # Extraer el contenido del ZIP
        print(f"Extracted contents of {file_name}")
        os.remove(filename)  # Eliminar el archivo ZIP


def main():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)  # Crear la carpeta si no existe

    html_soup = get_content(URL)  # Obtener y analizar el contenido de la URL
    links = html_soup.find_all("td")  # Encontrar todas las etiquetas <td>

    for link in links:
        href_tag = link.find("a")  # Encontrar la etiqueta <a> dentro de <td>
        if href_tag:
            href = href_tag["href"]  # Obtener el atributo href
            file_url = "https://www.omie.es" + href  # Construir la URL completa del archivo
            file_name = href.split("filename=")[-1]  # Obtener el nombre del archivo
            download_file(file_url, file_name)  # Descargar el archivo
            break


if __name__ == "__main__":
    main()  
