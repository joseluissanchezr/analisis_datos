import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from scipy import interpolate

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



def quantity(file_path, day, number):

    df = pd.read_csv(file_path, sep=";", encoding="latin1")
    # visualisation de la quantité totale sur l'horizon d'un temps 

    # Liste pour stocker les quantités d'équilibre pour chaque heure
    equilibrium_quantities = []

    # Calculer la quantité d'équilibre pour chaque heure
    for hora in sorted(df['Hora'].unique()):
        df_hora = df[df['Hora'] == hora]

        # Filtrer les données pour séparer les types d'offres de vente (V) et d'achat (C)
        offre = df_hora[df_hora['Tipo Oferta'] == 'V']
        demande = df_hora[df_hora['Tipo Oferta'] == 'C']

        if offre.empty or demande.empty:
            continue

        # Agréger les données par quantité cumulée et calculer le prix moyen pour chaque quantité cumulée
        offre_aggregated = offre.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()
        demande_aggregated = demande.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()

        # Trier les données pour que l'offre soit croissante et la demande décroissante
        offre_aggregated = offre_aggregated.sort_values(by='Precio Compra/Venta')
        demande_aggregated = demande_aggregated.sort_values(by='Precio Compra/Venta', ascending=False)

        # Calculer la quantité cumulée pour l'offre et la demande
        offre_aggregated['Quantité Cumulée'] = offre_aggregated['Energía Compra/Venta'].cumsum()
        demande_aggregated['Quantité Cumulée'] = demande_aggregated['Energía Compra/Venta'].cumsum()

        # Créer des fonctions d'interpolation
        offre_interpol = interpolate.interp1d(offre_aggregated['Quantité Cumulée'], offre_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")
        demande_interpol = interpolate.interp1d(demande_aggregated['Quantité Cumulée'], demande_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")

        # Trouver la quantité où les prix sont égaux (approximation)
        quantities = np.linspace(max(offre_aggregated['Quantité Cumulée'].min(), demande_aggregated['Quantité Cumulée'].min()), 
                                min(offre_aggregated['Quantité Cumulée'].max(), demande_aggregated['Quantité Cumulée'].max()), 500)
        intersection_qty = quantities[np.abs(offre_interpol(quantities) - demande_interpol(quantities)).argmin()]
        
        # Stocker la quantité d'équilibre pour cette heure
        equilibrium_quantities.append((hora, intersection_qty))

        # Convertir la liste des quantités d'équilibre en DataFrame
        equilibrium_df = pd.DataFrame(equilibrium_quantities, columns=['Hora', 'Quantité d\'Équilibre'])

    # Tracer la courbe de la quantité d'équilibre en fonction des heures
    plt.figure(figsize=(12, 8))
    plt.plot(equilibrium_df['Hora'], equilibrium_df['Quantité d\'Équilibre'], marker='o', linestyle='-')
    plt.title(f"Quantité d'Équilibre en Fonction du Temps pour le jour {day}, marché numéro {number}")
    plt.xlabel('Heure')
    plt.ylabel('Quantité cumulée equilibre (MWh)')
    plt.grid(True)

    plt.savefig("app/static/quantity.png")



def price(file_path, day, number):

    #visualisation de l evolution du prix de l 'electrecité sur le temps 
    # Liste pour stocker les prix d'équilibre pour chaque heure
    equilibrium_prices = []
    df = pd.read_csv(file_path, sep=";", encoding="latin1")

    # Calculer le prix d'équilibre pour chaque heure
    for hora in sorted(df['Hora'].unique()):
            
        df = pd.read_csv(file_path, sep=";", encoding="latin1")
        df_hora = df[df['Hora'] == hora]

        # Filtrer les données pour séparer les types d'offres de vente (V) et d'achat (C)
        offre = df_hora[df_hora['Tipo Oferta'] == 'V']
        demande = df_hora[df_hora['Tipo Oferta'] == 'C']

        if offre.empty or demande.empty:
            continue

        # Agréger les données par quantité cumulée et calculer le prix moyen pour chaque quantité cumulée
        offre_aggregated = offre.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()
        demande_aggregated = demande.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()

        # Trier les données pour que l'offre soit croissante et la demande décroissante
        offre_aggregated = offre_aggregated.sort_values(by='Precio Compra/Venta')
        demande_aggregated = demande_aggregated.sort_values(by='Precio Compra/Venta', ascending=False)

        # Calculer la quantité cumulée pour l'offre et la demande
        offre_aggregated['Quantité Cumulée'] = offre_aggregated['Energía Compra/Venta'].cumsum()
        demande_aggregated['Quantité Cumulée'] = demande_aggregated['Energía Compra/Venta'].cumsum()

        # Créer des fonctions d'interpolation
        offre_interpol = interpolate.interp1d(offre_aggregated['Quantité Cumulée'], offre_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")
        demande_interpol = interpolate.interp1d(demande_aggregated['Quantité Cumulée'], demande_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")

        # Trouver la quantité où les prix sont égaux (approximation)
        quantities = np.linspace(max(offre_aggregated['Quantité Cumulée'].min(), demande_aggregated['Quantité Cumulée'].min()), 
                                min(offre_aggregated['Quantité Cumulée'].max(), demande_aggregated['Quantité Cumulée'].max()), 500)
        intersection_qty = quantities[np.abs(offre_interpol(quantities) - demande_interpol(quantities)).argmin()]
        intersection_price = offre_interpol(intersection_qty)
        
        # Stocker le prix d'équilibre pour cette heure
        equilibrium_prices.append((hora, intersection_price))

    # Convertir la liste des prix d'équilibre en DataFrame
    equilibrium_df = pd.DataFrame(equilibrium_prices, columns=['Hora', 'Prix d\'Équilibre'])

    # Tracer la courbe du prix d'équilibre en fonction des heures
    plt.figure(figsize=(12, 8))
    plt.plot(equilibrium_df['Hora'], equilibrium_df['Prix d\'Équilibre'], marker='o', linestyle='-')
    plt.title(f"Prix d'Équilibre en Fonction du Temps pour le jour {day}, marché numéro {number}")
    plt.xlabel('Heure')
    plt.ylabel('Prix d\'Équilibre (€)')
    plt.grid(True)

    plt.savefig("app/static/price.png")
