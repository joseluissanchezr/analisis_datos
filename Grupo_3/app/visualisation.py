import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from scipy import interpolate

def aggregated_curve(file_path, hour, day, number):

    df = pd.read_csv(file_path, sep=";", encoding="latin1")
    df_hour = df[df['Hora'] == hour]

    # Filter data to separate types of sale (V) and purchase (C) offers
    offer = df_hour[df_hour['Tipo Oferta'] == 'V']
    demand = df_hour[df_hour['Tipo Oferta'] == 'C']

    # Aggregate data by cumulative quantity and calculate the average price for each cumulative quantity
    offer_aggregated = offer.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()
    demand_aggregated = demand.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()

    # Sort data so that the offer is ascending and the demand is descending
    offer_aggregated = offer_aggregated.sort_values(by='Precio Compra/Venta')
    demand_aggregated = demand_aggregated.sort_values(by='Precio Compra/Venta', ascending=False)

    # Calculate the cumulative quantity for the offer and demand
    offer_aggregated['Cumulative Quantity'] = offer_aggregated['Energía Compra/Venta'].cumsum()
    demand_aggregated['Cumulative Quantity'] = demand_aggregated['Energía Compra/Venta'].cumsum()

    # Plot the offer and demand curves
    plt.figure(figsize=(12, 8))

    plt.plot(offer_aggregated['Cumulative Quantity'], offer_aggregated['Precio Compra/Venta'], label='Offer (V)', color='blue', marker='o')
    plt.plot(demand_aggregated['Cumulative Quantity'], demand_aggregated['Precio Compra/Venta'], label='Demand (C)', color='red', marker='o')

    plt.title(f"Offer (Sale) and Demand (Purchase) Curves for hour {hour}, date {day}, and intraday market number {number}")
    plt.xlabel('Cumulative Quantity (MWh)')
    plt.ylabel('Price (€)')
    plt.legend()
    plt.grid(True)

    plt.savefig("app/static/aggregated_curve.png")

