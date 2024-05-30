import requests
import re
import zipfile
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def delete_existing_files_and_directories(source_directory, destination_directory):
    # Delete all files in the source directory
    if os.path.exists(source_directory):
        for file in os.listdir(source_directory):
            file_path = os.path.join(source_directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    for root, dirs, files in os.walk(file_path, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')    
    # Delete all files and directories in the destination directory
    if os.path.exists(destination_directory):
        for file in os.listdir(destination_directory):
            file_path = os.path.join(destination_directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    for root, dirs, files in os.walk(file_path, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def download_last_n_months_files(m1, y1, n):
    dates = []
    downloaded_files = []
    for i in range(n):
        date = datetime(year=y1, month=m1, day=1) - timedelta(days=30 * i)
        dates.append(date.strftime('%Y%m'))

    url_base = "https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Intraday%20Auction%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demnand%20curves%20of%20intraday%20auction%20market%20including%20bid%20units&realdir=curva_pibc_uof"

    response = requests.get(url_base)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        file_names = [re.search(r'curva_pibc_uof_\d{6}.zip', link['href']).group(0) for link in links if re.search(r'curva_pibc_uof_\d{6}.zip', link['href'])]

        if file_names:
            files_to_download = [file for file in file_names if any(date in file for date in dates)]

            if not files_to_download:
                print("No files found for the specified last n months.")
                return

            for file in files_to_download:
                latest_file_url = f"https://www.omie.es/en/file-download?parents%5B0%5D=curva_pibc_uof&filename={file}"
                file_name = f"data/{file}"

                response = requests.get(latest_file_url)

                if response.status_code == 200:
                    os.makedirs(os.path.dirname(file_name), exist_ok=True)
                    with open(file_name, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Download complete: {file_name}")
                    downloaded_files.append(file_name)
                else:
                    print(f"Error downloading the file: {response.status_code}")
        else:
            print("No files matching the specified pattern were found.")
    else:
        print(f"Error requesting the page: {response.status_code}")

    return downloaded_files

def zip_file_extraction(source_directory, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    zip_files = [file for file in os.listdir(source_directory) if file.endswith('.zip')]

    for file in zip_files:
        file_path = os.path.join(source_directory, file)
        subdirectory = os.path.join(destination_directory, file[:-4])
        os.makedirs(subdirectory, exist_ok=True)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(subdirectory)

def rename_and_delete_files_in_subfolders(destination_directory):
    for subdir, _, files in os.walk(destination_directory):
        for file in files:
            if file.endswith('.1'):
                source_path = os.path.join(subdir, file)
                dest_path = os.path.join(subdir, file[:-2] + '.csv')
                if not os.path.exists(dest_path):
                    os.rename(source_path, dest_path)
                else:
                    os.remove(source_path)

def data_extraction(m1, y1, n):
    source_directory = 'data/'
    destination_directory = 'extracted/'
    
    # Delete existing files and directories
    delete_existing_files_and_directories(source_directory, destination_directory)
    
    # Download the new files
    downloaded_files = download_last_n_months_files(m1, y1, n)
    
    # Extract the ZIP files
    zip_file_extraction(source_directory, destination_directory)
    
    # Rename and delete .1 files in subfolders
    rename_and_delete_files_in_subfolders(destination_directory)

    return downloaded_files