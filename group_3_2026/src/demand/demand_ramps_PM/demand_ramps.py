import pandas as pd

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
