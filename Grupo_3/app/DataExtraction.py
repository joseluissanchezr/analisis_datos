# Imports
import requests
import re
import zipfile
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def download_last_n_months_files(m1, y1, n):
    # Calculate the last n months
    dates = []
    for i in range(n):
        date = datetime(year=y1, month=m1, day=1) - timedelta(days=30 * i)
        dates.append(date.strftime('%Y%m'))

    # Base URL
    url_base = "https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Intraday%20Auction%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demnand%20curves%20of%20intraday%20auction%20market%20including%20bid%20units&realdir=curva_pibc_uof"

    # Make a GET request to get the page content
    response = requests.get(url_base)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links on the page that match the file name pattern
        links = soup.find_all('a', href=True)
        file_names = [re.search(r'curva_pibc_uof_\d{6}.zip', link['href']).group(0) for link in links if re.search(r'curva_pibc_uof_\d{6}.zip', link['href'])]

        if file_names:
            # Filter files for the last n months
            files_to_download = [file for file in file_names if any(date in file for date in dates)]

            if not files_to_download:
                print("No files found for the specified last n months.")
                return

            # Download each file
            for file in files_to_download:
                # Construct the full URL of the file
                latest_file_url = f"https://www.omie.es/en/file-download?parents%5B0%5D=curva_pibc_uof&filename={file}"
                # File name to save on disk
                file_name = f"data/{file}"

                # Make a GET request to download the ZIP file
                response = requests.get(latest_file_url)

                if response.status_code == 200:
                    # Save the ZIP file to the specified path
                    os.makedirs(os.path.dirname(file_name), exist_ok=True)
                    with open(file_name, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Download complete: {file_name}")
                else:
                    print(f"Error downloading the file: {response.status_code}")
        else:
            print("No files matching the specified pattern were found.")
    else:
        print(f"Error requesting the page: {response.status_code}")


def zip_file_extraction(source_directory, destination_directory):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Get the list of ZIP files in the source directory
    zip_files = [file for file in os.listdir(source_directory) if file.endswith('.zip')]

    for file in zip_files:
        file_path = os.path.join(source_directory, file)
        # Create a subdirectory for each month
        subdirectory = os.path.join(destination_directory, file[:-4])
        # Check if the file has already been extracted
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory, exist_ok=True)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(subdirectory)
            print(f"File {file_path} extracted to {subdirectory}")
        else:
            print(f"The file {file_path} has already been extracted to {subdirectory}")


def rename_and_delete_files_in_subfolders(destination_directory):
    # Iterate through subdirectories
    for subdir, _, files in os.walk(destination_directory):
        for file in files:
            if file.endswith('.1'):
                # Build source and destination paths
                source_path = os.path.join(subdir, file)
                dest_path = os.path.join(subdir, file[:-2] + '.csv')
                # Rename the file
                if not os.path.exists(dest_path):
                    os.rename(source_path, dest_path)
                else:
                    print(f"The file {dest_path} already exists and will not be renamed.")
                # Remove the .1 file if it still exists
                if os.path.exists(source_path):
                    os.remove(source_path)
                    print(f"Removed {source_path}")


def data_extraction(m1, y1, n):
    # URL of the file I want to download
    url_page = "https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Day-ahead%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demand%20curves%20of%20Day-ahead%20market%20including%20bid%20units&realdir=curva_pbc_uof"

    # Path where I want to save the file
    path = "data/webpage_omie.html"

    # GET request to try to access URL data
    response = requests.get(url_page)

    # Ensure the request succeeded
    if response.status_code == 200:
        # Write the data to a local file at the specified path
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"File saved at {path}")
    else:
        print(f"Request error code: {response.status_code}")

    # Read the HTML file
    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

        # Pattern with characters before and after
        pattern = r".*curva_pbc_uof_*."

        # Find occurrences that match the pattern
        matches = re.findall(pattern, html_content)

        if matches:
            print(len(matches), "occurrences found on the webpage.")
        else:
            print("No occurrence found.")

    download_last_n_months_files(m1, y1, n)

    # Call the function to extract ZIP files
    source_directory = 'data/'
    destination_directory = 'extracted/'
    zip_file_extraction(source_directory, destination_directory)

    # Rename and delete .1 files in subfolders
    rename_and_delete_files_in_subfolders(destination_directory)


