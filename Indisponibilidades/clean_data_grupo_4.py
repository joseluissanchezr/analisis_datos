import os
import pandas as pd

DATA_FOLDER = "../data"  # Carpeta donde se han guardado los datos extraidos del primer archivo "extract_data_grupo_4.py"

# Estat función limpia los datos del archivo de la siguiente forma:
def clean_file(file_path):

    # Carga el archivo en un DataFrame de pandas
    df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
    
    # Elimina filas con valores NaN
    df.dropna(inplace=True)
    
    # Elimina duplicados
    df.drop_duplicates(inplace=True)
    
    # Identifica y elimina los valores atípicosusando el rango intercuartil (IQR)
    Q1 = df.quantile(0.25) # Calcula el primer cuartil
    Q3 = df.quantile(0.75) #Calucla el tercer cuartil
    IQR = Q3 - Q1 #Ranfo de datos entre el primer y el tercer curtil.
    lower_bound = Q1 - 1.5 * IQR  #Identifica valores atípicos por debajo de este límite que he marcado
    upper_bound = Q3 + 1.5 * IQR ##Identifica valores atípicos por encima de este límite que he marcado

    # Filtra el DataFrame para eliminar cualquier fila que contenga valores atípicos comparando con el límite inferior y superior.
    df = df[~((df < lower_bound) | (df > upper_bound)).any(axis=1)]
    
    # Guarda el DataFrame limpio en un nuevo archivo
    cleaned_file_path = file_path.replace(".csv", "_cleaned.csv")
    df.to_csv(cleaned_file_path, index=False, sep=';', encoding='utf-8')
    print(f"Limpió {file_path}, guardado como {cleaned_file_path}")
    
#Funcion que limpia todo los archivos del directorio con la función definida antes (clean_file)

def clean_data_folder():
    """
    Limpia todos los archivos CSV en la carpeta DATA_FOLDER.
    """
    for file_name in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".csv"):  # Ajusta según la extensión de tus archivos
            clean_file(file_path)
    print("Datos limpiados!")
