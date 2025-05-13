mport requests
from datetime import datetime, timedelta

# Configura los datos
TOKEN = "2ae5923f7cafb2edb1eedd917ebb30d5"  # Usaaca el token dado por el profe o el que nos envien por email
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Token {TOKEN}",
    "User-Agent": "Mozilla/5.0"
}

# Indicadores que quieres consultar
indicadores = {
    "Previsión eólica": 541,
    "Generación real eólica": 551
}

# Fechas (últimas 24 horas)
hoy = datetime.utcnow()
ayer = hoy - timedelta(days=1)

start_date = ayer.strftime("%Y-%m-%dT00:00:00Z")
end_date = hoy.strftime("%Y-%m-%dT00:00:00Z")

# Función para obtener datos
def obtener_datos(indicador_id):
    url = f"https://api.esios.ree.es/indicators/{indicador_id}?start_date={start_date}&end_date={end_date}&timezone=Europe/Madrid"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        valores = data['indicator']['values']
        for entrada in valores:
            print(f"{entrada['datetime']}: {entrada['value']} MW")
    else:
        print(f"Error {response.status_code}: {response.text}")

# Ejecutar
for nombre, id in indicadores.items():
    print(f"\nDatos de: {nombre}")
    obtener_datos(id)
