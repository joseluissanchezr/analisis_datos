import matplotlib.pyplot as plt 
import pandas as pd

def aggregated_curve(file_path, hour, day, number):

    df = pd.read_csv(file_path, sep=";", encoding="latin1")
    df_hora = df[df['Hora'] == hour]

    # Filtrer les données pour séparer les types d'offres de vente (V) et d'achat (C)
    offre = df_hora[df_hora['Tipo Oferta'] == 'V']
    demande = df_hora[df_hora['Tipo Oferta'] == 'C']

    # Agréger les données par quantité cumulée et calculer le prix moyen pour chaque quantité cumulée
    offre_aggregated = offre.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()
    demande_aggregated = demande.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()

    # Trier les données pour que l'offre soit croissante et la demande décroissante
    offre_aggregated = offre_aggregated.sort_values(by='Precio Compra/Venta')
    demande_aggregated = demande_aggregated.sort_values(by='Precio Compra/Venta', ascending=False)

    # Calculer la quantité cumulée pour l'offre et la demande
    offre_aggregated['Quantité Cumulée'] = offre_aggregated['Energía Compra/Venta'].cumsum()
    demande_aggregated['Quantité Cumulée'] = demande_aggregated['Energía Compra/Venta'].cumsum()

    # Tracer les courbes d'offre et de demande
    plt.figure(figsize=(12, 8))

    plt.plot(offre_aggregated['Quantité Cumulée'], offre_aggregated['Precio Compra/Venta'], label='Offre (V)', color='blue', marker='o')
    plt.plot(demande_aggregated['Quantité Cumulée'], demande_aggregated['Precio Compra/Venta'], label='Demande (C)', color='red', marker='o')

    plt.title(f"Courbes d'Offre (Vente) et de Demande (Achat) pour l'heure {hour}, la date {day} et le marché intraquotidien numéro {number}")
    plt.xlabel('Quantité Cumulée (MWh)')
    plt.ylabel('Prix (€)')
    plt.legend()
    plt.grid(True)
    
    plt.savefig("app/static/aggregated_curve.png")
