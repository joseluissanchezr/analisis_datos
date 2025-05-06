import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Función para procesar un archivo descargado
def process_file(link, folder_name):
    # Descargar el archivo desde el enlace
    zip_file_name = link.split('/')[-1].split("=")[-1]
    zip_file_path = os.path.join(folder_name, zip_file_name)
    response = requests.get(link)
    if response.status_code == 200:
        with open(zip_file_path, 'wb') as file:
            file.write(response.content)
    # Extraer los archivos del archivo ZIP
    extracted_folder = os.path.splitext(zip_file_path)[0]
    os.makedirs(extracted_folder, exist_ok=True)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder)
    # Procesar los archivos extraídos
    extracted_files = os.listdir(extracted_folder)
    for file_name in extracted_files:
        new_file_name = os.path.splitext(file_name)[0] + ".csv"
        original_file_path = os.path.join(extracted_folder, file_name)
        new_file_path = os.path.join(extracted_folder, new_file_name)
        df = pd.read_csv(original_file_path, delimiter=';', encoding='latin-1', header=None, dtype=str, low_memory=False)
        df.columns = df.iloc[1]
        df = df.drop([0,1]).reset_index(drop=True)
        df = df.rename(columns={'Energía Compra/Venta': 'Energia Compra/Venta'})
        df.to_csv(new_file_path, index=False)
        os.remove(original_file_path)
    os.remove(zip_file_path)
    print(f"Los documentos del archivo {zip_file_name} ya se han descargado y procesado")

# URL de la página web
url = 'https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Day-ahead%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demand%20curves%20of%20Day-ahead%20market%20including%20bid%20units&realdir=curva_pbc_uof'
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'lxml')

# Encontrar todos los enlaces que contienen "file-download?parents%5B0%5D"
all_links = soup.find_all('a', href=lambda href: href and "file-download?parents%5B0%5D" in href)
# Añadir «https://www.omie.es» a los enlaces y almacenarlos en una lista
download_links = ["https://www.omie.es" + link.get('href') for link in all_links]

# Crear una carpeta para guardar los archivos descargados en el escritorio
desktop_path = str(Path.home() / "Desktop")
folder_name = os.path.join(desktop_path, "downloaded_files")
os.makedirs(folder_name, exist_ok=True)

# Utilizar ThreadPoolExecutor para descargar y procesar los archivos en paralelo
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for link in download_links[0:5]:
        futures.append(executor.submit(process_file, link, folder_name))
    for future in futures:
        future.result()
