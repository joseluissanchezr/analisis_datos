# === PARTE 1 ─ Configuración e importaciones básicas ===
# DATA ANALYSIS PROJECT · GROUP 2
# Descripción: extracción y limpieza de datos horarios de la API de ESIOS
# Indicadores: 541 (previsión) y 551 (producción real)

import requests
import pandas as pd
from datetime import datetime, timedelta

TOKEN = '255c4529289ed8e7cfcfdc5cff2c43d0f101fe5b3adaa20273c01b0deafa80d4'            
HEADERS = {
    'Accept'      : 'application/json',
    'Content-Type': 'application/json',
    'x-api-key'   : TOKEN,
    'User-Agent'  : 'esios-api-client'
}
