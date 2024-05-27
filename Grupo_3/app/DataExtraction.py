# Imports
import requests
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import zipfile
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from io import StringIO


def download_last_n_months_files(m1, y1, n):
    # Calcular los últimos n meses
    fechas = []
    for i in range(n):
        fecha = datetime(year=y1, month=m1, day=1) - timedelta(days=30 * i)
        fechas.append(fecha.strftime('%Y%m'))

    # URL base
    url_base = "https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Intraday%20Auction%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demnand%20curves%20of%20intraday%20auction%20market%20including%20bid%20units&realdir=curva_pibc_uof"

    # Hacer una solicitud GET para obtener el contenido de la página
    response = requests.get(url_base)

    if response.status_code == 200:
        # Parsear el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar todos los enlaces en la página que coincidan con el patrón de nombre del archivo
        links = soup.find_all('a', href=True)
        file_names = [re.search(r'curva_pibc_uof_\d{6}.zip', link['href']).group(0) for link in links if re.search(r'curva_pibc_uof_\d{6}.zip', link['href'])]

        if file_names:
            # Filtrar los archivos por los últimos 3 meses
            archivos_a_descargar = [file for file in file_names if any(fecha in file for fecha in fechas)]

            if not archivos_a_descargar:
                print("No se encontraron archivos para los últimos 3 meses especificados.")
                return

            # Descargar cada archivo
            for archivo in archivos_a_descargar:
                # Construir la URL completa del archivo
                latest_file_url = f"https://www.omie.es/en/file-download?parents%5B0%5D=curva_pibc_uof&filename={archivo}"
                # Nombre del archivo a guardar en el disco
                file_name = f"data/{archivo}"

                # Hacer una solicitud GET para descargar el archivo ZIP
                response = requests.get(latest_file_url)

                if response.status_code == 200:
                    # Guardar el archivo ZIP en la ruta especificada
                    os.makedirs(os.path.dirname(file_name), exist_ok=True)
                    with open(file_name, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Descarga completa: {file_name}")
                else:
                    print(f"Error al descargar el archivo: {response.status_code}")
        else:
            print("No se encontraron archivos que coincidan con el patrón especificado.")
    else:
        print(f"Error en la solicitud a la página: {response.status_code}")



def zil_file_extraction(directorio_origen, directorio_destino):
    # Crear el directorio destino si no existe
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)

    # Obtener la lista de archivos ZIP en el directorio de origen
    archivos_zip = [archivo for archivo in os.listdir(directorio_origen) if archivo.endswith('.zip')]

    for archivo in archivos_zip:
        file_path = os.path.join(directorio_origen, archivo)
        archivo_descomprimido = os.path.join(directorio_destino, archivo[:-4])

        # Comprobar si el archivo ya ha sido descomprimido
        if not os.path.exists(archivo_descomprimido):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(directorio_destino)
            print(f"Archivo {file_path} descomprimido en {directorio_destino}")
        else:
            print(f"El archivo {file_path} ya ha sido descomprimido en {directorio_destino}")


def data_extraction(m1, y1, n):
    # URL of the file I want to download
    url_page = "https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Day-ahead%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demand%20curves%20of%20Day-ahead%20market%20including%20bid%20units&realdir=curva_pbc_uof"

    # Path where I want to save the file
    path = "data/webpage_omie.html"

    # GET request to try to access URL data
    response = requests.get(url_page)

    # I make sure the request succeeded
    if response.status_code == 200:
        # ... so I write the data in a local file, in the specified path
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"File saved at {path}")
    else:
        print(f"Request error code: {response.status_code}")

    # I read the HTML file
    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

        # Pattern with characters before and after
        pattern = r".*curva_pbc_uof_*."

        # Find occurrences that match the pattern
        matches = re.findall(pattern, html_content)

        if matches:
            print(len(matches), "occurences found on the webpage.")
        else:
            print("No occurence found.")


    download_last_n_months_files(m1, y1, n)

    # Llamada a la función para extraer archivos ZIP
    directorio_origen = 'data/'
    directorio_destino = 'descomprimido/'
    zil_file_extraction(directorio_origen, directorio_destino)

    # Obtener la lista de archivos descomprimidos
    archivos_descomprimidos = os.listdir(directorio_destino)

    # Cambiar el nombre de los archivos .1 a .csv
    for archivo in archivos_descomprimidos:
        if archivo.endswith('.1'):
            # Construir las rutas de origen y destino
            ruta_origen = os.path.join(directorio_destino, archivo)
            ruta_destino = os.path.join(directorio_destino, archivo[:-2] + '.csv')
            # Verificar si el archivo .csv ya existe
            if not os.path.exists(ruta_destino):
                # Renombrar el archivo
                os.rename(ruta_origen, ruta_destino)
                #print(f"Renombrado {ruta_origen} a {ruta_destino}")
            #else:
                #print(f"El archivo {ruta_destino} ya existe y no se renombrará.")


    # Obtener la lista de archivos CSV en el directorio
    archivos_descomprimidos = [f for f in os.listdir(directorio_destino) if f.endswith('.csv')]

