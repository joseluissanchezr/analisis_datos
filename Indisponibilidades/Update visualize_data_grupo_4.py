import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def read_file(file_path):
    with open(file_path) as file:
        return file.read()

def analyze_files(file_paths):
    occurrence_count = {}

    for file_path in file_paths:
        data = read_file(file_path)
        for line in data.split("\n"):
            line = line.split(";")
            if len(line) > 15 and line[15]:
                key = line[15].lower().strip()
                occurrence_count[key] = occurrence_count.get(key, 0) + 1

    # Convertir el diccionario en un dataframe de pandas
    df = pd.DataFrame(list(occurrence_count.items()), columns=['Values', 'Number of occurrences'])

    # Ordenar el dataframe por el número de ocurrencias y seleccionar las top_n filas
    df = df.sort_values(by='Number of occurrences', ascending=False).head(20)

    return df

# Gráfico de barras horizontal para mostrar las 20 indisponibilidades más frecuentes
def visualize_data_bar(filtered_data):
    plt.figure(figsize=(10, 8))
    sns.barplot(x='Number of occurrences', y='Values', data=filtered_data, palette='viridis')
    plt.xlabel("Number of occurrences")
    plt.ylabel("Values")
    plt.title("Top 20 Occurrences of values in the data (Bar Chart)")
    plt.tight_layout()
    plt.show()

# Gráfico de línea para mostrar la tendencia de las indisponibilidades por orden de frecuencia
def visualize_data_line(filtered_data):
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_data['Values'], filtered_data['Number of occurrences'], marker='o', linestyle='-', color='b')
    plt.xlabel("Values")
    plt.ylabel("Number of occurrences")
    plt.title("Top 20 Occurrences of values in the data (Line Chart)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Gráfico de pastel para mostrar la distribución porcentual de los diferentes tipos de eventos.
def visualize_data_pie(filtered_data):
    plt.figure(figsize=(8, 8))
    plt.pie(filtered_data['Number of occurrences'], labels=filtered_data['Values'], autopct='%1.1f%%', startangle=140)
    plt.title("Top 20 Occurrences of values in the data (Pie Chart)")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Directorio donde se encuentran los archivos de indisponibilidades (en ../data)
directory = "../data"
file_paths = [os.path.join(directory, file) for file in os.listdir(directory)]

# Analizar los archivos y visualizar los datos
filtered_data = analyze_files(file_paths)

# Visualizaciones utilizando funciones definidas
visualize_data_bar(filtered_data)
visualize_data_line(filtered_data)
visualize_data_pie(filtered_data)
