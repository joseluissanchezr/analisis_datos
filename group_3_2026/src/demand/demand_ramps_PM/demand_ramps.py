import pandas as pd
import matplotlib.pyplot as plt
import os

# loading the cleaned data for France, Germany, and Spain
france = pd.read_csv("group_3_2026/src/data/processed/france_cleaned.csv")
germany = pd.read_csv("group_3_2026/src/data/processed/germany_cleaned.csv")
spain = pd.read_csv("group_3_2026/src/data/processed/spain_cleaned.csv")


demand_data = pd.concat([france, germany, spain], ignore_index=True)
demand_data["datetime"] = pd.to_datetime(demand_data["datetime"], errors="coerce")
demand_data["demand_mwh"] = pd.to_numeric(demand_data["demand_mwh"], errors="coerce")
demand_data = demand_data.dropna(subset=["country", "datetime", "demand_mwh"])

demand_data = demand_data.sort_values(["country", "datetime"])
demand_data["ramp"] = demand_data.groupby("country")["demand_mwh"].diff()
demand_data["absolute_ramp"] = demand_data["ramp"].abs()

largest_ramps = demand_data.nlargest(10, "absolute_ramp")

demand_data.to_csv(
    "group_3_2026/src/demand/demand_ramps_PM/demand_ramps_results.csv",
    index=False,
)

largest_ramps.to_csv(
    "group_3_2026/src/demand/demand_ramps_PM/largest_demand_ramps.csv",
    index=False,
)

print("Demand ramp analysis completed")
print(largest_ramps)

top_3_per_country = (
    demand_data.groupby("country")
    .apply(lambda x: x.nlargest(3, "absolute_ramp"))
    .reset_index(drop=True)
)

# Sort the results for the CSV output (Country, then Ramp size)
final_results_csv = top_3_per_country.sort_values(
    ["country", "absolute_ramp"], ascending=[True, False]
)

print("\n--- ANALYSIS SUMMARY: Top 3 Ramps per Country ---")
print(final_results_csv[["country", "datetime", "demand_mwh", "ramp", "absolute_ramp"]])

# ==========================================
# 3. VISUALISATION: Chart of Top 3 Ramps per Country
# ==========================================
print("\nGenerating visualization...")

# Define the colors for each country
# Bright, distinguishable colors
country_colors = {
    'France': '#1f77b4', # A nice blue
    'Germany': '#f1c40f', # A bright yellow
    'Spain': '#e74c3c', # A solid red
}

# 1. Sort the data for proper visualization (largest ramps overall at the bottom, building up)
plot_data = top_3_per_country.sort_values("absolute_ramp", ascending=True)

# 2. Create labels (Country + Formatted Time)
labels = (
    plot_data["country"]
    + " ("
    + plot_data["datetime"].dt.strftime("%Y-%m-%d %H:%M")
    + ")"
)

# 3. Generate a list of colors, one for each bar based on the country
bar_colors = [country_colors[country] for country in plot_data['country']]

# Create the plot
plt.figure(figsize=(14, 8)) # Larger figure to hold all the data points comfortably

# Generate the horizontal bar chart with different colors for each country
bars = plt.barh(
    labels, plot_data["absolute_ramp"], color=bar_colors, edgecolor="black", alpha=0.8
)

# Add styling and labels
plt.title("Top 3 Largest Electrical Demand Ramps per Country", fontsize=16, fontweight="bold")
plt.xlabel("Absolute Demand Change (MWh)", fontsize=14)
plt.ylabel("Country and Time", fontsize=14)

# Add a grid on the x-axis to make it easier to read the values
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

# Show the plot
print("Plot generated and automatically captured by the dashboard script.")
plt.show()