def quantity(file_path, day, number):

    df = pd.read_csv(file_path, sep=";", encoding="latin1")
    # Visualization of the total quantity over the time horizon

    # List to store equilibrium quantities for each hour
    equilibrium_quantities = []

    # Calculate the equilibrium quantity for each hour
    for hour in sorted(df['Hora'].unique()):
        df_hour = df[df['Hora'] == hour]

        # Filter data to separate types of sale (V) and purchase (C) offers
        offer = df_hour[df_hour['Tipo Oferta'] == 'V']
        demand = df_hour[df_hour['Tipo Oferta'] == 'C']

        if offer.empty or demand.empty:
            continue

        # Aggregate data by cumulative quantity and calculate the average price for each cumulative quantity
        offer_aggregated = offer.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()
        demand_aggregated = demand.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()

        # Sort data so that the offer is ascending and the demand is descending
        offer_aggregated = offer_aggregated.sort_values(by='Precio Compra/Venta')
        demand_aggregated = demand_aggregated.sort_values(by='Precio Compra/Venta', ascending=False)

        # Calculate the cumulative quantity for the offer and demand
        offer_aggregated['Cumulative Quantity'] = offer_aggregated['Energía Compra/Venta'].cumsum()
        demand_aggregated['Cumulative Quantity'] = demand_aggregated['Energía Compra/Venta'].cumsum()

        # Create interpolation functions
        offer_interpol = interpolate.interp1d(offer_aggregated['Cumulative Quantity'], offer_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")
        demand_interpol = interpolate.interp1d(demand_aggregated['Cumulative Quantity'], demand_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")

        # Find the quantity where prices are equal (approximation)
        quantities = np.linspace(max(offer_aggregated['Cumulative Quantity'].min(), demand_aggregated['Cumulative Quantity'].min()), 
                                min(offer_aggregated['Cumulative Quantity'].max(), demand_aggregated['Cumulative Quantity'].max()), 500)
        intersection_qty = quantities[np.abs(offer_interpol(quantities) - demand_interpol(quantities)).argmin()]
        
        # Store the equilibrium quantity for this hour
        equilibrium_quantities.append((hour, intersection_qty))

        # Convert the list of equilibrium quantities to a DataFrame
        equilibrium_df = pd.DataFrame(equilibrium_quantities, columns=['Hour', 'Equilibrium Quantity'])

    # Plot the equilibrium quantity over time
    plt.figure(figsize=(12, 8))
    plt.plot(equilibrium_df['Hour'], equilibrium_df['Equilibrium Quantity'], marker='o', linestyle='-')
    plt.title(f"Equilibrium Quantity Over Time for day {day}, market number {number}")
    plt.xlabel('Hour')
    plt.ylabel('Cumulative Equilibrium Quantity (MWh)')
    plt.grid(True)

    plt.savefig("app/static/quantity.png")

def price(file_path, day, number):

    # Visualization of the evolution of electricity prices over time
    # List to store equilibrium prices for each hour
    equilibrium_prices = []
    df = pd.read_csv(file_path, sep=";", encoding="latin1")

    # Calculate the equilibrium price for each hour
    for hour in sorted(df['Hora'].unique()):
            
        df = pd.read_csv(file_path, sep=";", encoding="latin1")
        df_hour = df[df['Hora'] == hour]

        # Filter data to separate types of sale (V) and purchase (C) offers
        offer = df_hour[df_hour['Tipo Oferta'] == 'V']
        demand = df_hour[df_hour['Tipo Oferta'] == 'C']

        if offer.empty or demand.empty:
            continue

        # Aggregate data by cumulative quantity and calculate the average price for each cumulative quantity
        offer_aggregated = offer.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()
        demand_aggregated = demand.groupby('Precio Compra/Venta')['Energía Compra/Venta'].sum().reset_index()

        # Sort data so that the offer is ascending and the demand is descending
        offer_aggregated = offer_aggregated.sort_values(by='Precio Compra/Venta')
        demand_aggregated = demand_aggregated.sort_values(by='Precio Compra/Venta', ascending=False)

        # Calculate the cumulative quantity for the offer and demand
        offer_aggregated['Cumulative Quantity'] = offer_aggregated['Energía Compra/Venta'].cumsum()
        demand_aggregated['Cumulative Quantity'] = demand_aggregated['Energía Compra/Venta'].cumsum()

        # Create interpolation functions
        offer_interpol = interpolate.interp1d(offer_aggregated['Cumulative Quantity'], offer_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")
        demand_interpol = interpolate.interp1d(demand_aggregated['Cumulative Quantity'], demand_aggregated['Precio Compra/Venta'], bounds_error=False, fill_value="extrapolate")

        # Find the quantity where prices are equal (approximation)
        quantities = np.linspace(max(offer_aggregated['Cumulative Quantity'].min(), demand_aggregated['Cumulative Quantity'].min()), 
                                min(offer_aggregated['Cumulative Quantity'].max(), demand_aggregated['Cumulative Quantity'].max()), 500)
        intersection_qty = quantities[np.abs(offer_interpol(quantities) - demand_interpol(quantities)).argmin()]
        intersection_price = offer_interpol(intersection_qty)
        
        # Store the equilibrium price for this hour
        equilibrium_prices.append((hour, intersection_price))

    # Convert the list of equilibrium prices to a DataFrame
    equilibrium_df = pd.DataFrame(equilibrium_prices, columns=['Hour', 'Equilibrium Price'])

    # Plot the equilibrium price over time
    plt.figure(figsize=(12, 8))
    plt.plot(equilibrium_df['Hour'], equilibrium_df['Equilibrium Price'], marker='o', linestyle='-')
    plt.title(f"Equilibrium Price Over Time for day {day}, market number {number}")
    plt.xlabel('Hour')
    plt.ylabel('Equilibrium Price (€)')
    plt.grid(True)

    plt.savefig("app/static/price.png")
